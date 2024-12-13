import os
import json
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go

from utils import drink_specifier, flatten, simulate, setup_model, add_line, set_figure_layout, set_default_session_state

# st.elements.utils._shown_default_value_warning=True # This is not a good solution, but it hides the warning of using default values and sessionstate api

# Setup the models

model, model_features = setup_model()

# Start the app

st.title("Personal differences (as an effect of body size)")
st.markdown("""In social situations, such as in dinners, it is common that the same amount of alcohol is given to all participants. However, the effect of alcohol on is highly personal for each individual. This exercise will show the differences in the time course of alcohol in the body depending on the body size of the individual.
            
You will be able to specify the body size of the individual and the amount of alcohol consumed. The time course of alcohol in the body will be plotted.
""")
       
# Shared variables between the pages

set_default_session_state(st.session_state)

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

st.divider()
# Specifying the drinks


stim, extra_time = drink_specifier()

st.divider()
# Questions to reflect over

st.markdown("""## Questions to reflect over before simulating
- What do you think will happen if the same amount of alcohol is consumed by the three avatars?
- Do you think the alcohol dynamics will differ between the three avatars? If so, by how much?
            
When you are ready, press the "Show simulation" button below to see the results.
""")


# Simulate the three avatars
sim_results = simulate(model, anthropometrics, stim, extra_time=extra_time)
sim_results_large_man = simulate(model, avatar_large_male, stim, extra_time=extra_time)
sim_results_small_woman = simulate(model, avatar_small_female, stim, extra_time=extra_time)

page_button_key = 'show_simulation_1'

# Initialize session state for show_simulation if not already set
if page_button_key not in st.session_state:
    st.session_state[page_button_key] = False

# Button to toggle show_simulation state
if st.button("Show simulation"):
    st.session_state[page_button_key] = True

if st.session_state[page_button_key]:
    st.divider()
    st.subheader("Simulation of the differences in alcohol dynamics")
    # feature = st.selectbox("Feature of the model to plot", model_features, model_features.index("Blood alcohol concentration (‰)"))
    feature = "Blood alcohol concentration (‰)"

    fig = go.Figure()
    add_line(fig, "Your avatar", sim_results, feature, st.session_state['avatar_color'], showlegend=True)
    add_line(fig, "Large man", sim_results_large_man, feature, avatar_large_male['avatar_color'])
    add_line(fig, "Small woman", sim_results_small_woman, feature, avatar_small_female['avatar_color'])

    set_figure_layout(fig, feature)

    st.plotly_chart(fig)

    st.markdown(""" ## Questions to reflect over after simulating
- What happened when the three avatars consumed the same amount of alcohol? Did they get the same blood alcohol concentration?
- Did you expect this result? Why or why not?         
""")
