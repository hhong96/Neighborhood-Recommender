import requests
import csv
import pymysql
import pandas as pd
import pyodbc
import random

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# create session
session = requests.Session()
credentials = {
    'Authorization': 'Bearer rDR4ZlExYjRVWoti0dAk1N_XcLZ1UHeEcNos-gW-GPD-fvF_m011eVGGxHT5_Mf-s'
                     '-YqZN_VC9kKxWYUrso1555alfIjEyN2BQ54VRDwa5XsoAmBxSUF8bi-wttCY3Yx '
    # 'Authorization': 'Bearer CQXzRo9NPu6G9AjCLTytuR8PUMZI1AWQGDn3QsTHstJemKhFAcLdGgdn-TXiZx9'
    #                  '-wZervjpriKYU2c_CrqgF3G59tw-PzAFp0Z52g-3U0DNAUJRUdcOdY2ye1JJZY3Yx '
}

session.headers['Authorization'] = credentials['Authorization']
url = ''

# Connection
# query for read sql
def data_read(query):
      conn = pymysql.connect(host='cse6242.czj7hqwhnoml.us-east-1.rds.amazonaws.com', user="admin",
                                              password="cse6242110", port=3306, database="realestate"
                                              )
      df = pd.read_sql(query, conn)
      conn.close()
      return df

def readSS(query):
    conn_str = ("Driver={SQL Server Native Client 11.0};"
                "Server=localhost;"
                "Database=CSE6242;"
                "Trusted_Connection=yes;")
    conn = pyodbc.connect(conn_str)

    df = pd.read_sql(query, conn)
    conn.close()
    return df

def getData(location, term, limit):
    url = 'https://api.yelp.com/v3/businesses/search?location='+location+'&term='+term+'&limit=' + str(limit)
    data = session.get(url).json()
    return data

def getDataCBSA(location, term, limit, sortby):
    #https://api.yelp.com/v3/businesses/search?location=Atlanta-Sandy Springs-Roswell, GA&term=food&limit=50&sort_by=rating
    url = 'https://api.yelp.com/v3/businesses/search?location='+location+'&term='+term+'&limit=' + str(limit) + '&sort_by=' + sortby
    data = session.get(url).json()
    return data

def getAverageScore(data, total_review_count):
    scores = []
    for d in data['businesses']:
        is_closed = d['is_closed']
        if not is_closed:
            review_count = +d['review_count']
            rating = +d['rating']
            score = review_count / total_review_count * rating
            scores.append(score)
    location_score = sum(scores) / len(scores) * 100
    return round(location_score, 2)

def getTermToHouseholdRatio(bCount,hhCount):
    return round(bCount / hhCount, 2)

def getCategoryTotalReviewCount(data):
    category_count = {}
    total_review_count = 0
    for d in data['businesses']:
        is_closed = d['is_closed']
        if not is_closed:
            review_count = +d['review_count']
            total_review_count = total_review_count + review_count
            categories = d['categories']
            for c in categories:
                title = c['title']
                if title in category_count.keys():
                    count = category_count[title]
                    count = count + 1
                    category_count[title] = count
                else:
                    category_count[title] = 1
    return category_count, total_review_count

def writeMetrics(metrics):
    with open("metrics.txt", "a") as f:
        for m in metrics:
            f.write(m)


# with open("yelp_cbsa.csv", "a", newline="", encoding='utf-8') as f:
#     fieldnames = ['cbsa', 'location', 'term', 'name', 'review_count', 'rating', 'latitude', 'longitude', 'categories']
#     writer = csv.DictWriter(f, fieldnames=fieldnames)
#     writer.writeheader()

with open("yelp_zc.csv", "a", newline="", encoding='utf-8') as f:
    fieldnames = ['zipcode', 'term', 'name', 'review_count', 'rating', 'latitude', 'longitude', 'categories']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

