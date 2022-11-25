import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
import googlemaps
# import pydeck as pdk
import util.key as key


st.set_page_config(page_title="Neighborhood Recommender", page_icon=":house:", layout="wide", initial_sidebar_state="expanded")

# Connection
@st.cache(show_spinner=False)
def get_cbsa():
      engine = create_engine(key.engine, echo=False)
      query = "select distinct cbsa, cbsatitle from listings_enriched_final order by cbsa"
      df = pd.read_sql(query, engine)
      return df

@st.cache(show_spinner=False, allow_output_mutation=True)
def cbsa_input(user_cbsa):
  engine = create_engine(key.engine, echo=False)
  
  family_type = pd.read_sql(f"select distinct family_type_dummy, case when family_type_dummy = 1 then 'Yes' else 'No' end as family_type_final from listings_enriched_final where cbsa = {user_cbsa} order by family_type_dummy desc", engine)
  yearbuilt = pd.read_sql(f"select * from call_yearbuilt where cbsa = {user_cbsa} order by yearbuilt_buckets_dummy desc", engine)
  bd = pd.read_sql(f"select distinct bedroom_bucket_dummy, cast(round(bedrooms_final) as char) as bedrooms_final from listings_enriched_final where cbsa = {user_cbsa} order by bedroom_bucket_dummy", engine)
  sqft = pd.read_sql(f"select * from call_sqft where cbsa = {user_cbsa}", engine)
  hometype = pd.read_sql(f"select * from call_hometype where cbsa = {user_cbsa}", engine)
  income = pd.read_sql(f"select * from call_income where cbsa = {user_cbsa}", engine)
  price = pd.read_sql(f"select * from call_price where cbsa = {user_cbsa}", engine)
  age = pd.read_sql(f"select * from call_age where cbsa = {user_cbsa}", engine)
  edu = pd.read_sql(f"select * from call_edu where cbsa = {user_cbsa}", engine)
  bt = pd.read_sql(f"select distinct bathrooms_bucket_dummy, cast(round(bathrooms_final) as char) as bathrooms_final from listings_enriched_final where cbsa = {user_cbsa} order by bathrooms_bucket_dummy", engine)
  
  return family_type, yearbuilt, bd, sqft, hometype, income, price, age, edu, bt


@st.cache(allow_output_mutation=True)
def get_zip(home_type_input, income_input, bedroom_input, age_input, price_input, sqft_input, year_input, fam_input, edu_input, bathroom_input):
  engine = create_engine(key.engine, echo=False)
  query = """
          select 
            *
          from output_pred output
          where 
          hometype_dummy = '{hometype}'
          and majority_income_dummy = '{income}'
          and bedroom_bucket_dummy = '{bd}'
          and median_age_dummy = '{age}'
          and price_dummy = '{price}'
          and sqft_buckets_dummy = '{sqft}'
          and yearbuilt_buckets_dummy = '{yearbuilt}'
          and family_type_dummy = '{familytype}'
          and overall_education_score_dummy = '{edu}'
          and bathrooms_bucket_dummy = '{bt}'
          """.format(hometype = home_type_input, income = income_input, bd = bedroom_input, age = age_input, price = price_input, sqft = sqft_input, yearbuilt = year_input, familytype = fam_input, edu = edu_input, bt = bathroom_input) 
  zip = pd.read_sql(query, engine)
  return zip


@st.cache(show_spinner=False, allow_output_mutation=True)
def get_listing(zipcode):
  engine = create_engine(key.engine, echo=False)
  query = "select * from listing where zipcode = {} limit 10".format(zipcode)
  listing = pd.read_sql(query, engine)
  return listing


@st.cache(show_spinner=False, allow_output_mutation=True)
def get_county(zipcode):
  engine = create_engine(key.engine, echo=False)
  query = "select concat(county, ', ', city) as county from zip_county where zipcode = {}".format(zipcode)
  county = pd.read_sql(query, engine)
  return county

cbsa = get_cbsa()


if 'cbsa' not in st.session_state:
  st.session_state['cbsa'] = 0
    
