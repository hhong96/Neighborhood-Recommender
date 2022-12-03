
# Neighborhood Recommender System :house:

This app recommend the best neighborhood to live in based on user input related to quality of living factors. It is deployed using Streamlit.
[Click]((https://hhong96-neighborhood-recommender-app-6szh3p.streamlit.app) to access the app.



## Overview

  ![Example](/image/example.png)
 

### Dataset

- Property Listing data from multiple MLS Source via third-party scrape

- Census Data from United States Census Bureau including the American Community Survey Data

- Yelp business reviews from Yelp API

- Smart Location Mapping from United States Environment Protection Agency



### Developer Setup
  

- Install [python3](https://www.python.org/downloads/) if not already installed

- Create a virtual environment for working with Python

   ```python3 -m venv neighborhood-recommender```

- Activate your virtual environment

   ```cd neighborhood-recommender && source bin/activate```

- Within the activated virtual environment install dependencies

  ```pip3 install -r requirements.txt```

- Create `.streamlit` folder in the main directory

- Create `secret.toml` file within the folder and input your database connection string & api_key setting variable names as below

  ```
  engine = {your database instance connection string}
  api_key = {your google Geocoding API}
  ```

  *This project was developed with MySQL AWS RDS and Google Geocoding API using free tier account. AWS RDS provides up to 20GB storage for 1 year, and GCP provides $300 credit in free tier for new users. For more information on how to obtain license, see the link in 'API' below.*


- Run the app with `streamlit run app.py` in the `streamlit-example` directory



#### API


- [Google Cloud Platform - Geocoding API](https://developers.google.com/maps/documentation/geocoding/start)
- [AWS - Relational Database Service](https://aws.amazon.com/rds/free/)
