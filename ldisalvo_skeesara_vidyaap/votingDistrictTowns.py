"""
CS504 : VotingDistrictTowns
Team : Vidya Akavoor, Lauren DiSalvo, Sreeja Keesara
Description :

Notes : 

March 29, 2019
"""

import datetime
import uuid

import dml
import prov.model

from ldisalvo_skeesara_vidyaap.helper.constants import TEAM_NAME, STATE_SENATE_ELECTIONS_NAME, STATE_SENATE_ELECTIONS_RESULTS_NAME, STATE_HOUSE_ELECTIONS_NAME, STATE_HOUSE_ELECTIONS_RESULTS_NAME, VOTING_DISTRICT_TOWNS, VOTING_DISTRICT_TOWNS_NAME

class votingDistrictTowns(dml.Algorithm):
    contributor = TEAM_NAME
    reads = [STATE_SENATE_ELECTIONS_NAME, STATE_SENATE_ELECTIONS_RESULTS_NAME, STATE_HOUSE_ELECTIONS_NAME, STATE_HOUSE_ELECTIONS_RESULTS_NAME]
    writes = [VOTING_DISTRICT_TOWNS_NAME]

    @staticmethod
    def execute(trial=False):
        """
            Build map of voting district to list of districts in that town
            ex) {
                    "_id" : ObjectId("5c9e373e4e31d23c590d959d"),
                    "Type" : "Senate",
                    "District" : "2nd Middlesex and Norfolk",
                    "Towns" : [ "Ashland", "Framingham", "Franklin", "Holliston", "Hopkinton", "Medway", "Natick" ]
                }
        """
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate(TEAM_NAME, TEAM_NAME)

        # Get list of election ids and district names
        senateDistricts = list(repo[STATE_SENATE_ELECTIONS_NAME].find({}, {"_id": 1, "district": 1}))
        houseDistricts = list(repo[STATE_HOUSE_ELECTIONS_NAME].find({}, {"_id": 1, "district": 1}))

        foundSenateDistricts = []
        foundHouseDistricts = []
        votingDistrictRows = []

        # find all towns in district
        for row in senateDistricts:
            district = row['district']
            if district not in foundSenateDistricts:
                foundSenateDistricts.append(district)
                towns = list(repo[STATE_SENATE_ELECTIONS_RESULTS_NAME].distinct("City/Town", {"Election ID": row['_id'], "City/Town": {"$ne": "TOTALS"}}))

                newRowToInsert = {}
                newRowToInsert['Type'] = 'Senate'
                newRowToInsert['District'] = district
                newRowToInsert['Towns'] = towns

                votingDistrictRows.append(newRowToInsert)

        for row in houseDistricts:
            district = row['district']
            if district not in foundHouseDistricts:
                foundHouseDistricts.append(district)
                towns = list(repo[STATE_HOUSE_ELECTIONS_RESULTS_NAME].distinct("City/Town", {
                    "Election ID": row['_id'], "City/Town": {"$ne": "TOTALS"}}))

                newRowToInsert = {}
                newRowToInsert['Type'] = 'House'
                newRowToInsert['District'] = district
                newRowToInsert['Towns'] = towns

                votingDistrictRows.append(newRowToInsert)

        # Insert rows into collection
        repo.dropCollection(VOTING_DISTRICT_TOWNS)
        repo.createCollection(VOTING_DISTRICT_TOWNS)
        repo[VOTING_DISTRICT_TOWNS_NAME].insert_many(votingDistrictRows)
        repo[VOTING_DISTRICT_TOWNS_NAME].metadata({'complete': True})
        print(repo[VOTING_DISTRICT_TOWNS_NAME].metadata())

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
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.

        this_script = doc.agent('alg:'+TEAM_NAME+'#votingDistrictTowns', {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        stateHouseElectionsEntity = doc.entity('dat:' + TEAM_NAME + '#stateHouseElections', { prov.model.PROV_LABEL: 'MA General State House Elections 2000-2018', prov.model.PROV_TYPE: 'ont:DataSet'})
        stateHouseElectionsResultsEntity = doc.entity('dat:' + TEAM_NAME + '#stateHouseElectionsResults', {prov.model.PROV_LABEL: 'MA General State House Elections Results 2000-2018', prov.model.PROV_TYPE: 'ont:DataSet'})
        stateSenateElectionsEntity = doc.entity('dat:' + TEAM_NAME + '#stateSenateElections', {prov.model.PROV_LABEL: 'MA General State Senate Elections 2000-2018', prov.model.PROV_TYPE: 'ont:DataSet'})
        stateSenateElectionsResultsEntity = doc.entity('dat:' + TEAM_NAME + '#stateSenateElectionsResults', {prov.model.PROV_LABEL: 'MA General State Senate Elections Results 2000-2018', prov.model.PROV_TYPE: 'ont:DataSet'})

        get_votingDistrictTowns = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_votingDistrictTowns, this_script)

        doc.usage(get_votingDistrictTowns, stateHouseElectionsEntity, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Computation',
                   'ont:Query': '.find({}, {"_id": 1, "district": 1})'
                   }
                  )

        doc.usage(get_votingDistrictTowns, stateSenateElectionsEntity, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Computation',
                   'ont:Query': '.find({}, {"_id": 1, "district": 1})'
                   }
                  )

        doc.usage(get_votingDistrictTowns, stateHouseElectionsResultsEntity, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Computation',
                   'ont:Query': ".distinct('City/Town')"
                   }
                  )

        doc.usage(get_votingDistrictTowns, stateSenateElectionsResultsEntity, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Computation',
                   'ont:Query': ".distinct('City/Town')"
                   }
                  )

        voting_district_towns = doc.entity(
            'dat:ldisalvo_skeesara_vidyaap#votingDistrictTowns',
            {prov.model.PROV_LABEL: 'Map of Voting Districts to List of Towns',
             prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(voting_district_towns, this_script)
        doc.wasGeneratedBy(voting_district_towns, get_votingDistrictTowns, endTime)
        doc.wasDerivedFrom(voting_district_towns, stateHouseElectionsEntity,
                           get_votingDistrictTowns, get_votingDistrictTowns,
                           get_votingDistrictTowns)
        doc.wasDerivedFrom(voting_district_towns, stateHouseElectionsResultsEntity,
                           get_votingDistrictTowns, get_votingDistrictTowns,
                           get_votingDistrictTowns)
        doc.wasDerivedFrom(voting_district_towns, stateSenateElectionsEntity,
                           get_votingDistrictTowns, get_votingDistrictTowns,
                           get_votingDistrictTowns)
        doc.wasDerivedFrom(voting_district_towns, stateSenateElectionsResultsEntity,
                           get_votingDistrictTowns, get_votingDistrictTowns,
                           get_votingDistrictTowns)

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