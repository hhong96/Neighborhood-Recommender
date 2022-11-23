
# Neighborhood Recommender System :house:

This app recommend the best neighborhood to live in based on user input related to quality of living factors. It is deployed using Streamlit.

## Overview

  ![Example](/image/example.png)
 

### Dataset

- Property Listing data from multiple MLS Source via third-party scrape

- Census Data from United States Census Bureau including the American Community Survey Data

- Yelp business reviews from Yelp API

- Smart Location Mapping from United States Environment Protection Agency

### Model

This model was trained to recommend a subset of You can find the details on training algorithm in ____.

  
  

## Setup

  

- Install [python3](https://www.python.org/downloads/) if not already installed

- Create a virtual environment for working with Python

- `python3 -m venv neighborhood-recommender`

- Activate your virtual environment

- `cd neighborhood-recommender && source bin/activate`

- Within the activated virtual environment install dependencies

- `pip3 install -r requirements.txt`

- Run the app with `streamlit run app.py` in the `streamlit-example` directory