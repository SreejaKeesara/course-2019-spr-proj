"""
CS504 : demographicData.py
Team : Vidya Akavoor, Lauren DiSalvo, Sreeja Keesara
Description : Transformation of data to create weighted ideology scores for each house district

Notes:

February 28, 2019
"""

import datetime
import uuid

import dml
import prov.model

from ldisalvo_skeesara_vidyaap.helper.constants import TEAM_NAME, STATE_SENATE_ELECTIONS_NAME, STATE_SENATE_ELECTIONS_RESULTS_NAME, HISTORICAL_RATIOS_SENATE_NAME, HISTORICAL_RATIOS_SENATE


class historicalRatiosSenate(dml.Algorithm):
    contributor = TEAM_NAME
    reads = [STATE_SENATE_ELECTIONS_NAME, STATE_SENATE_ELECTIONS_RESULTS_NAME]
    writes = [HISTORICAL_RATIOS_SENATE_NAME]

    @staticmethod
    def execute(trial=False):
        """
            Read from State House Elections and Results tables to find the ratio of Democratic votes to Republican
            in each district for each year

            ex) {
                    "year" : 2017,
                    "15th Suffolk" : .6 (number representing ratio of how Democratic or Republican),
                    "3rd Hampshire" : .3 (number representing ratio of how Democratic or Republican),
                    ...
                }
        """
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate(TEAM_NAME, TEAM_NAME)


        electionsByDistrict = list(repo[STATE_SENATE_ELECTIONS_NAME].find({ "year": { "$gte": 2010 } }))
        ratiosPerYear = {}


        for tup in electionsByDistrict:
            # find the results row that matches the year and district of current tuple
            totalRow = list(repo[STATE_SENATE_ELECTIONS_RESULTS_NAME].find(
                {"City/Town": "TOTALS",
                 "Election ID": tup["_id"]
                 }))[0]


            # find which candidate was the Democrat and which was the Republican
            dem = ""
            rep = ""
            others = []

            for c in tup["candidates"]:
                candidate = c["party"]
                if candidate == "Democratic":
                    dem = c["name"].replace('.','')
                elif candidate == "Republican":
                    rep = c["name"].replace('.','')
                else:
                    others += [c["name"].replace('.', '')]

            # find the ratio of votes that each candidate got

            total_count = totalRow["Total Votes Cast"]
            dem_ratio = 0
            rep_ratio = 0

            if dem != "":
                try:
                    dem_ratio = float(totalRow[dem]/total_count)
                except KeyError:
                    print("NOTE: Democrat not located: ", dem)


            if rep != "":
                try:
                    rep_ratio = float(totalRow[rep]/total_count)
                except KeyError:
                    print("NOTE: Republic not location: ", rep)

            final_ratio = (dem_ratio + (rep_ratio *-1)) / 2


            if tup["year"] in ratiosPerYear:
                ratiosPerYear[tup["year"]] += [(tup["district"], final_ratio)]
            else:
                ratiosPerYear[tup["year"]] = [(tup["district"], final_ratio)]

        # calculate the average over time (using helper) and insert into database
        new_list = []
        for k, vs in ratiosPerYear.items():
            new_json = {}
            new_json["year"] = k
            for v in vs:
                new_json[v[0]] = v[1]
            new_list += [new_json]


        repo.dropCollection(HISTORICAL_RATIOS_SENATE)
        repo.createCollection(HISTORICAL_RATIOS_SENATE_NAME)
        repo[HISTORICAL_RATIOS_SENATE_NAME].insert_many(new_list)
        repo[HISTORICAL_RATIOS_SENATE_NAME].metadata({'complete': True})
        print(repo[HISTORICAL_RATIOS_SENATE_NAME].metadata())


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
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.

        this_script = doc.agent('alg:ldisalvo_skeesara_vidyaap#historicalRatiosSenate',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        stateSenateElectionsEntity = doc.entity('dat:' + TEAM_NAME + '#stateSenateElections',
                                               {prov.model.PROV_LABEL: 'MA General State Senate Elections 2000-2018',
                                                prov.model.PROV_TYPE: 'ont:DataSet'})
        stateSenateElectionsResultsEntity = doc.entity('dat:' + TEAM_NAME + '#stateSenateElectionsResults', {
            prov.model.PROV_LABEL: 'MA General State Senate Elections Results 2000-2018',
            prov.model.PROV_TYPE: 'ont:DataSet'})

        get_historical_ratios_senate = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_historical_ratios_senate, this_script)

        doc.usage(get_historical_ratios_senate, stateSenateElectionsEntity, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Computation',
                   'ont:Query': 'Name'
                   }
                  )
        doc.usage(get_historical_ratios_senate, stateSenateElectionsResultsEntity, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Computation',
                   'ont:Query': 'Election ID'
                   }
                  )

        historical_ratios_senate = doc.entity('dat:ldisalvo_skeesara_vidyaap#historicalRatios',
                          {prov.model.PROV_LABEL: 'Ratio of Democratic to Republican per year', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(historical_ratios_senate, this_script)
        doc.wasGeneratedBy(historical_ratios_senate, get_historical_ratios_senate, endTime)
        doc.wasDerivedFrom(historical_ratios_senate, stateSenateElectionsEntity, get_historical_ratios_senate, get_historical_ratios_senate, get_historical_ratios_senate)
        doc.wasDerivedFrom(historical_ratios_senate, stateSenateElectionsResultsEntity, get_historical_ratios_senate, get_historical_ratios_senate, get_historical_ratios_senate)

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