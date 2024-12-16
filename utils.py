import os
import colorsys

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# Install sund in a custom location
import subprocess
import sys

os.makedirs('./custom_package', exist_ok=True)
if "sund" not in os.listdir('./custom_package'):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--target=./custom_package", 'https://www.isbgroup.eu/sund-toolbox/releases/sund-1.2.22.tar.gz'])

sys.path.append('./custom_package')
import sund


def set_default_session_state(session_state):
    if 'sex' not in session_state:
        session_state['sex'] = 'Man'
    if 'weight' not in session_state:
        session_state['weight'] = 70.0
    if 'height' not in session_state:
        session_state['height'] = 1.72
    if 'age' not in session_state:
        session_state['age'] = 30.0
    if 'avatar_color' not in session_state:
        session_state['avatar_color'] = '#A757D6'  # Default color

def flatten(list):
    return [item for sublist in list for item in sublist]


def setup_model(model_name="alcohol_model_28"):
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
    t_end = max(stim["EtOH_conc"]["t"]+stim["kcal_solid"]["t"])+extra_time
    sim.Simulate(timevector = np.linspace(t_start, t_end, 10000))
    
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

drink_defaults = {
"Beer" : {"concentration": 5.0, "volume": 0.33, "kcal": 45.0, "length": 20.0},
"Wine" : {"concentration": 11.0, "volume": 0.15, "kcal": 20.0, "length": 20.0},
"Spirits" : {"concentration": 40.0, "volume": 0.04, "kcal": 0.0, "length": 1.0/60}
}

def setup_drinks(drink_times, n_drinks, concentration, volume, kcal, length):

    drink_lengths = [0]+[length*on for _ in range(n_drinks) for on in [1 , 0]]

    EtOH_conc = [0]+[concentration*on for _ in range(n_drinks) for on in [1 , 0]]
    vol_drink_per_time = [0]+[volume/length*on if length>0 else 0 for _ in range(n_drinks) for on in [1 , 0]]
    kcal_liquid_per_vol = [0]+[kcal/volume*on if volume>0 else 0 for _ in range(n_drinks) for on in [1 , 0]]
    t = [t+(length/60)*on for t in drink_times for on in [0,1]]

    # Setup stimulation to the model

    stim = {
        "EtOH_conc": {"t": t, "f": EtOH_conc},
        "vol_drink_per_time": {"t": t, "f": vol_drink_per_time},
        "kcal_liquid_per_vol": {"t": t, "f": kcal_liquid_per_vol},
        "drink_length": {"t": t, "f": drink_lengths},
        "kcal_solid": {"t": [0], "f": [0, 0]},
        }
    return stim


def drink_picker(consume_time=None):

    if consume_time is None:
        beer_time = drink_defaults["Beer"]["length"]
        wine_time = drink_defaults["Wine"]["length"]
    else:
        beer_time = consume_time
        wine_time = consume_time

    drink_type_selection = st.selectbox("Drink type", [f"Beer (5 % v/v, 33 cl, {beer_time} minutes consumption)", f"Wine (11 % v/v, 15 cl, {wine_time} minutes consumption)", "Spirits (40 % v/v, 4 cl, 1 second consumption)", "Custom"])

    drink_type = drink_type_selection.split(' ')[0]

    if drink_type in ["Beer", "Wine", "Spirits"]:
        drink_concentration = drink_defaults[drink_type]["concentration"]
        drink_volume = drink_defaults[drink_type]["volume"]
        drink_kcal = drink_defaults[drink_type]["kcal"]
        if drink_type == "Spirits" or consume_time is None:
            drink_length = drink_defaults[drink_type]["length"]
        else: 
            drink_length = consume_time
    elif drink_type == "Custom":
        drink_concentration = st.number_input("Concentration of drink (%): ", 0.0, 100.0, 5.0, 0.01)
        drink_volume = st.number_input("Volume of drink (L): ", 0.0, 24.0, 0.33, 0.1)
        drink_kcal = st.number_input("Kcal of the drink (kcal): ", 0.0, 1000.0, 45.0, 1.0)
        drink_length = st.number_input("Drink length (min): ", 0.0, 240.0, 20.0, 0.1)
    else:
        drink_concentration = 0
        drink_volume = 0
        drink_kcal = 0
        drink_length = 0

    return drink_type, drink_concentration, drink_volume, drink_kcal, drink_length


def drink_specifier():

    st.header("Specifying the alcoholic drinks")

    n_drinks = st.slider("Number of drinks:", 1, 15, 3)

    drink_spacing = st.slider("Time between the drinks (minutes):", 1, 120, 20,1)
    start_time = 0

    drink_type, drink_concentration, drink_volume, drink_kcal, drink_length = drink_picker()

    extra_time = st.number_input("Additional time to simulate after last drink (h):", 0.0, 100.0, 12.0, 0.1)

    drink_times = [start_time]+[n*(drink_length/60+drink_spacing/60) for n in range(1,n_drinks)]
    
    stim = setup_drinks(drink_times, n_drinks, drink_concentration, drink_volume, drink_kcal, drink_length)

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