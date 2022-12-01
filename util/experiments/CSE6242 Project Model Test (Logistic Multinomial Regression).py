"""CSE6242 PROJECT MODEL"""
"""MULTINOMIAL LOGISTIC REGRESSION"""
# %% MODULES
import mysql
import mysql.connector
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_recall_fscore_support
import numpy as np

# %% CONSTANTS
# DATABASE CREDENTIALS
HOST = "cse6242.czj7hqwhnoml.us-east-1.rds.amazonaws.com"
USER = "admin"
PASSWORD = "cse6242110"
DATABASE = "realestate"
PORT = 3306

# TABLE (IN CASE NAME OF FINAL DATA TABLE CHANGES)
TABLE_NAME = "listings_enriched_final"

# COLUMN NAMES
CBSA = "cbsa"
CBSATITLE = "cbsatitle"
ZIPCODE = "zipcode"
HOMETYPE_DUMMY = "hometype_dummy"
SQFT_BUCKETS_DUMMY = "sqft_buckets_dummy" 
BEDROOM_BUCKET_DUMMY = "bedroom_bucket_dummy" 
BATHROOMS_BUCKET_DUMMY = "bathrooms_bucket_dummy" 
FAMILY_TYPE_DUMMY = "family_type_dummy" 
MAJORITY_AGE_GROUP_DUMMY = "majority_age_group_dummy" 
MAJORITY_EDUCATION_DUMMY = "majority_education_dummy" 
YEARBUILT_BUCKETS_DUMMY = "yearbuilt_buckets_dummy" 
OVERALL_EDUCATION_SCORE_DUMMY = "overall_education_score_dummy" 
CENTRALITY_INDEX_DUMMY = "centrality_index_dummy" 
PRICE_DUMMY = "price_dummy"

# OTHER COLUMN NAMES
AVG_SQFT = "avg_sqft"
AVG_BEDROOMS = "avg_bedrooms"
AVG_BATHROOMS = "avg_bathrooms"
AVG_YEAR_BUILT = "avg_year_built"
PERCENT_MALE = "percent_male",
PERCENT_FEMALE = "percent_female"
DIVERSITY_SCORE = "diversity_score"
MEDIAN_AGE = "median_age"
MEAN_INCOME = "mean_household_income"
UNEMPLOYMENT_RATE = "unemployment_rate"

# CBSA USED FOR FILTERING (CAN BE CHANGED TO TEST DIFFERENT CBSAs)
CBSA_CHECK = 47900

# TRAIN-TEST (CAN BE CHANGED FOR DIFFERENT TEST SIZES)
TEST_SIZE = 0.3             # Should be between 0 and 1
TRAIN_SIZE = 1-TEST_SIZE

# %% Database connection
db = mysql.connector.connect(
    host = HOST,
    user = USER,
    password = PASSWORD,
    database = DATABASE,
    port = PORT
)

# %% Cursor for database
db_cursor = db.cursor()

# %% SQL Query
main_data_query = f"""
SELECT
    cbsa,
    cbsatitle,
	zipcode,
    hometype_dummy,
	sqft_buckets_dummy,
	bedroom_bucket_dummy,
	bathrooms_bucket_dummy,
	family_type_dummy,
	majority_age_group_dummy,
	majority_education_dummy,
	yearbuilt_buckets_dummy,
	overall_education_score_dummy,
	centrality_index_dummy,
	price_dummy
FROM {DATABASE}.{TABLE_NAME}
"""

# CBSA summary query
cbsa_query = f"""
SELECT
	cbsa,
	cbsatitle,
	AVG(SqFt_final) AS avg_sqft,
	AVG(bedrooms_final) AS avg_bedrooms,
	AVG(bathrooms_final) AS avg_bathrooms,
	AVG(year_built_final) AS avg_year_built,
    AVG(percent_male_final) AS percent_male,
    AVG(percent_female_final) AS percent_female,
    AVG(diversity_score) AS diversity_score,
    AVG(median_age_final) AS median_age,
    AVG(mean_household_income_dollars_final) AS mean_household_income,
    AVG(unemployment_rate_final) AS unemployment_rate
FROM {DATABASE}.{TABLE_NAME}
GROUP BY 
	cbsa,
	cbsatitle
"""

