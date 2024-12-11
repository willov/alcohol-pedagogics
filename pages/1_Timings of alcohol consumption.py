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

from utils import setup_model, drink_specifier, flatten, simulate, add_line, set_figure_layout, get_complementary_color, set_default_session_state, drink_defaults, setup_drinks
# st.elements.utils._shown_default_value_warning=True # This is not a good solution, but it hides the warning of using default values and sessionstate api

# Setup the models

model, model_features = setup_model('alcohol_model')


# Start the app

st.title("Timings of alcohol consumption")
st.markdown("""Contrary to what many believe, the timeing of alcohol consumption can have a significant impact on the blood alcohol concentration. This exercise will show the differences in the time course of alcohol in the body depending on the timing of alcohol consumption.

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
# Specifying the drinks

stim = {}
for drink, settings in drink_defaults.items():

    concentration = settings["concentration"]
    volume = settings["volume"]
    kcal = settings["kcal"]
    if drink == "Spirits":
        length = 1/60
    else:
        length = 5/60

    drink_times = [0]

    stim[drink] = setup_drinks(drink_times, 1, concentration, volume, kcal, length)

# Simulate with and without the meal
extra_time = 4

sim_results_beer = simulate(model, anthropometrics, stim["Beer"], extra_time=extra_time)
sim_results_wine = simulate(model, anthropometrics, stim["Wine"], extra_time=extra_time)
sim_results_spirit = simulate(model, anthropometrics, stim["Spirits"], extra_time=extra_time)


st.markdown("""## Part 1: Timings of consuming different types of drinks
In this part, we will simulate the blood alcohol concentration when consuming one drink of different types (beer, wine, spirit) on an empty stomach using your defined avatar. In more detail, we will simulate the following drinks: 
- Beer: 33 cL with 5.0 %v/v alcohol and 45 kcal, consumed over 5 minutes
- Wine: 15 cL with 11 %v/v alcohol and 85 kcal, consumed over 5 minutes
- Spirit: 4 cL with 40 %v/v alcohol and 70 kcal, consumed over 1 second

            
### Questions to reflect over before simulating
- Do you think that there will be a difference in the time to peak blood concentration for the different drinks? 
- If so, what do you think will be the difference?
- How long time do you think it takes to reach peak blood concentration for the different drinks?
            
When you are ready, press the "Show simulation" button below to see the results.
""")


page_button_key = 'show_simulation_1'

# Initialize session state for show_simulation if not already set
if page_button_key not in st.session_state:
    st.session_state[page_button_key] = False

# Button to toggle show_simulation state
if st.button("Show simulation"):
    st.session_state[page_button_key] = True


def find_and_plot_t_max(fig, sim_results, feature, ymax, color):
     t_max = sim_results["Time"][np.argmax(sim_results[feature])]
     fig.add_trace(go.Scatter(x=[t_max, t_max], y=[0, ymax], showlegend=False, mode='lines', marker={"line": {"width":0}, "color":color}))
     return t_max

# Plotting the drinks
if st.session_state[page_button_key]:
    st.divider()
    st.subheader("Visualizing the differences in blood alcohol concentration when drinking different types of drinks")
    feature = st.selectbox("Feature of the model to plot", model_features, model_features.index("Blood alcohol concentration (‰)"))
    # st.line_chart(sim_results, x="Time", y=feature)

    fig = go.Figure()
    add_line(fig, "Beer", sim_results_beer, feature, "#e8b430")
    add_line(fig, "Wine", sim_results_wine, feature, "#7f0c0c")
    add_line(fig, "Spirit", sim_results_spirit, feature, "#d0d2d2")

    # Get the maximum value of the feature for all drinks:
    ymax = max([sim_results_beer[feature].max(), sim_results_wine[feature].max(), sim_results_spirit[feature].max()])+0.01
    tmax_beer = find_and_plot_t_max(fig, sim_results_beer, feature, ymax, "#e8b430")
    tmax_wine = find_and_plot_t_max(fig, sim_results_wine, feature, ymax, "#7f0c0c")
    tmax_spirit = find_and_plot_t_max(fig, sim_results_spirit, feature, ymax, "#d0d2d2")

    set_figure_layout(fig, feature, xaxis_title="Time since start of consumption (hours)")

    st.plotly_chart(fig)

    st.markdown(f""" Times for peak blood alcohol concentration:
    - Beer: {tmax_beer*60:.2f} minutes
    - Wine: {tmax_wine*60:.2f} minutes
    - Spirit: {tmax_spirit*60:.2f} minutes
    """)

    st.markdown(""" ## Questions to reflect over after simulating
- Was there a difference in the time to peak blood alcohol concentration for the different drinks?
- Was the time until peak concentration what you expected?
""")

st.divider()
st.markdown("""## Part 2: 
            
### Questions to reflect over before simulating
            
When you are ready, press the "Show simulation" button below to see the results.
""")
