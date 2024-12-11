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

from utils import drink_specifier, flatten, simulate, add_line, set_figure_layout, get_complementary_color, set_default_session_state
# st.elements.utils._shown_default_value_warning=True # This is not a good solution, but it hides the warning of using default values and sessionstate api

# Setup the models

def setup_model(model_name):
    sund.installModel(f"./models/{model_name}.txt")
    model_class = sund.importModel(model_name)
    model = model_class() 

    features = model.featurenames
    return model, features

model, model_features = setup_model('alcohol_model')


# Start the app

st.title("Differences as an effect of body size")
st.markdown("""In social situations, such as in dinners, it is common that the same amount of alcohol is given to all participants. However, the effect of alcohol on the body is different depending on the body size of the individual. This exercise will show the differences in the time course of alcohol in the body depending on the body size of the individual.
            
You will be able to specify the body size of the individual and the amount of alcohol consumed. The time course of alcohol in the body will be plotted.
""")
   
# Anthropometrics            
    
# Shared variables between the pages
set_default_session_state(st.session_state)

anthropometrics = {"sex": st.session_state['sex'], 
                   "weight": st.session_state['weight'], 
                   "height": st.session_state['height'], 
                   "age": st.session_state['age']}
anthropometrics["sex"] = float(anthropometrics["sex"].lower() in ["male", "man", "men", "boy", "1", "chap", "guy"]) #Converts to a numerical representation

st.divider()
# Specifying the drinks
stim, extra_time = drink_specifier()

# Setup meals
st.header("Specifying the meals")

start_time = 0.0

meal_times = []
meal_kcals = []

n_meals = st.slider("Number of (solid) meals:", 1, 15, 1)

for i in range(n_meals):
    st.markdown(f"**Meal {i+1}**")

    meal_times.append(st.number_input("Time of the meal, relative to first drink (h): ", -12.0, 100.0, start_time, 0.1, key=f"meal_time{i}"))
    meal_kcals.append(st.number_input("Kcal of the meal (kcal): ", 0.0, 10000.0, 500.0, 1.0, key=f"meal_kcals{i}"))
    start_time += 6

st.divider()

meal_times = [t+(30/60)*on for t in meal_times for on in [0,1]]
meal_kcals = [0]+[m*on for m in meal_kcals for on in [1 , 0]]

# Simulate with and without the meal

sim_results_no_meal = simulate(model, anthropometrics, stim, extra_time=extra_time)
stim["kcal_solid"] =  {"t": meal_times, "f": meal_kcals}
sim_results_meal = simulate(model, anthropometrics, stim, extra_time=extra_time)


st.markdown("""## Questions to reflect over before simulating
- Do you think there will be a difference between drinking on an empty stomach or after having eating?
- If so, what do you think will be the difference?
            
When you are ready, press the "Show simulation" button below to see the results.
""")


page_button_key = 'show_simulation_3'

# Initialize session state for show_simulation if not already set
if page_button_key not in st.session_state:
    st.session_state[page_button_key] = False

# Button to toggle show_simulation state
if st.button("Show simulation"):
    st.session_state[page_button_key] = True


# Plotting the drinks
if st.session_state[page_button_key]:
    st.divider()
    st.subheader("Visualizing the differences in blood alcohol concentration when drinking on an empty stomach and after a meal")
    feature = st.selectbox("Feature of the model to plot", model_features, model_features.index("Blood alcohol concentration (‰)"))
    # st.line_chart(sim_results, x="Time", y=feature)

    fig = go.Figure()
    add_line(fig, "Without meal", sim_results_no_meal, feature, st.session_state['avatar_color'])
    add_line(fig, "With meal", sim_results_meal, feature, get_complementary_color(st.session_state['avatar_color']))

    set_figure_layout(fig, feature)

    st.plotly_chart(fig)

    st.markdown(""" ## Questions to reflect over after simulating
- Was there a difference in the blood alcohol concentration when drinking on an empty stomach compared to after a meal?
- What happens if you consume the meal after having stopped drinking? 
- What happens if you consume the meal in the middle of the drinking session?        
""")
