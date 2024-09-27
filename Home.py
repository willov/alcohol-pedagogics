
import streamlit as st

# Install sund in a custom location
import subprocess
import sys
import os 

if "sund" not in os.listdir('./custom_package'):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--target=./custom_package", 'https://www.isbgroup.eu/sund-toolbox/releases/sund-1.2.22.tar.gz'])


st.title("Exercises to visualize different risk related to alcohol consumption")
st.markdown("""These exercises are ment to showcase different risks related to alcohol consumption. The intent is to bring awareness to the risks involved to improve the health of the population. 
            
You will find the exercises in the panels on the left side of the screen.
            
In the exercies you will have the option to use a digital avatar with customizable features. This avatar can be a representation of yourself or a fictional character. The avatar will be used to put the situations into a context. No information will be saved of the created avatar. You can set the avatar below. 
            
When you are ready, you can start the exercises by selecting them in the left panel. Enjoy!
""")

st.subheader("Set your avatar")

# Shared variables between the pages
if 'sex' not in st.session_state:
    st.session_state['sex'] = 'Man'
if 'weight' not in st.session_state:
    st.session_state['weight'] = 70.0
if 'height' not in st.session_state:
    st.session_state['height'] = 1.72
if 'age' not in st.session_state:
    st.session_state['age'] = 30.0
if 'color' not in st.session_state:
    st.session_state['avatar_color'] = '#A757D6'  # Default color


# st.session_state = {"sex": st.session_state['sex'], "weight": st.session_state['weight'], "height": st.session_state['height']}
st.session_state["sex"] = st.selectbox("Sex:", ["Man", "Woman"], [1, 0].index(st.session_state['sex']), key="sex")
st.session_state["weight"] = st.number_input("Weight (kg):", 30.0, 200.0, st.session_state['weight'], 0.1, key="weight")
st.session_state["height"] = st.number_input("Height (m):", 1.0, 2.5, st.session_state['height'], key="height")
st.session_state["age"] = st.number_input("Age (years):", 18.0, 120.0, st.session_state['age'], 1.0, key="age")
st.session_state['avatar_color'] = st.color_picker("Avatar Color:", st.session_state['avatar_color'])