if 'other_input' not in st.session_state:
  st.session_state['other_input'] = 0
  
if 'zipcode' not in st.session_state:
  st.session_state['zipcode'] = 0


st.markdown("# :house_buildings: Neighborhood Recommender")
st.markdown("### CSE 6242 Project - Team 110")
st.markdown("> Select an area you want to live in to get started, and fill out your preference on housing and your demographic information - We will find **the best neighbrohood for you**! :dancer:")    
st.markdown("")

with st.sidebar.form("other_form"):
    
  cbsa_param = st.selectbox("Select Geographic Area", options=[''] + cbsa['cbsatitle'].tolist())
  submit = st.form_submit_button("Submit")
  
  if submit:
    user_cbsa = cbsa[cbsa['cbsatitle'] == cbsa_param]['cbsa'].values[0]
    user_cbsa = str(user_cbsa)
    family_type, yearbuilt, bd, sqft, hometype, income, price, age, edu, bt = cbsa_input(user_cbsa)
    st.session_state['other_input'] = {'family_type': family_type, 'yearbuilt': yearbuilt, 'bd': bd, 'sqft': sqft, 'hometype': hometype, 'income': income, 'price': price, 'age': age, 'edu': edu, 'bt': bt}
    st.session_state['cbsa'] = user_cbsa

  if st.session_state['cbsa'] != 0:
    home_type_param = st.selectbox("Preferred Home Type", options=[''] + st.session_state['other_input']['hometype']['hometype'].tolist()) 
    bedroom_param = st.selectbox("\# Bedrooms", options=[''] + st.session_state['other_input']['bd']['bedrooms_final'].tolist())
    bathroom_param = st.selectbox("\# Bathrooms", options=[''] + st.session_state['other_input']['bt']['bathrooms_final'].tolist())
    price_param = st.selectbox("Ideal Price Range", [''] + st.session_state['other_input']['price']['price_bucket'].tolist())
    square_feet_param = st.selectbox("Preferred Size", [''] + st.session_state['other_input']['sqft']['sqft_final'].tolist())
    year_built_param = st.selectbox("Preferred Age of Property", [''] + st.session_state['other_input']['yearbuilt']['year_built_final'].tolist())
    income_param = st.selectbox("Your Income", options=[''] + st.session_state['other_input']['income']['majority_income_final'].tolist())
    edu_param = st.selectbox("Your Highest Education", options=[''] + st.session_state['other_input']['edu']['majority_education_final'].tolist())
    age_param = st.selectbox("Your Age", [''] + st.session_state['other_input']['age']['age_bucket'].tolist())
    family_param = st.selectbox("Do you live with your family (Spouse and Kids)?", options=[''] + st.session_state['other_input']['family_type']['family_type_final'].tolist())  
    
    if st.form_submit_button("Predict"):
      if home_type_param == '' or bedroom_param == '' or bathroom_param == '' or price_param == '' or square_feet_param == '' or year_built_param == '' or income_param == '' or edu_param == '' or age_param == '' or family_param == '':
        st.error("Please fill out all the fields")
        
      elif home_type_param != '' and bedroom_param != '' and bathroom_param != '' and price_param != '' and square_feet_param != '' and year_built_param != '' and income_param != '' and edu_param != '' and age_param != '' and family_param != '':
        home_type_input = st.session_state['other_input']['hometype'][st.session_state['other_input']['hometype']['hometype'] == home_type_param]['hometype_dummy'].values[0]
        income_input = st.session_state['other_input']['income'][st.session_state['other_input']['income']['majority_income_final'] == income_param]['majority_income_dummy'].values[0]
        bedroom_input = st.session_state['other_input']['bd'][st.session_state['other_input']['bd']['bedrooms_final'] == bedroom_param]['bedroom_bucket_dummy'].values[0]
        bathroom_input = st.session_state['other_input']['bt'][st.session_state['other_input']['bt']['bathrooms_final'] == bathroom_param]['bathrooms_bucket_dummy'].values[0]
        age_input = st.session_state['other_input']['age'][st.session_state['other_input']['age']['age_bucket'] == age_param]['median_age_dummy'].values[0]
        price_input = st.session_state['other_input']['price'][st.session_state['other_input']['price']['price_bucket'] == price_param]['price_dummy'].values[0]
        sqft_input = st.session_state['other_input']['sqft'][st.session_state['other_input']['sqft']['sqft_final'] == square_feet_param]['sqft_buckets_dummy'].values[0]
        year_input  = st.session_state['other_input']['yearbuilt'][st.session_state['other_input']['yearbuilt']['year_built_final'] == year_built_param]['yearbuilt_buckets_dummy'].values[0]
        fam_input = st.session_state['other_input']['family_type'][st.session_state['other_input']['family_type']['family_type_final'] == family_param]['family_type_dummy'].values[0]
        edu_input = st.session_state['other_input']['edu'][st.session_state['other_input']['edu']['majority_education_final'] == edu_param]['majority_education_dummy'].values[0]

        zip = get_zip(home_type_input, income_input, bedroom_input, age_input, price_input, sqft_input, year_input, fam_input, bathroom_input, edu_input)
        
        if zip[st.session_state['cbsa']].shape[0] != 0:
          st.session_state['zipcode'] = zip[st.session_state['cbsa']].values[0]
          

