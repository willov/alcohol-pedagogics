import os
import json
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go

# Install sund in a custom location
import subprocess
import sys
if "sund" not in os.listdir('./custom_package'):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--target=./custom_package", 'https://www.isbgroup.eu/sund-toolbox/releases/sund-1.2.22.tar.gz'])

sys.path.append('./custom_package')
import sund

# st.elements.utils._shown_default_value_warning=True # This is not a good solution, but it hides the warning of using default values and sessionstate api

# Setup the models

def setup_model(model_name):
    sund.installModel(f"./models/{model_name}.txt")
    model_class = sund.importModel(model_name)
    model = model_class() 

    features = model.featurenames
    return model, features

model, model_features = setup_model('alcohol_model')

# Define functions needed

def flatten(list):
    return [item for sublist in list for item in sublist]

def simulate(m, anthropometrics, stim, extra_time = 10):
    act = sund.Activity(timeunit = 'h')
    pwc = sund.PIECEWISE_CONSTANT # space saving only
    const = sund.CONSTANT # space saving only

    for key,val in stim.items():
        act.AddOutput(name = key, type=pwc, tvalues = val["t"], fvalues = val["f"]) 
    for key,val in anthropometrics.items():
        if key != "avatar_color":
            act.AddOutput(name = key, type=const, fvalues = val) 
    
    sim = sund.Simulation(models = m, activities = act, timeunit = 'h')
    
    sim.ResetStatesDerivatives()
    t_start = min(stim["EtOH_conc"]["t"]+stim["kcal_solid"]["t"])-0.25

    sim.Simulate(timevector = np.linspace(t_start, max(stim["EtOH_conc"]["t"])+extra_time, 10000))
    
    sim_results = pd.DataFrame(sim.featuredata,columns=sim.featurenames)
    sim_results.insert(0, 'Time', sim.timevector)

    t_start_drink = min(stim["EtOH_conc"]["t"])-0.25

    sim_drink_results = sim_results[(sim_results['Time']>=t_start_drink)]
    return sim_drink_results

# Start the app

st.title("Differences as an effect of body size")
st.markdown("""In social situations, such as in dinners, it is common that the same amount of alcohol is given to all participants. However, the effect of alcohol on the body is different depending on the body size of the individual. This exercise will show the differences in the time course of alcohol in the body depending on the body size of the individual.
            
You will be able to specify the body size of the individual and the amount of alcohol consumed. The time course of alcohol in the body will be plotted.
""")
   
# Anthropometrics            
    
# Shared variables between the pages
if 'sex' not in st.session_state:
    st.session_state['sex'] = 'Man'
if 'weight' not in st.session_state:
    st.session_state['weight'] = 70.0
if 'height' not in st.session_state:
    st.session_state['height'] = 1.72
if 'age' not in st.session_state:
    st.session_state['age'] = 30.0
if 'avatar_color' not in st.session_state:
    st.session_state['avatar_color'] = '#A757D6'  # Default color

anthropometrics = {"sex": st.session_state['sex'],
                   "weight": st.session_state['weight'], 
                   "height": st.session_state['height'], 
                   "age": st.session_state['age']}
anthropometrics["sex"] = float(anthropometrics["sex"].lower() in ["male", "man", "men", "boy", "1", "chap", "guy"]) #Converts to a numerical representation

## Setup the large male avatar

col1, col2 = st.columns(2)

with col1:
    avatar_large_male = {}
    avatar_large_male["sex"] = st.selectbox("Sex:", ["Man", "Woman"], 0, key="avatar_large_sex")
    avatar_large_male["sex"] = float(avatar_large_male["sex"].lower() in ["male", "man", "men", "boy", "1", "chap", "guy"]) #Converts to a numerical representation
    avatar_large_male["weight"] = st.number_input("Weight (kg):", 30.0, 200.0, 120.0, 0.1, key="avatar_large_weight")
    avatar_large_male["height"] = st.number_input("Height (m):", 1.0, 2.5, 1.95, key="avatar_large_height")
    avatar_large_male["age"] = st.number_input("Age (years):", 18.0, 120.0, 25.0, 1.0, key="avatar_large_age")
    avatar_large_male['avatar_color'] = st.color_picker("Avatar Color:", "#ff9932", key="avatar_large_color")

with col2:
    avatar_small_female = {}
    avatar_small_female["sex"] = st.selectbox("Sex:", ["Man", "Woman"], 1, key="avatar_small_sex")
    avatar_small_female["sex"] = float(avatar_small_female["sex"].lower() in ["male", "man", "men", "boy", "1", "chap", "guy"]) #Converts to a numerical representation
    avatar_small_female["weight"] = st.number_input("Weight (kg):", 30.0, 200.0, 50.0, 0.1, key="avatar_small_weight")
    avatar_small_female["height"] = st.number_input("Height (m):", 1.0, 2.5, 1.45, key="avatar_small_height")
    avatar_small_female["age"] = st.number_input("Age (years):", 18.0, 120.0, 25.0, 1.0, key="avatar_small_age")
    avatar_small_female['avatar_color'] = st.color_picker("Avatar Color:", "#b5d1cf", key="avatar_small_color")

# Specifying the drinks
st.divider()
st.subheader("Specifying the alcoholic drinks")

n_drinks = st.slider("Number of drinks:", 1, 15, 3)

