import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
import googlemaps
import util.key as key
import plotly.express as px
import plotly.graph_objects as go
import inflect

p = inflect.engine()

### main page layout
st.set_page_config(page_title="Neighborhood Recommender", page_icon=":house:", layout="wide", initial_sidebar_state="expanded")
st.markdown("# :house_buildings: Neighborhood Recommender")
st.markdown("### CSE 6242 Project - Team 110")
st.markdown("> Select an area you want to live in to get started, and fill out your preference on housing and your demographic information - We will find **the best neighbrohood for you**! :dancer:")    
st.markdown("")

engine = create_engine(key.engine, echo=False)
gmaps_key = googlemaps.Client(key=key.api_key)

### data read functions 
# get the list of cbsa (fixed - dataframe)
@st.experimental_memo
def get_cbsa():
  query = "select distinct cbsa, cbsatitle from listings_enriched_final order by cbsa"
  df = pd.read_sql(query, engine)
  return df

# get the dropdown options (fixed - dataframe)
@st.experimental_memo
def get_dd():
  query = "select type, dummy, bucket from mapping"
  df = pd.read_sql(query, engine)
  
  bd = df[df['type'] == 'Bedroom']
  cent = df[df['type'] == 'Centrality']
  edu = df[df['type'] == 'Education']
  fam = df[df['type'] == 'Family']
  home = df[df['type'] == 'HomeType']
  inc = df[df['type'] == 'Income']
  sch = df[df['type'] == 'School']
  sqft = df[df['type'] == 'Sqft']
  year = df[df['type'] == 'Yearbuilt']
  return bd, cent, edu, fam, home, inc, sch, sqft, year

# get the price, age dropdown options based on cbsa (dynamic - dataframe)
@st.experimental_memo
def get_dd_other(user_cbsa):
  price = pd.read_sql(f"select * from mapping_price where cbsa = {user_cbsa}", engine)
  age = pd.read_sql(f"select * from mapping_age where cbsa = {user_cbsa}", engine)
  return price, age

# get the zip recommendation based on the user inputs (dynamic - string)
@st.experimental_memo
def get_zip(cbsa_input, bedroom_input, cent_input, edu_input, fam_input, home_input, inc_input, sch_input, sqft_input, year_input, price_input, age_input):
  query = """
          select pred from predicted_output_{cbsa_input}
          where 
            majority_income_dummy = {inc_input} and
            majority_education_dummy = {edu_input} and
            hometype_dummy = {home_input} and
            family_type_dummy= {fam_input} and
            bedroom_bucket_dummy = {bedroom_input} and
            sqft_buckets_dummy = {sqft_input} and
            yearbuilt_buckets_dummy = {year_input} and
            overall_education_score_dummy = {sch_input} and
            centrality_index_dummy = {cent_input} and
            price_dummy = {price_input} and
            median_age_dummy = {age_input}
          """.format(cbsa_input=cbsa_input, inc_input=inc_input, edu_input=edu_input, home_input=home_input, fam_input=fam_input, bedroom_input=bedroom_input, sqft_input=sqft_input, year_input=year_input, sch_input = sch_input, cent_input=cent_input, price_input=price_input, age_input=age_input)
          
  zip = str(pd.read_sql(query, engine).iloc[0,0])
  return zip

# get the list of listing based on recommended zip (fixed - dataframe; 10 rows)
@st.experimental_memo
def get_listing(zipcode):
  query = "select streetAddress, city, state, zipcode, hometype_cd, sqft, bedrooms, bathrooms, yearbuilt from listing where zipcode = {} limit 10".format(zipcode)
  listing = pd.read_sql(query, engine)
  return listing

# get the list of food / fun business based on recommended zip (fixed - dataframe; 10 rows)
@st.experimental_memo
def get_yelp_data(zipcode):
  query1 = "select * from yelp_zc where zipcode = {} and term = 'food' order by rating desc, review_count desc limit 10".format(zipcode)
  query2 = "select * from yelp_zc where zipcode = {} and term = 'fun' order by rating desc, review_count desc limit 10".format(zipcode)
  food = pd.read_sql(query1, engine)
  fun = pd.read_sql(query2, engine)
  return food, fun

