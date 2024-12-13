import os
import json
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go

from utils import setup_model, drink_specifier, flatten, simulate, add_line, set_figure_layout, get_complementary_color, set_default_session_state
# st.elements.utils._shown_default_value_warning=True # This is not a good solution, but it hides the warning of using default values and sessionstate api

# Setup the models

model, model_features = setup_model()

# Start the app

st.title("Effects of meal consumption in combination with alcoholic drinks")
st.markdown("""Since alcohol is consumed as a drink, the rate of appearance of alcohol in the blood is partially controlled by the rate of gastric emptying. In turn, the gastric emptying is partially controlled by the food and liquids consumed. 
            
This exercise will show the differences in the time course of alcohol in the body depending on the consumption of a meal.
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

    meal_times.append(st.slider("Time of the meal, relative to first drink (h): ", -12.0, 12.0, start_time, 0.1, key=f"meal_time{i}"))
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
    st.subheader("Simulation of the differences in blood alcohol concentration when drinking on an empty stomach and after a meal")
    # feature = st.selectbox("Feature of the model to plot", model_features, model_features.index("Blood alcohol concentration (‰)"))
    feature = "Blood alcohol concentration (‰)"

    fig = go.Figure()
    add_line(fig, "Without meal", sim_results_no_meal, feature, st.session_state['avatar_color'])
    add_line(fig, "With meal", sim_results_meal, feature, get_complementary_color(st.session_state['avatar_color']))

    set_figure_layout(fig, feature)

    st.plotly_chart(fig)

    st.markdown(""" ## Questions to reflect over after simulating
- Was there a difference in the blood alcohol concentration when drinking on an empty stomach compared to after a meal?
- What happens if you consume the meal after having stopped drinking? 
- What happens if you consume the meal in the middle of the drinking session?
- What happens if you consume a larger meal?    
""")