if st.session_state['zipcode'] != 0:
    county = get_county(st.session_state['zipcode'])
    with st.container():
      st.markdown("## Your ideal neighborhood is " + str(county['county'].values[0]) + "! :tada:")
      st.markdown(f"*Zip Code : {str(st.session_state['zipcode'])}*")


tab1, tab2, tab3 = st.tabs(["listing", "yelp", "analysis"])   
     
with tab1: 
    ls = get_listing(st.session_state['zipcode'])
    ls['address'] = ls.apply(lambda x: '%s, %s, %s, %s' % (x['streetAddress'], x['city'], x['state'], x['zipcode']), axis=1)
    ls['lat'] = 0
    ls['lon'] = 0

    gmaps_key = googlemaps.Client(key=key.api_key)
    df = ls[["streetAddress", "city", "state", "zipcode", "homeType_CD", "SqFt", "bedrooms", "bathrooms", "yearBuilt"]]
    df.rename(columns={"streetAddress": "Street Address", "homeType_CD": "Home Type", "SqFt": "SqFt", "bedrooms": "# Bedroom", "bathrooms": "# Bathroom", "yearBuilt": "Year Built"}, inplace=True)
    
    # df_map = ls[["address", "lat", "lon"]]
    
    for i in range(len(ls)):
      # g = gmaps_key.geocode(df_map['address'][i])
      g = gmaps_key.geocode(ls['address'][i])
      
      if g[0]["geometry"]["location"]["lat"] != 0:
        # df_map['lat'][i] = g[0]["geometry"]["location"]["lat"]
        # df_map['lon'][i] = g[0]["geometry"]["location"]["lng"]
        ls['lat'][i] = g[0]["geometry"]["location"]["lat"]
        ls['lon'][i] = g[0]["geometry"]["location"]["lng"]
        

    with st.container():
      st.markdown("### Here are some available houses in your ideal neighborhood!")
      
      # st.pydeck_chart(pdk.Deck(
      #     map_style='mapbox://styles/mapbox/light-v9',
      #     layers=[
      #         pdk.Layer(
      #             'ScatterplotLayer',
      #             data=df_map,
      #             get_position='[lon, lat]',
      #             get_color='[200, 30, 0, 160]',
      #             get_radius=200,
      #             pickable=True,
      #         ),
      #     ],
      # )) 
      
      st.map(ls[['lat', 'lon']])
      st.table(df.style.format({"SqFt": "{:.0f}", "# Bedroom": "{:.0f}", "# Bathroom": "{:.0f}", "Year Built": "{:.0f}"}))
      
      
with tab2:
  pass

with tab3:
  pass

def main():
  pass
    
if __name__ == '__main__':
	main()
 