# analysis 1 function
@st.experimental_memo
def analysis_rank(zipcode, cbsa):
    # read table
    df = pd.read_sql('select * from census_final where cbsa={}'.format(cbsa), con=engine).astype({'zipcode': 'str', 'cbsa': 'str', 'years': 'str'})
    # to be analyzed columns
    column = ['unemployment_rate_final', 'gender_diversity_index_final', 'mean_travel_time_to_work_minutes_final', 'mean_household_income_dollars_final', 'percent_population_work_from_home_final', 'percent_family_households_final', 'median_age_final']
    # column name change
    rename = ['Unemployment Rate', 'Gender Diversity', 'Commute Time', 'Household Income', 'WFH Rate', 'Family-Friendliness', 'Median Age']
    
    # get the number of zipcodes in the cbsa
    all = len(df['zipcode'].unique().tolist())
    
    # assign color to user zip
    colors = {}
    color_discrete_map = {
        c: colors.get(c, "#C0C0C0") 
        for c in df['zipcode'].unique()}
    color_discrete_map[str(zipcode)] = "Red"
    
    # iterate through each column for analysis
    
    chart = []
    for i in range(len(column)):
        # sliced dataframe by column
        df_analysis = df[['zipcode', 'years', column[i]]].rename({'zipcode': 'Zip Code', 'years':'Years', column[i]: rename[i]}, axis=1)
        
        # min max for y range
        min = df_analysis[rename[i]].min()
        max = df_analysis[rename[i]].max()
        
        # dynamic title for each year
        title = []
        for j in range(len(df_analysis['Years'].unique())):
            rank_df = df_analysis.copy()
            rank_df = rank_df[rank_df['Years'] == rank_df['Years'].unique()[j]]
            rank_df['rank'] = rank_df[rename[i]].rank(ascending=False)
            
            rank = int(rank_df[rank_df['Zip Code'] == str(zipcode)]['rank'].values[0])
            title.append(f'{rename[i]} Ranking: your neighborhood {zipcode} is {p.ordinal(rank)} place out of {all} neighborhoods in Metropolitan Statistical Area {cbsa} in ' + df_analysis['Years'].unique()[j]
            )
        
        # bar chart animated by each year    
        fig = px.bar(df_analysis, y=rename[i], x='Zip Code', animation_frame='Years', color='Zip Code'
                    , color_discrete_map=color_discrete_map, text_auto=True)
        
        # sort descending, format y axis and range
        fig.update_layout(
            title = title[0],
            xaxis = {'categoryorder':'total descending'},
            yaxis_tickformat = '.3f',
            yaxis_range = [min*0.99999, max*1.001]
        )
        

        # append title for each year
        for k in range(len(fig.frames)):
            fig.frames[k]['layout'].update(title_text=title[k])
        
        chart.append(fig)
        
    return chart

# analysis 2
@st.experimental_memo
def analysis_2(zipcode):
  query = """
    select
        cf.zipcode,
        round(cf.percent_female_final,2) as pct_f,
        round(cf.percent_male_final,2) as pct_m,
        round(cf.percent_family_households_final,2) as pct_fam,
        round(cf.percent_family_households_final,2) as pct_non_fam,
        cf.majority_age_group_final as val_age,
        cf.majority_industry_final as val_ind,
        round(cf.unemployment_rate_final,2) as pct_unemp,
        round(cf.mean_travel_time_to_work_minutes_final,2) as ind_com,
        round(ae.nat_walk_ind,2) as ind_walk,
        round(ae.traffic_dens_ind,2) as ind_trf,
        yp.average_score as ind_yelp,
        yp.term_ratio as pct_yelp,
        round(avg(zlld.bedrooms_final),2) as avg_bd,
        round(avg(zlld.bathrooms_final),2) as avg_bt,
        round(avg(zlld.year_built_final),2) as avg_y,
        round(avg(zlld.SqFt_final),2) as avg_spft,
        round(avg(zlld.price),2) as avg_price,
        round(cf.mean_household_income_dollars_final) as avg_inc,
        round(avg(lef.elemntary_rating_final), 2) as el,
        round(avg(lef.middle_rating_final), 2) as md,
        round(avg(lef.high_rating_final), 2) as hi

    from census_final_2020  cf
        inner join yelp_enriched yp on cf.zipcode = yp.zipcode
        inner join accessibility_enriched ae on yp.zipcode = ae.zipcode
        inner join zipcode_level_listing_detail zlld on yp.zipcode = zlld.zipcode
        inner join listings_enriched_final lef on cf.zipcode = lef.zipcode
    
    where cf.zipcode = {zipcode}
    
    group by cf.zipcode
    """.format(zipcode = zipcode)
  df = pd.read_sql(query, engine)
  
  return df