# %% Execute query using database cursor
db_cursor.execute(main_data_query)

# %% Create dataframe using data from query
df = pd.DataFrame(db_cursor.fetchall())

# %% Execute cbsa_query using database cursor
db_cursor.execute(cbsa_query)

# %% Create dataframe using data from cbsa_query
cbsa_df = pd.DataFrame(db_cursor.fetchall())

# %% List of column names for dataframe
df_column_names =   [
                    CBSA,
                    CBSATITLE,
                    ZIPCODE,
                    HOMETYPE_DUMMY,
                    SQFT_BUCKETS_DUMMY, 
                    BEDROOM_BUCKET_DUMMY, 
                    BATHROOMS_BUCKET_DUMMY, 
                    FAMILY_TYPE_DUMMY, 
                    MAJORITY_AGE_GROUP_DUMMY, 
                    MAJORITY_EDUCATION_DUMMY, 
                    YEARBUILT_BUCKETS_DUMMY, 
                    OVERALL_EDUCATION_SCORE_DUMMY, 
                    CENTRALITY_INDEX_DUMMY, 
                    PRICE_DUMMY
                    ]

# %% List of column names for cbsa dataframe
cbsa_df_column_names =  [
                        CBSA,
                        CBSATITLE,
                        AVG_SQFT,
                        AVG_BEDROOMS,
                        AVG_BATHROOMS,
                        AVG_YEAR_BUILT,
                        PERCENT_MALE,
                        PERCENT_FEMALE,
                        DIVERSITY_SCORE,
                        MEDIAN_AGE,
                        MEAN_INCOME,
                        UNEMPLOYMENT_RATE
                        ]

# %% List for column names for dummy variables
dummy_column_names = df_column_names[3:]

# %% Rename columns using list
df.columns = df_column_names
cbsa_df.columns = cbsa_df_column_names

# Summary statistics for the main dataframe
df_describe = df.describe()

# %% Filter dataframe based on CBSA
# Check if CBSA used for testing is in dataset
assert CBSA_CHECK in df[CBSA], "CBSA not found. Use a valid one."

filtered_df = df[df[CBSA] == CBSA_CHECK]
cbsa_filtered = cbsa_df[cbsa_df[CBSA] == CBSA_CHECK]

# Summary statistics for the filtered dataframe
filtered_df_describe = filtered_df.describe()

# %% CBSA Information
cbsa_title = list(cbsa_filtered[CBSATITLE].unique())[0]
cbsa_sqft = list(cbsa_filtered[AVG_SQFT].unique())[0]
cbsa_bedrooms = list(cbsa_filtered[AVG_BEDROOMS].unique())[0]
cbsa_bathrooms = list(cbsa_filtered[AVG_BATHROOMS].unique())[0]
cbsa_year = list(cbsa_filtered[AVG_YEAR_BUILT].unique())[0]
cbsa_male = list(cbsa_filtered[PERCENT_MALE].unique())[0]
cbsa_female =  list(cbsa_filtered[PERCENT_FEMALE].unique())[0]
cbsa_diversity = list(cbsa_filtered[DIVERSITY_SCORE].unique())[0]
cbsa_age =  list(cbsa_filtered[MEDIAN_AGE].unique())[0]
cbsa_income =  list(cbsa_filtered[MEAN_INCOME].unique())[0]
cbsa_unemployment = list(cbsa_filtered[UNEMPLOYMENT_RATE].unique())[0]

# %% Change zipcode data type to category
filtered_df[ZIPCODE] = filtered_df[ZIPCODE].astype("category")    # Equivalent to creating dummy categorical variable

# %% List of unique zipcodes
unique_zip = list((filtered_df[ZIPCODE].unique()))
unique_zip = [str(x) for x in unique_zip]
unique_zip.sort()

# %% Assign x variables
X = filtered_df[dummy_column_names]

# %% Assign zipcode for dependent variable
y = filtered_df[ZIPCODE]

# %% Train-test split; random_state parameter can be changed/removed (used for consistent results)
assert TEST_SIZE > 0 and TEST_SIZE < 1, "TEST_SIZE must be between 0 and 1"
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=TEST_SIZE, random_state=110)

