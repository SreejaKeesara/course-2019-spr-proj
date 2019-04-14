"""
CS504 : canvassingBudgetConstraint
Team : Vidya Akavoor, Lauren DiSalvo, Sreeja Keesara
Description :

Notes : 

April 04, 2019
"""

import datetime
import uuid
import math

import dml
import prov.model
import z3
import re

from ldisalvo_skeesara_vidyaap.helper.constants import TEAM_NAME, VOTING_DISTRICT_TOWNS_NAME, DEMOGRAPHIC_DATA_TOWN_NAME, CANVASSING_BUDGET_CONSTRAINT_NAME, CANVASSING_BUDGET_CONSTRAINT

class canvassingBudgetConstraint(dml.Algorithm):
    contributor = TEAM_NAME
    reads = [VOTING_DISTRICT_TOWNS_NAME, DEMOGRAPHIC_DATA_TOWN_NAME]
    writes = [CANVASSING_BUDGET_CONSTRAINT_NAME]

    @staticmethod
    def execute(trial=False):
        """
            Find which towns that can be canvassed in a given district given
            a budget of the total number of people one can visit

            ex) {
                    "_id" : ObjectId("5cb367bd0a1aef089f1d060a"),
                    "District" : "2nd Middlesex and Norfolk",
                    "Type" : "Senate",
                    "Budget (# of people)" : 100000,
                    "Check" : "sat",
                    "Excluded Towns" : [ ],
                    "Model" : [
                                [ "Ashland", 1 ],
                                [ "Framingham", 1 ],
                                [ "Franklin", 0 ],
                                [ "Holliston", 0 ],
                                [ "Hopkinton", 0 ],
                                [ "Medway", 0 ],
                                [ "Natick", 0 ],
                                [ "popNatick", 36246 ],
                                [ "popMedway", 13329 ],
                                [ "popHopkinton", 18035 ],
                                [ "popHolliston", 14753 ],
                                [ "popFranklin", 32996 ],
                                [ "popFramingham", 72032 ],
                                [ "popAshland", 17706 ]
                            ]
                }
        """
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate(TEAM_NAME, TEAM_NAME)

        # Get full list of voting districts and towns within them (limit 50 if trial flag set)
        if trial:
            votingDistricts = list(repo[VOTING_DISTRICT_TOWNS_NAME].find().limit(50))
        else:
            votingDistricts = list(repo[VOTING_DISTRICT_TOWNS_NAME].find())
        rows = []

        # Iterate through each district to perform the constraint problem:
        # With enough budget to canvass 100,000 people in the district,
        # which towns within that district should I canvass?
        for district in votingDistricts:
            towns = district["Towns"]

            # NOTE: We first need to make sure that demographic data is available for every town in this district.
            #       If not, we remove that town from the constraint variables.

            # Empty list that will eventually hold the populations of each town in the district
            popList = []
            availableTowns = []
            excludedTowns = []

            # Iterate through each town to get population (2017 estimates) if available
            for town in towns:
                townDemo = list(repo[DEMOGRAPHIC_DATA_TOWN_NAME].find({"Town": re.compile("^" + town + "")}))
                if townDemo and not math.isnan(townDemo[0]["Population estimates, July 1, 2017,  (V2017)"]):
                    popList.append(townDemo[0]["Population estimates, July 1, 2017,  (V2017)"])
                    availableTowns.append(town)
                else:
                    excludedTowns.append(town)

            # Set up z3 variables for towns (0,1) and their populations
            numTowns = len(availableTowns)
            xs = [z3.Real(availableTowns[i]) for i in range(numTowns)]
            ps = [z3.Real('pop' + availableTowns[i]) for i in range(numTowns)]

            S = z3.Solver()

            # Add the constraints saying what each town's population is and whether we visit that town (1) or not (0)
            for i in range(numTowns):
                S.add(ps[i] == popList[i])
                S.add(z3.Or(xs[i] == 1, xs[i] == 0))

            # Add constraint that total number of people visited must not exceed the budget (100,000 people)
            totalPeopleVisited = sum([xs[j] * ps[j] for j in range(numTowns)])
            S.add(totalPeopleVisited <= 100000)

            # Build row to insert
            row = {}
            row["District"] = district["District"]
            row["Type"] = district["Type"]
            row["Budget (# of people)"] = 100000
            row["Check"] = str(S.check())
            row["Excluded Towns"] = excludedTowns

            if str(S.check()) == "sat":
                model = S.model()
                row["Model"] = [(str(d), int(str(model[d]))) for d in model]

            rows.append(row)

        # Insert rows into collection
        repo.dropCollection(CANVASSING_BUDGET_CONSTRAINT)
        repo.createCollection(CANVASSING_BUDGET_CONSTRAINT)
        repo[CANVASSING_BUDGET_CONSTRAINT_NAME].insert_many(rows)
        repo[CANVASSING_BUDGET_CONSTRAINT_NAME].metadata({'complete': True})
        print(repo[CANVASSING_BUDGET_CONSTRAINT_NAME].metadata())

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

        this_script = doc.agent('alg:ldisalvo_skeesara_vidyaap#canvassingBudgetConstraint',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        voting_district_towns = doc.entity('dat:' + TEAM_NAME + '#votingDistrictTowns', {
            prov.model.PROV_LABEL: 'Map of Voting Districts to List of Towns',
            prov.model.PROV_TYPE: 'ont:DataSet'})

        demographicDataTownEntity = doc.entity('dat:' + TEAM_NAME + '#demographicDataTown', {
            prov.model.PROV_LABEL: 'Census Data by Town, Massachusetts',
            prov.model.PROV_TYPE: 'ont:DataSet'})

        get_canvassing_constraint = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_canvassing_constraint, this_script)

        doc.usage(get_canvassing_constraint, voting_district_towns, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Computation',
                   'ont:Query': 'Name'
                   }
                  )
        doc.usage(get_canvassing_constraint, demographicDataTownEntity, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Computation',
                   'ont:Query': 'Election ID'
                   }
                  )

        canvassingBudgetConstraint = doc.entity('dat:' + TEAM_NAME + '#canvassingBudgetConstraint',
                          {prov.model.PROV_LABEL: 'Determines towns to canvass based on budget and population for each voting district', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(canvassingBudgetConstraint, this_script)
        doc.wasGeneratedBy(canvassingBudgetConstraint, get_canvassing_constraint, endTime)
        doc.wasDerivedFrom(canvassingBudgetConstraint, demographicDataTownEntity, get_canvassing_constraint, get_canvassing_constraint, get_canvassing_constraint)
        doc.wasDerivedFrom(canvassingBudgetConstraint, voting_district_towns, get_canvassing_constraint, get_canvassing_constraint, get_canvassing_constraint)

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