query = """SELECT DISTINCT CAST(zipcode AS CHAR(10)) AS zipcode FROM listings_enriched_final ORDER BY zipcode"""
qData = data_read(query)
for index, row in qData.iterrows():
    location = row["zipcode"]

    limit = 50
    sortby = "rating"

    term = "Food"

    data = getDataCBSA(location, term, limit, sortby)
    if 'businesses' in data:
        for d in data['businesses']:
            is_closed = d['is_closed']
            if not is_closed:
                name = d['name']
                review_count = +d['review_count']
                rating = d['rating']
                if 'coordinates' in d:
                    coordinates = d['coordinates']
                    latitude = coordinates['latitude']
                    longitude = coordinates['longitude']
                    if latitude is not None and longitude is not None:
                        categories_str = ''
                        categories = d['categories']
                        for c in categories:
                            title = c['title']
                            categories_str = categories_str + ', ' + title
                        categories_str = categories_str[2:]
                        # print(cbsa, location, term, name, review_count, rating, latitude, longitude, categories_str)
                        with open("yelp_zc.csv", "a", newline="", encoding='utf-8') as f:
                            fieldnames = ['zipcode', 'term', 'name', 'review_count', 'rating', 'latitude',
                                          'longitude',
                                          'categories']
                            writer = csv.DictWriter(f, fieldnames=fieldnames)
                            writer.writerow({'zipcode': location, 'term': term, 'name': name,
                                             'review_count': review_count, 'rating': rating, 'latitude': latitude,
                                             'longitude': longitude, 'categories': categories_str})
    else:
        print("Not Found")

    term = "Fun"

    data = getDataCBSA(location, term, limit, sortby)
    if 'businesses' in data:
        for d in data['businesses']:
            is_closed = d['is_closed']
            if not is_closed:
                name = d['name']
                review_count = +d['review_count']
                rating = d['rating']
                if 'coordinates' in d:
                    coordinates = d['coordinates']
                    latitude = coordinates['latitude']
                    longitude = coordinates['longitude']
                    if latitude is not None and longitude is not None:
                        categories_str = ''
                        categories = d['categories']
                        for c in categories:
                            title = c['title']
                            categories_str = categories_str + ', ' + title
                        categories_str = categories_str[2:]
                        # print(cbsa, location, term, name, review_count, rating, latitude, longitude, categories_str)
                        with open("yelp_zc.csv", "a", newline="", encoding='utf-8') as f:
                            fieldnames = ['zipcode', 'term', 'name', 'review_count', 'rating', 'latitude',
                                          'longitude',
                                          'categories']
                            writer = csv.DictWriter(f, fieldnames=fieldnames)
                            writer.writerow({'zipcode': location, 'term': term, 'name': name,
                                             'review_count': review_count, 'rating': rating, 'latitude': latitude,
                                             'longitude': longitude, 'categories': categories_str})
    else:
        print("Not Found")

