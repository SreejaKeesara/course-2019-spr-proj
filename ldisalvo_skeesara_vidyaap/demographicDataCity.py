"""
CS504 : demographicDataCity.py
Team : Vidya Akavoor, Lauren DiSalvo, Sreeja Keesara
Description : Retrieval of demographic data by city using census.gov

Notes :

March 31, 2019
"""

import datetime
import uuid

import dml
import pandas as pd
import prov.model
import urllib.request

from ldisalvo_skeesara_vidyaap.helper.constants import TEAM_NAME, COUNTY_URL, MA_CITY_LIST, DEMOGRAPHIC_DATA_TOWN_NAME,\
    TOWN_URL


class demographicDataCity(dml.Algorithm):
    contributor = TEAM_NAME
    reads = [DEMOGRAPHIC_DATA_TOWN_NAME]
    writes = [DEMOGRAPHIC_DATA_TOWN_NAME]

    @staticmethod
    def execute(trial=False):
        """
            Retrieve demographic data by city from census.gov and insert into collection (collection already contains
            town information)
            ex)
             { "Town" : "Fitchburg city, Massachusetts",
               "Population estimates, July 1, 2017,  (V2017)" : 40793,
               "Population estimates base, April 1, 2010,  (V2017)" : 40318,
               "Median selected monthly owner costs -without a mortgage, 2013-2017" : 652,
                ..........................
            }
        """
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate(TEAM_NAME, TEAM_NAME)

        # Retrieve data from census.gov for each city (note: retrieval generates csv with max of 6 locations)
        city_divisions = [MA_CITY_LIST[:6], MA_CITY_LIST[6:12], MA_CITY_LIST[12:18], MA_CITY_LIST[18:24],
                          MA_CITY_LIST[24:30], MA_CITY_LIST[30:36], MA_CITY_LIST[36:42], MA_CITY_LIST[42:48],
                          MA_CITY_LIST[48:54], MA_CITY_LIST[54:60], MA_CITY_LIST[60:66], MA_CITY_LIST[66:72],
                          MA_CITY_LIST[72:78], MA_CITY_LIST[78:84], MA_CITY_LIST[84:90], MA_CITY_LIST[90:96],
                          MA_CITY_LIST[96:102], MA_CITY_LIST[102:108], MA_CITY_LIST[108:114], MA_CITY_LIST[114:120]]
        all_dfs= []
        for divisions in city_divisions:
            cities = ""
            for city in divisions:
                cities += (city.lower().replace(",", "") + ",").replace(" ", "")
            cities = cities[:-1]
            url = TOWN_URL[:43] + cities + COUNTY_URL[43:]
            df = pd.read_csv(urllib.request.urlopen(url))
            df = df.drop(df.index[-20:])
            df.set_index("Fact", inplace=True)
            df = df.transpose()
            df = df[~df.index.str.contains("Note")]
            cols = list(df)
            all_dfs.append(df)

        for df in all_dfs:
            df.columns = cols

        joined_df = pd.concat(all_dfs)
        df = joined_df.dropna(axis=1, how='all')
        df = df.reset_index()
        df = df.rename(columns={'index': 'Town'})

        # Clean data and convert to numeric
        dfCols = list(df.columns[1:-1])
        for x in dfCols:
            df[x] = df[x].str.replace(",", "")
            df[x] = df[x].str.replace("%", "")
            df[x] = df[x].str.replace("$", "")
            df[x] = df[x].str.replace("+", "")
            df[x] = df[x].apply(pd.to_numeric, errors='coerce')

        records = []
        for x in df.to_dict(orient='records'):
            records += [x]

        # Insert rows into collection
        repo[DEMOGRAPHIC_DATA_TOWN_NAME].insert_many(records)
        repo[DEMOGRAPHIC_DATA_TOWN_NAME].metadata({'complete': True})
        print(repo[DEMOGRAPHIC_DATA_TOWN_NAME].metadata())

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start": startTime, "end": endTime}


    @staticmethod
    def provenance(doc=prov.model.ProvDocument(), startTime=None, endTime=None):
        '''
            Create the provenance document describing everything happening
            in this script. Each run of the script will generate a new
            document describing that invocation event.
            '''

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate(TEAM_NAME, TEAM_NAME)
        doc.add_namespace('alg',
                          'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat',
                          'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.

        this_script = doc.agent('alg:' + TEAM_NAME + '#demographicDataCity',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'],
                                 'ont:Extension': 'py'})

        demographicDataTownEntity = doc.entity('dat:' + TEAM_NAME + '#demographicDataTown',
                                                 {prov.model.PROV_LABEL: 'Census Data by Town',
                                                  prov.model.PROV_TYPE: 'ont:DataSet'})


        get_demographicDataCity = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_demographicDataCity, this_script)
        doc.usage(get_demographicDataCity, demographicDataTownEntity, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': 'westfieldcitymassachusetts,pittsfieldcitymassachusetts,agawamtowncitymassachusetts,'
                                'amesburytowncitymassachusetts,attleborocitymassachusetts,'
                                'barnstabletowncitymassachusetts/PST045218'
                   }
                  )

        demographicDataCityEntity = doc.entity('dat:' + TEAM_NAME + '#demographicDataCity', {
            prov.model.PROV_LABEL: 'Demographic Data City - includes city and town',
            prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(demographicDataCityEntity, this_script)
        doc.wasGeneratedBy(demographicDataCityEntity, get_demographicDataCity, endTime)
        doc.wasDerivedFrom(demographicDataTownEntity, get_demographicDataCity, get_demographicDataCity, get_demographicDataCity)

        repo.logout()

        return doc

'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
example.execute()
doc = example.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''
## eof


