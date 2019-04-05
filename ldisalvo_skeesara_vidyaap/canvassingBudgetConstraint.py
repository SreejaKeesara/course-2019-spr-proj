"""
CS504 : canvassingBudgetConstraint
Team : Vidya Akavoor, Lauren DiSalvo, Sreeja Keesara
Description :

Notes : 

April 04, 2019
"""

import datetime
import uuid

import dml
import prov.model
import z3
import re

from ldisalvo_skeesara_vidyaap.helper.constants import TEAM_NAME, VOTING_DISTRICT_TOWNS_NAME, DEMOGRAPHIC_DATA_TOWN_NAME

class canvassingBudgetConstraint(dml.Algorithm):
    contributor = TEAM_NAME
    reads = [VOTING_DISTRICT_TOWNS_NAME, DEMOGRAPHIC_DATA_TOWN_NAME]
    writes = []

    @staticmethod
    def execute(trial=False):
        """
        Find which towns one can visit in a given district given a budget of the total number of people one can visit

        """
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate(TEAM_NAME, TEAM_NAME)

        # Input district that we are looking for and get towns within that district
        targetDistrict = "9th Norfolk"
        votingDistrictData = list(repo[VOTING_DISTRICT_TOWNS_NAME].find({"District": targetDistrict}))[0]

        # list of towns in district "targetDistrict"
        towns = votingDistrictData["Towns"]

        # set up z3 variables for towns (0,1) and their populations
        # NOTE: we have hard coded six variables because we are assuming that we will know which district
        #       we are looking at in advance. In this case it is "9th Norfolk"
        (x1, x2, x3, x4, x5, x6) = [z3.Real('x' + str(i)) for i in range(1, 7)]
        (p1, p2, p3, p4, p5, p6) = [z3.Real('p' + str(i)) for i in range(1, 7)]
        S = z3.Solver()

        # empty list that will eventually hold the populations of each town in the district
        popList = []

        for town in towns:
            townDemo = list(repo[DEMOGRAPHIC_DATA_TOWN_NAME].find({"Town": re.compile("^" + town + "")}))
            if townDemo:
                popList.append(townDemo[0]["Population estimates, July 1, 2017,  (V2017)"])

        # add the constraints saying what each town's population is
        S.add(p1 == popList[0])
        S.add(p2 == popList[1])
        S.add(p3 == popList[2])
        S.add(p4 == popList[3])
        S.add(p5 == popList[4])
        S.add(p6 == popList[5])

        # add constraints saying that the "town" variables (x1-x6) must be either 0 or 1
        # this represents whether we visit the town (1) or not (0)
        for x in (x1, x2, x3, x4, x5, x6):
            S.add(z3.Or(x ==1, x == 0))
            # S.add(z3.And(x >= 0, x <= 1))

        # add the constraint that says that the total number of people visited must not exceed the budget
        # in this case 50,000 people
        S.add(p1*x1 + p2*x2 + p3*x3 + p4*x4 + p5*x5 + p6*x6 <= 50000)

        print(S.check())
        print(S.model())

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
        votingDistrictTownEntity = doc.entity('dat:' + TEAM_NAME + '#votingDistrictTowns',
                                               {prov.model.PROV_LABEL: 'The towns in each voting district',
                                                prov.model.PROV_TYPE: 'ont:DataSet'})
        demographicDataTownEntity = doc.entity('dat:' + TEAM_NAME + '#demographicDataTown', {
            prov.model.PROV_LABEL: '2017 Census data from each town in MA',
            prov.model.PROV_TYPE: 'ont:DataSet'})

        get_canvassing_constraint = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_canvassing_constraint, this_script)

        doc.usage(get_canvassing_constraint, votingDistrictTownEntity, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Computation',
                   'ont:Query': 'Name'
                   }
                  )
        doc.usage(get_canvassing_constraint, demographicDataTownEntity, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Computation',
                   'ont:Query': 'Election ID'
                   }
                  )

        # house_correlations = doc.entity('dat:ldisalvo_skeesara_vidyaap#demographicSenateCorrelations',
        #                   {prov.model.PROV_LABEL: 'Correlations between Census data and Senate voting patterns', prov.model.PROV_TYPE: 'ont:DataSet'})
        # doc.wasAttributedTo(house_correlations, this_script)
        # doc.wasGeneratedBy(house_correlations, get_house_correlations, endTime)
        # doc.wasDerivedFrom(house_correlations, demographicHouseDataEntity, get_house_correlations, get_house_correlations, get_house_correlations)
        # doc.wasDerivedFrom(house_correlations, weightedHouseIdeologyEntity, get_house_correlations, get_house_correlations, get_house_correlations)
        #
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
canvassingBudgetConstraint.execute()
## eof