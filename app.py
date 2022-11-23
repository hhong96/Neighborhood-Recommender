# %%
import altair as alt
import pandas as pd
import streamlit as st
import pymysql
import googlemaps
import sys
import util.key as key

pd.set_option('display.max_columns', None)

# Connection
def data_read(query):
      conn = pymysql.connect(host=key.host, user=key.user,
                                              password=key.password, port=key.port, database=key.database
                                              )
      df = pd.read_sql(query, conn)
      conn.close()
      return df
    
def cbsa_input(user_cbsa):
  family_type = data_read(f"select distinct family_type_dummy, case when family_type_dummy = 1 then 'Yes' else 'No' end as family_type_final from listings_enriched_final where cbsa = {user_cbsa} order by family_type_dummy desc")
  cent = data_read(f"select distinct centrality_index_dummy from listings_enriched_final where cbsa = {user_cbsa} order by centrality_index_dummy")
  yearbuilt = data_read(f"select * from call_yearbuilt where cbsa = {user_cbsa} order by yearbuilt_buckets_dummy desc")
  bd = data_read(f"select distinct bedroom_bucket_dummy, cast(round(bedrooms_final) as char) as bedrooms_final from listings_enriched_final where cbsa = {user_cbsa} order by bedroom_bucket_dummy")
  sqft = data_read(f"select * from call_sqft where cbsa = {user_cbsa}")
  hometype = data_read(f"select * from call_hometype where cbsa = {user_cbsa}")
  income = data_read(f"select * from call_income where cbsa = {user_cbsa}")
  price = data_read(f"select * from call_price where cbsa = {user_cbsa}")
  age = data_read(f"select * from call_age where cbsa = {user_cbsa}")
  return family_type, cent, yearbuilt, bd, sqft, hometype, income, price, age

def main():
# %%    
  cbsa = data_read("select distinct cbsa, cbsatitle from listings_enriched_final order by cbsa")

  # %%

  st.markdown("<div><h1 style='text-align: center;'>Where should you live?</h1></div>", unsafe_allow_html=True)
  cbsa_param = st.selectbox("Select Geographic Area", options=cbsa['cbsatitle'].tolist())

  if cbsa_param:
    user_cbsa = cbsa[cbsa['cbsatitle'] == cbsa_param]['cbsa'].values[0]
    user_cbsa = str(user_cbsa)
    
    family_type, cent, yearbuilt, bd, sqft, hometype, income, price, age = cbsa_input(user_cbsa)
    col1, col2, col3 = st.columns(3)

    with col1:
      home_type_param = st.selectbox("Home Type", options=hometype['hometype'].tolist()) 
      income_param = st.selectbox("Income", options=income['majority_income_final'].tolist())
      bedroom_param = st.select_slider("Num of Bedrooms", options=bd['bedrooms_final'].tolist(), on_change=None)

    with col2:
      price_param = st.selectbox("Ideal Price Range", price['price_bucket'].tolist())
      square_feet_param = st.selectbox("Size Preference", sqft['sqft_final'].tolist())
      year_built_param = st.selectbox("Home Year-Built", yearbuilt['year_built_final'].tolist())

    with col3:
      age_param = st.selectbox("Age", age['age_bucket'].tolist())
      family_param = st.selectbox("Do you live with your family?", options=family_type['family_type_final'].tolist())   
      centrality_param = st.selectbox("Do you prefer city?", options=cent['centrality_index_dummy'].tolist(), on_change=None)  
      
      
    if st.button('Predict'):
      home_type_param = hometype[hometype['hometype'] == home_type_param]['hometype_dummy'].values[0]
      income_param = income[income['majority_income_final'] == income_param]['majority_income_dummy'].values[0]
      bedroom_param = bd[bd['bedrooms_final'] == bedroom_param]['bedroom_bucket_dummy'].values[0]
      age_param = age[age['age_bucket'] == age_param]['median_age_dummy'].values[0]
      price_param = price[price['price_bucket'] == price_param]['price_dummy'].values[0]
      square_feet_param = sqft[sqft['sqft_final'] == square_feet_param]['sqft_buckets_dummy'].values[0]
      year_built_param  = yearbuilt[yearbuilt['year_built_final'] == year_built_param]['yearbuilt_buckets_dummy'].values[0]
      family_param = family_type[family_type['family_type_final'] == family_param]['family_type_dummy'].values[0]
      
      
      query = """
      select zipcode
      from output_vertical
      where 
      cbsa = '{}'
      and hometype_dummy = '{}'
      and majority_income_dummy = '{}'
      and bedroom_bucket_dummy = '{}'
      and median_age_dummy = '{}'
      and price_dummy = '{}'
      and sqft_buckets_dummy = '{}'
      and yearbuilt_buckets_dummy = '{}'
      and family_type_dummy = '{}'
      and centrality_index_dummy = '{}'
      """.format(user_cbsa, home_type_param, income_param, bedroom_param, age_param, price_param, square_feet_param, year_built_param, family_param, centrality_param)


      if data_read(query)['zipcode'].shape[0] == 0:
        st.markdown("<div2><h2 style='text-align: center;'> no data yet :( this is my zip code.</h2><div2>", unsafe_allow_html=True)
        zipcode = 22314
        
      else:
        zipcode = data_read(query)['zipcode'].values[0]
        st.markdown("<div2><h2 style='text-align: center;'>We recommend you live in zipcode " + str(zipcode) + "!</h2><div2>", unsafe_allow_html=True)
        
      ls = data_read("select * from listing where zipcode = {} limit 10".format(zipcode))
      ls['address'] = ls.apply(lambda x: '%s, %s, %s, %s' % (x['streetAddress'], x['city'], x['state'], x['zipcode']), axis=1)
      ls['lat'] = 0
      ls['lon'] = 0
      
      gmaps_key = googlemaps.Client(key=key.api_key)
      
      for i in range(len(ls)):
        g = gmaps_key.geocode(ls['address'][i])
        if g[0]["geometry"]["location"]["lat"] != 0:
          ls['lat'][i] = g[0]["geometry"]["location"]["lat"]
          ls['lon'][i] = g[0]["geometry"]["location"]["lng"]
        
      # %%
      with st.container():
        st.map(ls[['lat', 'lon']])
    
    
if __name__ == '__main__':
	main()
 