# Exercise to showcase different aspects of risks related to alcohol consumption


This repository contains the code for an application prototype to test if simulation based exercises can be used to inform individuals about risks related to alcohol consumption. The exercises are based on model simulations with the model from the publication titled \"A physiologically based digital twin for alcohol consumption – predicting real-life drinking responses and long-term plasma PEth\", [published in npj Digital Medicine](https://doi.org/10.1038/s41746-024-01089-6).

The prototype is hosted at [https://alcohol-pedagogics.streamlit.app](https://alcohol-pedagogics.streamlit.app), but can also be run locally. To do that, install the required packages listed in the `Pipfile` file:

```bash
pipenv install
```

Then run the application by running `streamlit run Home.py` in the terminal.

Please note that the application can take a few minutes to start up, primarily when running at [https://alcohol-pedagogics.streamlit.app](https://alcohol-pedagogics.streamlit.app), but also locally. Also note that a valid C-compiler is necessary for running the application locally.

The app was tested with Python 3.12.3, with the dependencies listed in the `Pipfile`.