# %% Establish logistic regression model
logistic = LogisticRegression()

# %% Fit training data to model
logistic.fit(X_train, y_train)

# %% Predict logistic model using test data
y_pred = logistic.predict(X_test)

# %% Model accuracy score
model_accuracy = accuracy_score(y_test, y_pred)

# %% Precision/recall/f-score/support scores
scores = precision_recall_fscore_support(y_pred, y_test, average ='weighted')

# %% Convert predictions to series
predictions = pd.Series(y_pred, name = "predictions")

# %% Create copy of test data for zipcode; reset index
y_test_copy = y_test.reset_index().copy()

# %% Concatenate/join the test data for y and its predictions to create dataframe
test_pred = pd.concat([y_test_copy,predictions], axis =1, ignore_index=False)

# %% Highlight matches in dataframe where original zipcode is same as predicted zipcode
test_pred["match"] = np.where(test_pred[ZIPCODE] == test_pred["predictions"], 1,0)    # 1 if yes; 0 if no

# %% Filter dataframe for matches
test_pred = test_pred[test_pred["match"] == 1]

# %% Dataframe of zipcode and matches
test_pred = test_pred[[ZIPCODE, "match"]]

# %% Aggregate dataframe by zipcode and sum # of matches
test_pred = test_pred.groupby(ZIPCODE).sum()

# %% Create dataframe for # of times zipcode is recorded in test data
row_entries = pd.DataFrame(y_test.value_counts())   # Dataframe for value counts
row_entries.reset_index(inplace=True)               # Remove index
row_entries.columns = [ZIPCODE, "total_rows"]     # Rename columns

# %% Merge dataframes on zipcode
zipcode_df = pd.merge(test_pred, row_entries, how = "left", on = ZIPCODE)

# %% Calculate accuracy for individual zipcodes based on # of zipcode matches divided by # of total rows
zipcode_df["accuracy"] = zipcode_df["match"]/zipcode_df["total_rows"]

# %% Sort data by accuracy score and # of total rows
zipcode_df = zipcode_df.sort_values(by = ["accuracy", "total_rows"], ascending = False)

# %% PREDICTIONS
# Values for dummy variables
hometype_dummy_values = sorted(df[HOMETYPE_DUMMY].unique())
sqft_dummy_values = sorted(df[SQFT_BUCKETS_DUMMY].unique())
bedroom_dummy_values = sorted(df[BEDROOM_BUCKET_DUMMY].unique())
bathrooms_dummy_values = sorted(df[BATHROOMS_BUCKET_DUMMY].unique())
family_type_dummy_values = sorted(df[FAMILY_TYPE_DUMMY].unique())
majority_age_group_dummy_values = sorted(df[MAJORITY_AGE_GROUP_DUMMY].unique())
majority_education_dummy_values = sorted(df[MAJORITY_EDUCATION_DUMMY].unique())
yearbuilt_dummy_values = sorted(df[YEARBUILT_BUCKETS_DUMMY].unique())
overall_education_score_dummy_values = sorted(df[OVERALL_EDUCATION_SCORE_DUMMY].unique())
centrality_index_dummy_values = sorted(df[CENTRALITY_INDEX_DUMMY].unique())
price_dummy_values = sorted(df[PRICE_DUMMY].unique())

# Number of combinations for predictions
num_combinations =  len(hometype_dummy_values) * \
                    len(sqft_dummy_values) * \
                    len(bedroom_dummy_values) * \
                    len(bedroom_dummy_values) * \
                    len(family_type_dummy_values) * \
                    len(majority_age_group_dummy_values) * \
                    len(majority_education_dummy_values) * \
                    len(yearbuilt_dummy_values) * \
                    len(overall_education_score_dummy_values) * \
                    len(centrality_index_dummy_values) * \
                    len(price_dummy_values)