drink_spacing = st.slider("Time between the drinks (minutes):", 1, 120, 45,1)
start_time = 0
drink_times = [start_time]+[n*drink_spacing/60 for n in range(n_drinks)]

drink_type = st.selectbox("Drink type", ["Beer (5 % v/v, 33 cl, 20 minutes consumption)", "Wine (12 % v/v, 15 cl, 20 minutes consumption)", "Spirits (40 % v/v, 4 cl, 1 minutes consumption)", "Custom"])

if drink_type.split(' ')[0] == "Beer":
    drink_concentrations = [5.0]*n_drinks
    drink_volumes = [0.33]*n_drinks
    drink_kcals = [45.0]*n_drinks
    drink_lengths = [20.0]*n_drinks
elif drink_type.split(' ')[0] == "Wine":
    drink_concentrations = [12.0]*n_drinks
    drink_volumes = [0.15]*n_drinks
    drink_kcals = [85.0]*n_drinks
    drink_lengths = [20.0]*n_drinks
elif drink_type.split(' ')[0] == "Spirits":
    drink_concentrations = [40.0]*n_drinks
    drink_volumes = [0.04]*n_drinks
    drink_kcals = [70.0]*n_drinks
    drink_lengths = [1.0]*n_drinks
elif drink_type == "Custom":
    drink_concentrations = [st.number_input("Concentration of drink (%): ", 0.0, 100.0, 5.0, 0.01)]*n_drinks
    drink_volumes = [st.number_input("Volume of drink (L): ", 0.0, 24.0, 0.33, 0.1)]*n_drinks
    drink_kcals = [st.number_input("Kcal of the drink (kcal): ", 0.0, 1000.0, 45.0, 1.0)]*n_drinks
    drink_lengths = [st.number_input("Drink length (min): ", 0.0, 240.0, 20.0, 0.1)]*n_drinks

extra_time = st.number_input("Additional time to simulate after last drink (h):", 0.0, 100.0, 12.0, 0.1)

st.divider()

EtOH_conc = [0]+[c*on for c in drink_concentrations for on in [1 , 0]]
vol_drink_per_time = [0]+[v/t*on if t>0 else 0 for v,t in zip(drink_volumes, drink_lengths) for on in [1 , 0]]
kcal_liquid_per_vol = [0]+[k/v*on if v>0 else 0 for v,k in zip(drink_volumes, drink_kcals) for on in [1 , 0]]
drink_length = [0]+[t*on for t in drink_lengths for on in [1 , 0]]
t = [t+(l/60)*on for t,l in zip(drink_times, drink_lengths) for on in [0,1]]

# Setup stimulation to the model

stim = {
    "EtOH_conc": {"t": t, "f": EtOH_conc},
    "vol_drink_per_time": {"t": t, "f": vol_drink_per_time},
    "kcal_liquid_per_vol": {"t": t, "f": kcal_liquid_per_vol},
    "drink_length": {"t": t, "f": drink_length},
    "kcal_solid": {"t": [0], "f": [0, 0]},
    }

# Questions to reflect over

st.subheader("Questions to reflect over before simulating")
st.markdown("""
- What do you think will happen if the same amount of alcohol is consumed by the three avatars?
- Do you think the alcohol dynamics will differ between the three avatars? If so, by how much?
            
When you are ready, press the "Show simulation" button below to see the results.
""")

show_simulation = st.button("Show simulation")

# Simulate the three avatars
sim_results = simulate(model, anthropometrics, stim, extra_time=extra_time)
sim_results_large_man = simulate(model, avatar_large_male, stim, extra_time=extra_time)
sim_results_small_woman = simulate(model, avatar_small_female, stim, extra_time=extra_time)

if show_simulation:
    st.divider()
    st.subheader("Visualizing the differences in alcohol dynamics")
    feature = st.selectbox("Feature of the model to plot", model_features)

    fig = go.Figure()
    fig.add_trace(go.Scatter(name="Your avatar", x=sim_results["Time"], y=sim_results[feature], showlegend=True, mode='lines', marker={"line": {"width":0}, "color":st.session_state['avatar_color']}))
    fig.add_trace(go.Scatter(name="Large man", x=sim_results_large_man["Time"], y=sim_results_large_man[feature], showlegend=True, mode='lines', marker={"line": {"width":0}, "color":avatar_large_male['avatar_color']}))
    fig.add_trace(go.Scatter(name="Small woman", x=sim_results_small_woman["Time"], y=sim_results_small_woman[feature], showlegend=True, mode='lines', marker={"line": {"width":0}, "color":avatar_small_female['avatar_color']}))

    fig.update_layout(
        width=800,  # Adjust the width as needed
        height=600,  # Adjust the height as needed
        legend=dict(
            x=1,  # Position the legend inside the plot area
            y=1,
            xanchor='right',  # Anchor the legend to the right
            yanchor='top',
        ),
        xaxis_title="Time (hours since first drink)",
        yaxis_title=feature
    )

    st.plotly_chart(fig)

    st.divider()
    st.subheader("Questions to reflect over after simulating")
    st.markdown("""
- What happened when the three avatars consumed the same amount of alcohol?
- Do you think the alcohol dynamics will differ between the three avatars? If so, by how much?
            
When you are ready, press the "Show simulation" button below to see the results.
""")