# analysis 3
@st.experimental_memo
def analysis_3(zipcode):
  query = """
  select
    p.zipcode,
    p.month,
    p.avg_price_change*100 as avg_price
  from price_change_by_zipcode_and_month p
  where
      p.zipcode = {zipcode}
    """.format(zipcode = zipcode)
  
  df = pd.read_sql(query, engine)
  return df

### initiate cbsa / fixed dropdown options 
cbsa = get_cbsa()
bd, cent, edu, fam, home, inc, sch, sqft, year = get_dd()

### initiate sesison states that will be used over steps
if 'cbsa' not in st.session_state:
  st.session_state['cbsa'] = 0
    
if 'user_input' not in st.session_state:
  st.session_state['user_input'] = 0
  
if 'zipcode' not in st.session_state:
  st.session_state['zipcode'] = 0

### sidebar
with st.sidebar.form("other_form"):
    #### 1) cbsa selection form
  cbsa_param = st.selectbox("Select Geographic Area", options=[''] + cbsa['cbsatitle'].tolist())
  submit = st.form_submit_button("Submit")
  
  if submit:
    ##### map cbsa label to bucket
    user_cbsa = cbsa[cbsa['cbsatitle'] == cbsa_param]['cbsa'].values[0]
    user_cbsa = str(user_cbsa)
    st.session_state['cbsa'] = user_cbsa
    
    ##### get price, age dropdown options based on cbsa user input
    price, age = get_dd_other(user_cbsa)
    st.session_state['user_input'] = {'price': price, 'age': age}

  
  if st.session_state['cbsa'] != 0:
    #### 2) user input form
    home_type_param = st.selectbox("Preferred House Type", options=[''] + home['bucket'].tolist()) 
    bedroom_param = st.selectbox("Preferred Number of Bedrooms", options=[''] + bd['bucket'].tolist())
    sqft_param = st.selectbox("Preferred Sq Ft", options=[''] + sqft['bucket'].tolist())
    year_param = st.selectbox("Preferred Year Built", options=[''] + year['bucket'].tolist())
    price_param = st.selectbox("Preferred Price Range", options=[''] + st.session_state['user_input']['price']['bucket'].tolist())
    age_param = st.selectbox("Household Median Age", options=[''] + st.session_state['user_input']['age']['bucket'].tolist())
    inc_param = st.selectbox("Household Income", options=[''] + inc['bucket'].tolist())
    edu_param = st.selectbox("Household Level of Education", options=[''] + edu['bucket'].tolist())
    fam_param = st.selectbox("Do you have children under 19 in your household?", options=[''] + fam['bucket'].tolist())
    sch_param = st.selectbox("Grade School Importance", options=[''] + sch['bucket'].tolist())
    cent_param = st.selectbox("Proximity to City Center Importance", options=[''] + cent['bucket'].tolist())
    
    if st.form_submit_button("Predict"):
      if home_type_param == '' or bedroom_param == '' or cent_param == '' or edu_param == '' or fam_param == '' or inc_param == '' or sch_param == '' or sqft_param == '' or year_param == '' or price_param == '' or age_param == '':
        ##### if not all filled out, return error message
        st.warning("Please fill in all the fields")
        
      elif home_type_param != '' and bedroom_param != '' and cent_param != '' and edu_param != '' and fam_param != '' and inc_param != '' and sch_param != '' and sqft_param != '' and year_param != '' and price_param != '' and age_param != '':
        ##### if all filled out, map the user input label to bucket
        bedroom_input = bd[bd['bucket'] == bedroom_param]['dummy'].values[0]
        cent_input = cent[cent['bucket'] == cent_param]['dummy'].values[0]
        edu_input = edu[edu['bucket'] == edu_param]['dummy'].values[0]
        fam_input = fam[fam['bucket'] == fam_param]['dummy'].values[0]
        home_input = home[home['bucket'] == home_type_param]['dummy'].values[0]
        inc_input = inc[inc['bucket'] == inc_param]['dummy'].values[0]
        sch_input = sch[sch['bucket'] == sch_param]['dummy'].values[0]
        sqft_input = sqft[sqft['bucket'] == sqft_param]['dummy'].values[0]
        year_input = year[year['bucket'] == year_param]['dummy'].values[0]
        price_input = st.session_state['user_input']['price'][st.session_state['user_input']['price']['bucket'] == price_param]['dummy'].values[0]
        age_input = st.session_state['user_input']['age'][st.session_state['user_input']['age']['bucket'] == age_param]['dummy'].values[0]
      
        ##### get the predicted zipcode based on user input
        zip = get_zip(st.session_state['cbsa'], bedroom_input, cent_input, edu_input, fam_input, home_input, inc_input, sch_input, sqft_input, year_input, price_input, age_input)
        
        if zip != None:
          st.session_state['zipcode'] = zip
        else:
          st.warning("No recommendation found")