# %% Create dataframe for all combinations based on data for CBSA
lst = []
for hometype in hometype_dummy_values:
    for sqft in sqft_dummy_values:
        for bedroom in bedroom_dummy_values:
            for bathroom in bathrooms_dummy_values:
                for family in family_type_dummy_values:
                    for age in majority_age_group_dummy_values:
                        for education in majority_education_dummy_values:
                            for year in yearbuilt_dummy_values:
                                for educ_score in overall_education_score_dummy_values:
                                    for centrality in centrality_index_dummy_values:
                                       for price in price_dummy_values: 
                                            lst.append([hometype, 
                                                        sqft, 
                                                        bedroom, 
                                                        bathroom, 
                                                        family, 
                                                        age, 
                                                        education,
                                                        year,
                                                        educ_score,
                                                        centrality,
                                                        price])

combination_df = pd.DataFrame(lst, columns=dummy_column_names)
combination_df = combination_df.sort_values(dummy_column_names, ascending=True)

# %% Predictions for zipcodes using all combinations for CBSA
zipcode_predictions = logistic.predict(combination_df)

# %% Create series for zipcode predictions
zipcode_predictions = pd.Series(zipcode_predictions, name = "zipcode_count")

# %% RECOMMENDATIONS (RECOMMENDED ZIPCODE)
# Dataframe for recommended zipcodes for all combinations; output for final data
recommendations = pd.concat([combination_df,zipcode_predictions], axis =1, ignore_index=False)
recommendations[CBSA] = CBSA_CHECK

# %% Create dataframe for counts of recommended zipcode
recommended_zip_counts = recommendations["zipcode_count"].value_counts()
recommended_zip_counts = pd.DataFrame(recommended_zip_counts)
recommended_zip_counts.reset_index(inplace=True)
recommended_zip_counts.columns = ["recommended_zipcode", "count"]

# %% SUMMARY
print(f"""
Data from {DATABASE}.{TABLE_NAME} ({len(df)} observations)

Summary data for CBSA {CBSA_CHECK} ({cbsa_title})
-------------------------------------
There are {len(filtered_df)} observations with {len(filtered_df[ZIPCODE].unique())} unique zipcodes: {', '.join(unique_zip)}. 

Properties in CBSA {CBSA_CHECK} on average were built in {int(cbsa_year)} and have {cbsa_sqft.round(2)} of square feet, {cbsa_bedrooms.round(2)} bedrooms and {cbsa_bathrooms.round(2)} bathrooms. CBSA {CBSA_CHECK} has a male-female ratio is {(cbsa_male*100).round(1)}-{(cbsa_female*100).round(1)}, diversity score of {cbsa_diversity.round(2)}, median age of {int(cbsa_age)}, unemployment rate of {(cbsa_unemployment*100).round(1)}%, and average household income of ${cbsa_income.round(2)}.

With a training-testing split of {TRAIN_SIZE*100}-{TEST_SIZE*100}, there are {len(X_train)} observations in the training dataset and {len(X_test)} observations in the testing dataset.

The precision of the model is {scores[0]}.
The recall of the model is {scores[1]}.
The f-score of the model is {scores[2]}.

Based on the data, there are {num_combinations} input combinations for predictions. 

The top 2 most recommended zipcodes for the various input combinations for CBSA {CBSA_CHECK} are
{recommended_zip_counts["recommended_zipcode"][0]} (recommended {recommended_zip_counts["count"][0]} times out of {num_combinations} combinations; {round(recommended_zip_counts["count"][0]/sum(recommended_zip_counts["count"])*100,2)}%) and {recommended_zip_counts["recommended_zipcode"][1]} (recommended {recommended_zip_counts["count"][1]} times out of {num_combinations} combinations; {round(recommended_zip_counts["count"][1]/sum(recommended_zip_counts["count"])*100,2)}%).

NOTE:
To view specific zipcode recommendations based on various input combinations, check the recommendations variable. To see how accurate the model was for recommending an individual zipcode in the CBSA, see the zipcode_df variable. Various statistics for all CBSAs can be found in cbsa_df variable. For summary statistics for the specific CBSA used for testing, check the filtered_df_describe variable. Other summary statistics (for the complete data) can be viewed with the df_describe variable. 

To identify other CBSAs for testing, check the unique_cbsa variable. To test a different CBSA, choose a CBSA in unique_cbsa and change the CBSA_CHECK constant to your selection, then run this file again.
""")

# %%