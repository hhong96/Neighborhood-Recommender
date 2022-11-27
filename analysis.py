import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import util.key as key
import inflect

p = inflect.engine()
engine = create_engine(key.engine, echo=False)


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
        fig.show()