### main dashboard
#### 1) result zipcode display
if st.session_state['zipcode'] != 0:
  with st.container():
    st.markdown("## Your ideal neighborhood is " + str(st.session_state["zipcode"]) + "! :tada:")
else:
  with st.container():
    st.markdown("## Your ideal neighborhood is ... :thinking_face:")


tab1, tab2, tab3, tab4 = st.tabs(["Analysis", "Housing", "Food", "Fun"])   

#### 2) housing map display    
with tab1: 
  if st.session_state['zipcode'] != 0:
    
    with st.container():
      a2 = analysis_2(st.session_state['zipcode'])
      col1, col2, col3, col4 = st.columns(4)
      
      with col1:
        st.metric("Majority Age Group", a2['val_age'][0].replace('_', ' ').title())
        st.metric("Walkability Score", a2['ind_walk'][0])
        
      with col2:
        st.metric("Avg. Household Income", "$" + str(a2['avg_inc'][0]))
        st.metric("Traffic Density", a2['ind_trf'][0])
        
      with col3:
        st.metric("Unemployment Rate", str(a2['pct_unemp'][0]*100) + "%")
        st.metric("Yelp Avg. Score", a2['ind_yelp'][0])
        
      with col4:
        st.metric("Avg. Travel Time to Work", str(a2["ind_com"][0]) + " min")
        st.metric("Yelp Term Ratio", a2['pct_yelp'][0])
        
      st.metric("Majority Industry", a2["val_ind"][0])
      
    st.markdown("  ")
    st.markdown("---")
    st.markdown("  ")
    
    with st.container():
      chart = analysis_rank(st.session_state['zipcode'], st.session_state['cbsa']) 
      
      ##### display the chart
      tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs(["Unemployment", "Gender Diversity", "Commute Time", "Household Income", "WFH Rate", "Family Friendliness", "Median Age"])
      with tab5:
        st.plotly_chart(chart[0])
      with tab6:
        st.plotly_chart(chart[1])
      with tab7: 
        st.plotly_chart(chart[2])
      with tab8:
        st.plotly_chart(chart[3])
      with tab9:
        st.plotly_chart(chart[4])
      with tab10:
        st.plotly_chart(chart[5])
      with tab11:
        st.plotly_chart(chart[6])
    
    
    st.markdown("  ")
    st.markdown("---")
    st.markdown("  ")
    
    with st.container():
      a3 = analysis_3(st.session_state['zipcode'])
      col5, col6, col7, col8, col9 = st.columns(5)
      
      with col5:
        st.metric("Avg. Bedrooms", str(a2['avg_bd'][0]))
        
      with col6:
        st.metric("Avg. Bathrooms", str(a2['avg_bt'][0]))
        
      with col7:
        st.metric("Avg. YearBuilt", str(a2['avg_y'][0]))
        
      with col8:
        st.metric("Avg. Sq Ft", str(a2['avg_spft'][0]))
        
      with col9:
        st.metric("Avg. Price", str(a2['avg_price'][0]))
    
    a2
    a3
    
  else:
    ##### if no rec yet, display none
    st.map(pd.DataFrame({'lat': [33.7722], 'lon': [-84.3902]}))

    
      

