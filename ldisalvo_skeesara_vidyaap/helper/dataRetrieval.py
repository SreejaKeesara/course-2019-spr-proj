"""
CS504 : dataRetrieval
Team : Vidya Akavoor, Lauren DiSalvo, Sreeja Keesara
Description :

Notes : 

April 30, 2019
"""
import urllib
import json
import pandas as pd
import pymongo

from ldisalvo_skeesara_vidyaap.helper.constants import HOUSE_DISTRICT_SHAPE_URL, \
    SENATE_DISTRICT_SHAPE_URL, TEAM_NAME, DEMOGRAPHIC_DATA_DISTRICT_SENATE_NAME, \
    DEMOGRAPHIC_DATA_DISTRICT_HOUSE_NAME, WEIGHTED_HOUSE_IDEOLOGIES_NAME, \
    WEIGHTED_SENATE_IDEOLOGIES_NAME, HISTORICAL_RATIOS_HOUSE_NAME, HISTORICAL_RATIOS_SENATE_NAME, \
    SENATE_KEY, HOUSE_KEY

class dataRetrieval:
    def process_map_data(url, populationData):
        csv_string = urllib.request.urlopen(url).read().decode("utf-8")
        response = json.loads(csv_string)['features']
        for district in response:
            lon, lat = dataRetrieval.calculate_center(district['geometry']['type'], district['geometry']['coordinates'][0])
            name = district['properties']['NAME'].replace('First', '1st').replace('Second', '2nd').replace('Third', '3rd').replace('Fourth', '4th').replace('Fifth', '5th').replace('Sixth', '6th').replace('Midddlesex', 'Middlesex').replace('&', 'and').replace('Berkshire, Hampshire, Franklin and Hampden', 'Berkshire, Hampshire and Franklin')
            population = int(populationData[populationData['district'] == name]["Population, Census, April 1, 2010"].tolist()[0])
            district['lat'] = lat
            district['lon'] = lon
            district['name'] = name
            district['population'] = population
            district.pop('type')
            district.pop('geometry')
            district.pop('properties')

        df = pd.DataFrame.from_records(response)
        return df

    def calculate_center(type, coordinates):
        if type == 'MultiPolygon':
            coordinates = coordinates[0]

        x = [float(p[0]) for p in coordinates]
        y = [float(p[1]) for p in coordinates]
        return sum(x) / len(coordinates), sum(y) / len(coordinates)

    def get_population_data(type):
        if type == SENATE_KEY:
            return pd.DataFrame.from_records(list(repo[DEMOGRAPHIC_DATA_DISTRICT_SENATE_NAME].find({}, {"Population, Census, April 1, 2010": 1, "Senate District": 1}))).rename(index=str, columns={"Senate District": "district"})
        else:
            return pd.DataFrame.from_records(list(repo[DEMOGRAPHIC_DATA_DISTRICT_HOUSE_NAME].find({}, {"Population, Census, April 1, 2010": 1, "House District": 1}))).rename(index=str, columns={"House District": "district"})

    def get_ideology_ratios(type, isAverage):
        if isAverage:
            dataset = WEIGHTED_SENATE_IDEOLOGIES_NAME if type == SENATE_KEY else WEIGHTED_HOUSE_IDEOLOGIES_NAME
        else:
            dataset = HISTORICAL_RATIOS_SENATE_NAME if type == SENATE_KEY else HISTORICAL_RATIOS_HOUSE_NAME

        return pd.DataFrame.from_records(list(repo[dataset].find()))

    def get_ratios_list(df, isAverage, districtList, year):
        ratiosList = []

        if isAverage:
            for district in districtList:
                ratiosList.append(df[df['district'] == district]['Average ratio'])
        else:
            for district in districtList:
                ratiosList.append(df[df['year'] == year][district])

        return ratiosList


# Set up the database connection.
client = pymongo.MongoClient()
repo = client.repo
repo.authenticate(TEAM_NAME, TEAM_NAME)

SENATE_BY_YEAR = dataRetrieval.get_ideology_ratios(SENATE_KEY, False)
HOUSE_BY_YEAR = dataRetrieval.get_ideology_ratios(HOUSE_KEY, False)
SENATE_AVERAGE = dataRetrieval.get_ideology_ratios(SENATE_KEY, True)
HOUSE_AVERAGE = dataRetrieval.get_ideology_ratios(HOUSE_KEY, True)

HOUSE_MAP_POINTS = dataRetrieval.process_map_data(HOUSE_DISTRICT_SHAPE_URL, dataRetrieval.get_population_data(HOUSE_KEY))
SENATE_MAP_POINTS = dataRetrieval.process_map_data(SENATE_DISTRICT_SHAPE_URL, dataRetrieval.get_population_data(SENATE_KEY))

repo.logout()