# query = """SELECT DISTINCT cbsa, cbsatitle FROM listings_enriched_final ORDER BY cbsatitle"""
# qData = data_read(query)
# for index, row in qData.iterrows():
#     cbsa = row["cbsa"]
#     location = row["cbsatitle"]

    # limit = 50
    # sortby = "rating"
    #
    # term = "Food"
    #
    # data = getDataCBSA(location, term, limit, sortby)
    # if 'businesses' in data:
    #     for d in data['businesses']:
    #         is_closed = d['is_closed']
    #         if not is_closed:
    #             name = d['name']
    #             review_count = +d['review_count']
    #             rating = d['rating']
    #             if 'coordinates' in d:
    #                 coordinates = d['coordinates']
    #                 latitude = coordinates['latitude']
    #                 longitude = coordinates['longitude']
    #                 if latitude is not None and longitude is not None:
    #                     categories_str = ''
    #                     categories = d['categories']
    #                     for c in categories:
    #                         title = c['title']
    #                         categories_str = categories_str + ', ' + title
    #                     categories_str = categories_str[2:]
    #                     # print(cbsa, location, term, name, review_count, rating, latitude, longitude, categories_str)
    #                     with open("yelp_cbsa.csv", "a", newline="", encoding='utf-8') as f:
    #                         fieldnames = ['cbsa', 'location', 'term', 'name', 'review_count', 'rating', 'latitude',
    #                                       'longitude',
    #                                       'categories']
    #                         writer = csv.DictWriter(f, fieldnames=fieldnames)
    #                         writer.writerow({'cbsa': cbsa, 'location': location, 'term': term, 'name': name,
    #                                          'review_count': review_count, 'rating': rating, 'latitude': latitude,
    #                                          'longitude': longitude, 'categories': categories_str})
    # else:
    #     print("Not Found")
    #
    # term = "Fun"
    #
    # data = getDataCBSA(location, term, limit, sortby)
    # if 'businesses' in data:
    #     for d in data['businesses']:
    #         is_closed = d['is_closed']
    #         if not is_closed:
    #             name = d['name']
    #             review_count = +d['review_count']
    #             rating = d['rating']
    #             if 'coordinates' in d:
    #                 coordinates = d['coordinates']
    #                 latitude = coordinates['latitude']
    #                 longitude = coordinates['longitude']
    #                 if latitude is not None and longitude is not None:
    #                     categories_str = ''
    #                     categories = d['categories']
    #                     for c in categories:
    #                         title = c['title']
    #                         categories_str = categories_str + ', ' + title
    #                     categories_str = categories_str[2:]
    #                     # print(cbsa, location, term, name, review_count, rating, latitude, longitude, categories_str)
    #                     with open("yelp_cbsa.csv", "a", newline="", encoding='utf-8') as f:
    #                         fieldnames = ['cbsa', 'location', 'term', 'name', 'review_count', 'rating', 'latitude',
    #                                       'longitude',
    #                                       'categories']
    #                         writer = csv.DictWriter(f, fieldnames=fieldnames)
    #                         writer.writerow({'cbsa': cbsa, 'location': location, 'term': term, 'name': name,
    #                                          'review_count': review_count, 'rating': rating, 'latitude': latitude,
    #                                          'longitude': longitude, 'categories': categories_str})
    # else:
    #     print("Not Found")

# query = """SELECT zipcode, hhCount FROM listings_final where zipcode <> 'None' """
#
# qData = readSS(query)
# print(qData.count())
#
# metrics = []
# for index, row in qData.iterrows():
#     location = row["zipcode"] # original location value
#     location_fix = str(location).zfill(5) # fixed for api calls
#     hhCount = row["hhCount"]
#     print(location_fix)
#
#     term = 'fun' # based on 2 categories
#     limit = 50 # max limit by yelp
#
#     #make the api call
#     data = getData(location, term, limit)
#     if 'businesses' in data:
#         #gets category counts and total review count
#         categories, total_review_count = getCategoryTotalReviewCount(data)
#         # metrics.append("INSERT INTO YelpMetrics_Staging (zipcode, metric_type, value) VALUES ('"+location+"', 'food_count', "+str(len(categories.keys()))+");\n")
#         metrics.append("INSERT INTO YelpMetrics_Staging (zipcode, metric_type, value) VALUES ('"+location+"', 'fun_count', "+str(len(categories.keys()))+");\n")
#
#
#         #gets average score based on
#         #(business reviews count / sum of total business reviews) * rating * 100 ?
#         average_score = getAverageScore(data,total_review_count)
#         # metrics.append("INSERT INTO YelpMetrics_Staging (zipcode, metric_type, value) VALUES ('"+location+"', 'food_average_score', "+str(average_score)+");\n")
#         metrics.append("INSERT INTO YelpMetrics_Staging (zipcode, metric_type, value) VALUES ('"+location+"', 'fun_average_score', "+str(average_score)+");\n")
#
#         #gets the ratio of term options / listings in zipcode
#         #need to work on this to produce ratios for other categories to
#         ratio = getTermToHouseholdRatio(limit, hhCount)
#         # metrics.append("INSERT INTO YelpMetrics_Staging (zipcode, metric_type, value) VALUES ('"+location+"', 'ratio', "+str(ratio)+");\n")
#     else:
#         print(location + " no businesses found")
#
# if len(metrics) > 0:
#     writeMetrics(metrics)