#### 3) food map display      
with tab2:
  with st.container():
    if st.session_state['zipcode'] != 0:
      ##### get the housing data based on the predicted zipcode
      ls = get_listing(st.session_state['zipcode'])
      df = ls.rename(columns={"streetAddress": "Street Address", "sqft": "Sqft", "hometype_cd": "Home Type", "bedrooms": "Bedroom", "bathrooms": "Bathroom", "yearbuilt": "Year Built"})
      
      ls['address'] = ls.apply(lambda x: '%s, %s, %s, %s' % (x['streetAddress'], x['city'], x['state'], x['zipcode']), axis=1)
      ls['lat'] = 0
      ls['lon'] = 0
      
      ##### get lat, lon for each listing
      for i in range(len(ls)):
        g = gmaps_key.geocode(ls['address'][i])
        
        if g[0]["geometry"]["location"]["lat"] == 0:
          pass
        
        else:
          ls['lat'][i] = g[0]["geometry"]["location"]["lat"]
          ls['lon'][i] = g[0]["geometry"]["location"]["lng"]
          
      ##### display the map
      st.markdown("### Here are some available houses in your ideal neighborhood!")
      st.map(ls[['lat', 'lon']])
      
      ##### display the table
      st.table(df.style.format({"SqFt": "{:.0f}", "Bedroom": "{:.0f}", "Bathroom": "{:.0f}", "Year Built": "{:.0f}"}))
          
    else:
      ##### if no rec yet, display default map
      st.map(pd.DataFrame({'lat': [33.7722], 'lon': [-84.3902]}))


#### 4) fun map display      
with tab3:
  with st.container():
    if st.session_state['zipcode'] != 0:
      ##### get the food data based on the predicted zipcode
      yd = get_yelp_data(st.session_state['zipcode'])[0]

      yd.rename(
        columns={"term": "Yelp Category", "name": "Name", "rating": "Rating", "review_count": "Review Count",
                "categories": "Business Categories"}, inplace=True)

        ##### display the map
      st.markdown("### Here are some of the top restaurants from Yelp in your ideal neighborhood!")
      st.map(yd[['latitude', 'longitude']])
      
      ##### display the table
      df = yd.copy()
      df.drop('zipcode', inplace=True, axis=1, errors='ignore')
      df.drop('latitude', inplace=True, axis=1, errors='ignore')
      df.drop('longitude', inplace=True, axis=1, errors='ignore')
      st.table(df.style.format({"Review Count": "{:.0f}", "Rating": "{:.0f}"}))
        
    else:
      ##### if no rec yet, display default map
      st.map(pd.DataFrame({'lat': [33.7722], 'lon': [-84.3902]}))



#### 5) analysis display
with tab4:
  with st.container():
    if st.session_state['zipcode'] != 0:
      ##### get the fun data based on the predicted zipcode
      yd = get_yelp_data(st.session_state['zipcode'])[1]

      yd.rename(
        columns={"term": "Yelp Category", "name": "Name", "rating": "Rating", "review_count": "Review Count",
                "categories": "Business Categories"}, inplace=True)

        ##### display the map
      st.markdown("### Here are some of the top entertainments from Yelp in your ideal neighborhood!")
      st.map(yd[['latitude', 'longitude']])
      
      ##### display the table
      df = yd.copy()
      df.drop('zipcode', inplace=True, axis=1, errors='ignore')
      df.drop('latitude', inplace=True, axis=1, errors='ignore')
      df.drop('longitude', inplace=True, axis=1, errors='ignore')
      st.table(df.style.format({"Review Count": "{:.0f}", "Rating": "{:.0f}"}))
        
    else:
      ##### if no rec yet, display default map
      st.map(pd.DataFrame({'lat': [33.7722], 'lon': [-84.3902]}))\
        

def main():
  pass
    
if __name__ == '__main__':
	main()
 