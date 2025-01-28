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

from utils import setup_model, drink_specifier, flatten, simulate, add_line, set_figure_layout, get_complementary_color, set_default_session_state, drink_defaults, setup_drinks, drink_picker
# st.elements.utils._shown_default_value_warning=True # This is not a good solution, but it hides the warning of using default values and sessionstate api

# Setup the models

model, model_features = setup_model()


# Start the app

st.title("Timings of alcohol consumption")
st.markdown("""Contrary to what many believe, the timing of alcohol consumption can have a significant impact on the blood alcohol concentration. This exercise will show the differences in the time course of alcohol in the body depending on the timing of alcohol consumption.

This exercise will be divided into two parts: the first part will show the different timings of consuming different types of drinks (beer, wine, spirit), and the second will showcase differences when consuming multiple drinks. 
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

## Part 2
st.markdown("""## Part 2: Timing of consuming multiple consequent drinks
In this part, we will simulate the blood alcohol concentration when consuming five consequtive drinks of the same type (beer, wine, or spirit) with 15 minutes in between drinks on an empty stomach using your defined avatar. For the final drink, we will vary the start time between the final two drinks and showcase the difference in the peak blood alcohol concentration. By default, the time between the last drinks is set to either 5 minutes or 30 minutes.

""")

n_drinks = 4

drink_type, drink_concentration, drink_volume, drink_kcal, drink_length = drink_picker()

extra_time = st.number_input("1) Additional time to simulate after last drink (h):", 0.0, 100.0, 12.0, 0.1)

start_time = 0
drink_spacing_v1 = st.slider("1) Time between the last drinks (minutes):", 1, 120, 5,1)
drink_spacing_v2 = st.slider("2) Time between the last drinks (minutes):", 1, 120, 30,1)
drink_times = [start_time]+[n*(20/60+15/60) for n in range(1,n_drinks)]

drink_times_v1 = drink_times + [drink_times[-1]+drink_length/60+drink_spacing_v1/60]
drink_times_v2 = drink_times + [drink_times[-1]+drink_length/60+drink_spacing_v2/60]

stim_v0 = setup_drinks(drink_times, n_drinks, drink_concentration, drink_volume, drink_kcal, drink_length)
stim_v1 = setup_drinks(drink_times_v1, n_drinks+1, drink_concentration, drink_volume, drink_kcal, drink_length)
stim_v2 = setup_drinks(drink_times_v2, n_drinks+1, drink_concentration, drink_volume, drink_kcal, drink_length)

st.markdown("""### Questions to reflect over before simulating
- What do you think will be the difference in the peak blood alcohol concentration when the last drink is consumed 5 minutes after the previous drink compared to 30 minutes after the previous drink?
            
When you are ready, press the "Show simulation" button below to see the results.
""")

sim_results_v0 = simulate(model, anthropometrics, stim_v0, extra_time=extra_time)
sim_results_v1 = simulate(model, anthropometrics, stim_v1, extra_time=extra_time)
sim_results_v2 = simulate(model, anthropometrics, stim_v2, extra_time=extra_time)

page_button_key_2 = 'show_simulation_1_2'

# Initialize session state for show_simulation if not already set
if page_button_key_2 not in st.session_state:
    st.session_state[page_button_key_2] = False

# Button to toggle show_simulation state
if st.button("Show simulation", key="show_button_2"):
    st.session_state[page_button_key_2] = True

if st.session_state[page_button_key_2]:
    st.divider()
    st.subheader("Simulation of the differences in alcohol dynamics")
    # feature = st.selectbox("Feature of the model to plot", model_features, model_features.index("Blood alcohol concentration (‰)"))
    feature = "Blood alcohol concentration (‰)"

    fig = go.Figure()
    add_line(fig, "No additional drink", sim_results_v0, feature, "#d0d2d2")
    add_line(fig, f"Delayed with {drink_spacing_v1} min", sim_results_v1, feature, st.session_state['avatar_color'], showlegend=True)
    add_line(fig, f"Delayed with {drink_spacing_v2} min", sim_results_v2, feature, get_complementary_color(st.session_state['avatar_color']))

    set_figure_layout(fig, feature)

    st.plotly_chart(fig)

    st.markdown(""" ### Questions to reflect over after simulating
- Was the difference in peak blood alcohol concentration what you expected?
- How much do you need to delay the last drink to not give a higher peak blood alcohol concentration relative to the next-to-last drink?
""")
