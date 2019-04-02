"""
CS504 : demographicDataDistrictSenate.py
Team : Vidya Akavoor, Lauren DiSalvo, Sreeja Keesara
Description : Retrieval of demographic data by district


March 29, 2019
"""

import datetime
import uuid
import re

import dml
import prov.model
import bson

from ldisalvo_skeesara_vidyaap.helper.constants import TEAM_NAME, \
    VOTING_DISTRICT_TOWNS_NAME, DEMOGRAPHIC_DATA_DISTRICT_SENATE_NAME, DEMOGRAPHIC_DATA_TOWN_NAME


class demographicDataDistrictSenate(dml.Algorithm):
    contributor = TEAM_NAME
    reads = [VOTING_DISTRICT_TOWNS_NAME]
    writes = [DEMOGRAPHIC_DATA_DISTRICT_SENATE_NAME]

    @staticmethod

    #TODO: Fix comment here
    def execute(trial=False):
        """

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
        records = []
        for record in senate:
            district = record.get("District")
            towns = record.get("Towns")
            type = record.get("Type")

            # Debugging Comments
            # print("TYPE: ", type, " DISTRICT: ", district, " AND TOWNS: ", towns)
            # print("TOTAL: ", len(towns))

            townList = ""

            for town in towns:
                town = "^" + town + ""
                townList += town + "|"

            townList = townList[:-1]


            doc2 = repo[DEMOGRAPHIC_DATA_TOWN_NAME].aggregate(
                [{"$match": {"Town" : re.compile(townList)}},
                 {"$group":{
                    "_id": bson.objectid.ObjectId(),
                    "Population estimates, July 1, 2017,  (V2017)": {"$avg" : "$Population estimates, July 1, 2017,  (V2017)"},
                    "Population estimates base, April 1, 2010,  (V2017)": {"$avg" : "$Population estimates base, April 1, 2010,  (V2017)"},
                    "Population, Census, April 1, 2010": {"$avg" : "$Population, Census, April 1, 2010"},
                    "Persons under 5 years, percent": {"$avg": "$Persons under 5 years, percent"},
                    "Persons under 18 years, percent": {"$avg": "$Persons under 18 years, percent"},
                    "Persons 65 years and over, percent": {"$avg": "$Persons 65 years and over, percent"},
                    "Female persons, percent": {"$avg": "$Female persons, percent"},
                    "White alone, percent": {"$avg": "$White alone, percent"},
                    "Black or African American alone, percent": {"$avg": "$Black or African American alone, percent"},
                    "American Indian and Alaska Native alone, percent": {"$avg": "$American Indian and Alaska Native alone, percent"},
                    "Asian alone, percent": {"$avg": "$Asian alone, percent"},
                    "Native Hawaiian and Other Pacific Islander alone, percent": {"$avg": "$Native Hawaiian and Other Pacific Islander alone, percent"},
                    "Two or More Races, percent": {"$avg": "$Two or More Races, percent"},
                    "Hispanic or Latino, percent": {"$avg": "$Hispanic or Latino, percent"},
                    "White alone, not Hispanic or Latino, percent": {"$avg": "$White alone, not Hispanic or Latino, percent"},
                    "Veterans, 2013-2017": {"$avg": "$Veterans, 2013-2017"},
                    "Foreign born persons, percent, 2013-2017": {"$avg": "$Foreign born persons, percent, 2013-2017"},
                    "Owner-occupied housing unit rate, 2013-2017": {"$avg": "$Owner-occupied housing unit rate, 2013-2017"},
                    "Median value of owner-occupied housing units, 2013-2017": {"$avg": "$Median value of owner-occupied housing units, 2013-2017"},
                    "Median selected monthly owner costs -with a mortgage, 2013-2017": {"$avg": "$Median selected monthly owner costs -with a mortgage, 2013-2017"},
                    "Median selected monthly owner costs -without a mortgage, 2013-2017": {"$avg": "$Median selected monthly owner costs -without a mortgage, 2013-2017"},
                    "Median gross rent, 2013-2017": {"$avg": "$Median gross rent, 2013-2017"},
                    "Households, 2013-2017": {"$avg": "$Households, 2013-2017"},
                    "Persons per household, 2013-2017": {"$avg": "$Persons per household, 2013-2017"},
                    "Living in same house 1 year ago, percent of persons age 1 year+, 2013-2017": {"$avg": "$Living in same house 1 year ago, percent of persons age 1 year+, 2013-2017"},
                    "Language other than English spoken at home, percent of persons age 5 years+, 2013-2017": {"$avg": "$Language other than English spoken at home, percent of persons age 5 years+, 2013-2017"},
                    "Households with a computer, percent, 2013-2017": {"$avg": "$Households with a computer, percent, 2013-2017"},
                    "Households with a broadband Internet subscription, percent, 2013-2017": {"$avg": "$Households with a broadband Internet subscription, percent, 2013-2017"},
                    "High school graduate or higher, percent of persons age 25 years+, 2013-2017": {"$avg": "$High school graduate or higher, percent of persons age 25 years+, 2013-2017"},
                    "Bachelor's degree or higher, percent of persons age 25 years+, 2013-2017": {"$avg": "$Bachelor's degree or higher, percent of persons age 25 years+, 2013-2017"},
                    "With a disability, under age 65 years, percent, 2013-2017": {"$avg": "$With a disability, under age 65 years, percent, 2013-2017"},
                    "Persons  without health insurance, under age 65 years, percent": {"$avg": "$Persons  without health insurance, under age 65 years, percent"},
                    "In civilian labor force, total, percent of population age 16 years+, 2013-2017": {"$avg": "$In civilian labor force, total, percent of population age 16 years+, 2013-2017"},
                    "In civilian labor force, female, percent of population age 16 years+, 2013-2017": {"$avg": "$In civilian labor force, female, percent of population age 16 years+, 2013-2017"},
                    "Total accommodation and food services sales, 2012 ($1,000)": {"$avg": "$Total accommodation and food services sales, 2012 ($1,000)"},
                    "Total health care and social assistance receipts/revenue, 2012 ($1,000)": {"$avg": "$Total health care and social assistance receipts/revenue, 2012 ($1,000)"},
                    "Total manufacturers shipments, 2012 ($1,000)": {"$avg": "$Total manufacturers shipments, 2012 ($1,000)"},
                    "Total retail sales, 2012 ($1,000)": {"$avg": "$Total retail sales, 2012 ($1,000)"},
                    "Total retail sales per capita, 2012": {"$avg": "$Total retail sales per capita, 2012"},
                    "Mean travel time to work (minutes), workers age 16 years+, 2013-2017": {"$avg": "$Mean travel time to work (minutes), workers age 16 years+, 2013-2017"},
                    "Median household income (in 2017 dollars), 2013-2017": {"$avg": "$Median household income (in 2017 dollars), 2013-2017"},
                    "Per capita income in past 12 months (in 2017 dollars), 2013-2017": {"$avg": "$Per capita income in past 12 months (in 2017 dollars), 2013-2017"},
                    "Persons in poverty, percent": {"$avg": "$Persons in poverty, percent"},
                    "Total employer establishments, 2016": {"$avg": "$Total employer establishments, 2016"},
                    "Total employment, 2016": {"$avg": "$Total employment, 2016"},
                    "Total annual payroll, 2016 ($1,000)": {"$avg": "$Total annual payroll, 2016 ($1,000)"},
                    "Total employment, percent change, 2015-2016": {"$avg": "$Total employment, percent change, 2015-2016"},
                    "Total nonemployer establishments, 2016": {"$avg": "$Total nonemployer establishments, 2016"},
                    "All firms, 2012": {"$avg": "$All firms, 2012"},
                    "Men-owned firms, 2012": {"$avg": "$Men-owned firms, 2012"},
                    "Women-owned firms, 2012": {"$avg": "$Women-owned firms, 2012"},
                    "Minority-owned firms, 2012": {"$avg": "$Minority-owned firms, 2012"},
                    "Nonminority-owned firms, 2012": {"$avg": "$Nonminority-owned firms, 2012"},
                    "Veteran-owned firms, 2012": {"$avg": "$Veteran-owned firms, 2012"},
                    "Nonveteran-owned firms, 2012": {"$avg": "$Nonveteran-owned firms, 2012"},
                    "Population per square mile, 2010": {"$avg": "$Population per square mile, 2010"},
                    "Land area in square miles, 2010": {"$avg": "$Land area in square miles, 2010"},
                    "Housing units,  July 1, 2017,  (V2017)": {"$avg": "$Housing units,  July 1, 2017,  (V2017)"},
                    "Building permits, 2017": {"$avg": "$Building permits, 2017"},
                    "Total merchant wholesaler sales, 2012 ($1,000)": {"$avg": "$Total merchant wholesaler sales, 2012 ($1,000)"},

                 }
            }])

            res = []
            for doc in doc2:
                doc["Senate District"] = district
                res += [doc]
            records += res

            # Debugging Comments
            # doc = repo[DEMOGRAPHIC_DATA_TOWN_NAME].find({"Town" : re.compile(townList)}).count()
            # print("TOWN ABLE TO RETRIEVE: ", doc)
            #
            # doc2 = repo[DEMOGRAPHIC_DATA_TOWN_NAME].find({"Town" : re.compile(townList)})
            # to = []
            # for t in doc2:
            #     town = t.get("Town")
            #     to += [town]
            # print("TOWNS RETRIEVED: ", to)

        # Insert rows into collection
        repo.dropCollection(DEMOGRAPHIC_DATA_DISTRICT_SENATE_NAME)
        repo.createCollection(DEMOGRAPHIC_DATA_DISTRICT_SENATE_NAME)
        repo[DEMOGRAPHIC_DATA_DISTRICT_SENATE_NAME].insert_many(records)
        repo[DEMOGRAPHIC_DATA_DISTRICT_SENATE_NAME].metadata({'complete': True})
        print(repo[DEMOGRAPHIC_DATA_DISTRICT_SENATE_NAME].metadata())

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start": startTime, "end": endTime}

    #TODO: Fix comment here
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



