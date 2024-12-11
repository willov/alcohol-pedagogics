import os
import colorsys

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# Install sund in a custom location
import subprocess
import sys
if "sund" not in os.listdir('./custom_package'):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--target=./custom_package", 'https://www.isbgroup.eu/sund-toolbox/releases/sund-1.2.22.tar.gz'])

sys.path.append('./custom_package')
import sund


def flatten(list):
    return [item for sublist in list for item in sublist]


def setup_model(model_name):
    sund.installModel(f"./models/{model_name}.txt")
    model_class = sund.importModel(model_name)
    model = model_class() 

    features = model.featurenames
    return model, features


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


def get_complementary_color(hex_color):
    # Convert hex color to RGB
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    # Convert RGB to HSV
    h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)

    # Get the complementary color by shifting the hue by 180 degrees (0.5 in the HSV space)
    h_complementary = (h + 0.5) % 1.0

    # Convert HSV back to RGB
    r_complementary, g_complementary, b_complementary = colorsys.hsv_to_rgb(h_complementary, s, v)
    r_complementary = int(r_complementary * 255)
    g_complementary = int(g_complementary * 255)
    b_complementary = int(b_complementary * 255)

    # Convert RGB back to hex
    return f'#{r_complementary:02x}{g_complementary:02x}{b_complementary:02x}'


def drink_specifier():

    st.header("Specifying the alcoholic drinks")

    n_drinks = st.slider("Number of drinks:", 1, 15, 3)

    drink_spacing = st.slider("Time between the drinks (minutes):", 1, 120, 45,1)
    start_time = 0
    drink_times = [start_time]+[n*drink_spacing/60 for n in range(1,n_drinks)]

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


    EtOH_conc = [0]+[c*on for c in drink_concentrations for on in [1 , 0]]
    vol_drink_per_time = [0]+[v/t*on if t>0 else 0 for v,t in zip(drink_volumes, drink_lengths) for on in [1 , 0]]
    kcal_liquid_per_vol = [0]+[k/v*on if v>0 else 0 for v,k in zip(drink_volumes, drink_kcals) for on in [1 , 0]]
    drink_length = [0]+[t*on for t in drink_lengths for on in [1 , 0]]
    t = [t+(l/60)*on for t,l in zip(drink_times, drink_lengths) for on in [0,1]]

    print(t)

    # Setup stimulation to the model

    stim = {
        "EtOH_conc": {"t": t, "f": EtOH_conc},
        "vol_drink_per_time": {"t": t, "f": vol_drink_per_time},
        "kcal_liquid_per_vol": {"t": t, "f": kcal_liquid_per_vol},
        "drink_length": {"t": t, "f": drink_length},
        "kcal_solid": {"t": [0], "f": [0, 0]},
        }
    return stim, extra_time


def add_line(fig, label, sim_results, feature, color, showlegend=True):
    fig.add_trace(go.Scatter(name=label, x=sim_results["Time"], y=sim_results[feature], showlegend=showlegend, mode='lines', marker={"line": {"width":0}, "color":color}))


def set_figure_layout(fig, yaxis_title, xaxis_title="Time (hours since first drink)"):
    fig.update_layout(
        width=800,  # Adjust the width as needed
        height=600,  # Adjust the height as needed
        legend=dict(
            x=1,  # Position the legend inside the plot area
            y=1,
            xanchor='right',  # Anchor the legend to the right
            yanchor='top',
        ),
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title
    )