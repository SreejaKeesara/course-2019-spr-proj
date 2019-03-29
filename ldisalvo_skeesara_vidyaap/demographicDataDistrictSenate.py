"""
CS504 : demographicDataDistrict.py
Team : Vidya Akavoor, Lauren DiSalvo, Sreeja Keesara
Description : Retrieval of demographic data by district


March 29, 2019
"""

import datetime
import uuid

import dml
import pandas as pd
import prov.model
import urllib.request

from ldisalvo_skeesara_vidyaap.helper.constants import TEAM_NAME, COUNTY_URL, MA_COUNTY_LIST, DEMOGRAPHIC_DATA_COUNTY, \
    DEMOGRAPHIC_DATA_COUNTY_NAME, VOTING_DISTRICT_TOWNS_NAME, DEMOGRAPHIC_DATA_DISTRICT_SENATE_NAME, DEMOGRAPHIC_DATA_TOWN_NAME


class demographicDataDistrictSenate(dml.Algorithm):
    contributor = TEAM_NAME
    reads = [VOTING_DISTRICT_TOWNS_NAME]
    writes = [DEMOGRAPHIC_DATA_DISTRICT_SENATE_NAME]

    @staticmethod
    def execute(trial=False):
        """
        TODO: FIX THIS DESCRIPTION JSON!!!
            Retrieve average demographic data by Senate district and insert into collection
            ex)
             { "Barnstable County, Massachusetts":
                "Population estimates, July 1, 2017,  (V2017)": "213,444",
                "Population estimates base, April 1, 2010,  (V2017)": "215,868",
                "Population, percent change - April 1, 2010 (estimates base) to July 1, 2017,  (V2017)": "-1.1%",
                "Population, Census, April 1, 2010": "215,888",
                "Persons under 5 years, percent": "3.6%",
                "Persons under 18 years, percent": "15.1%",
                ..........................
            }
        """
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate(TEAM_NAME, TEAM_NAME)

        # Retrieve facts as keys
        document = repo[VOTING_DISTRICT_TOWNS_NAME].find_one()
        keys = []
        for key in document:
            keys += [key]

        # Retrieve keys District (name), Towns (list)
        keys = keys[1:]

        # Retrieve towns associated with each senate district

        # Filter by senate
        senate = repo[VOTING_DISTRICT_TOWNS_NAME].find({"Type" : "Senate"})
        for record in senate:
            district = record.get("District")
            towns = record.get("Towns")

            townList = []
            for town in towns:
                town = "/^" + town + "/"
                townList += [town]

            doc = repo[DEMOGRAPHIC_DATA_TOWN_NAME].find({"Town" : {"$in:" [townList]}}).aggregate()




        keys = []
        for key in document:
            keys += [key]


        # Insert rows into collection
        repo.dropCollection(DEMOGRAPHIC_DATA_DISTRICT_SENATE_NAME)
        repo.createCollection(DEMOGRAPHIC_DATA_DISTRICT_SENATE_NAME)
        repo[DEMOGRAPHIC_DATA_DISTRICT_SENATE_NAME].insert_many(records)
        repo[DEMOGRAPHIC_DATA_DISTRICT_SENATE_NAME].metadata({'complete': True})
        print(repo[DEMOGRAPHIC_DATA_DISTRICT_SENATE_NAME].metadata())

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
        doc.add_namespace('census', 'https://www.census.gov/quickfacts/fact/csv/')

        this_script = doc.agent('alg:'+TEAM_NAME+'#demographicDataCounty',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'],
                                 'ont:Extension': 'py'})
        resource = doc.entity('census:table/ma/', {'prov:label': 'Census Data by County, Massachusetts',
                                                prov.model.PROV_TYPE: 'ont:DataResource',
                                                'ont:Extension': 'csv'})
        get_demographicDataCounty = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_demographicDataCounty, this_script)
        doc.usage(get_demographicDataCounty, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': 'worcestercountymassachusetts,hampdencountymassachusetts,hampshirecountymassachusetts,'
                                'franklincountymassachusetts,berkshirecountymassachusetts,ma/PST045218'
                   }
                  )

        demographicDataCountyEntity = doc.entity('dat:'+TEAM_NAME+'#demographicDataCounty', {prov.model.PROV_LABEL: 'Census Data by County, Massachusetts',
                                                 prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(demographicDataCountyEntity, this_script)
        doc.wasGeneratedBy(demographicDataCountyEntity, get_demographicDataCounty, endTime)
        doc.wasDerivedFrom(demographicDataCountyEntity, resource, get_demographicDataCounty, get_demographicDataCounty, get_demographicDataCounty)

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


