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
        """
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate(TEAM_NAME, TEAM_NAME)

        # Get demographic data by voting district
        # votingDistrictData = list(repo[VOTING_DISTRICT_TOWNS_NAME].find())
        #
        # for district in votingDistrictData:
        #     towns = district["Towns"]
        #     townPopDict = {}


        towns = [ "Ashland", "Framingham", "Holliston", "Hopkinton", "Medway", "Natick" ]
        (x1, x2, x3, x4, x5, x6) = [z3.Real('x' + str(i)) for i in range(1, 7)]
        (p1, p2, p3, p4, p5, p6) = [z3.Real('p' + str(i)) for i in range(1, 7)]
        S = z3.Solver()

        popList = []

        for town in towns:
            townDemo = list(repo[DEMOGRAPHIC_DATA_TOWN_NAME].find({"Town": re.compile("^" + town + "")}))
            if townDemo:
                popList.append(townDemo[0]["Population estimates, July 1, 2017,  (V2017)"])

        S.add(p1 == popList[0])
        S.add(p2 == popList[1])
        S.add(p3 == popList[2])
        S.add(p4 == popList[3])
        S.add(p5 == popList[4])
        S.add(p6 == popList[5])

        for x in (x1, x2, x3, x4, x5, x6):
            S.add(z3.Or(x ==1, x == 0))
            # S.add(z3.And(x >= 0, x <= 1))

        S.add(p1*x1 + p2*x2 + p3*x3 + p4*x4 + p5*x5 + p6*x6 <= 100000)

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
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('electionstats', 'http://electionstats.state.ma.us/')

        this_script = doc.agent('alg:'+TEAM_NAME+'#ballotQuestions', {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('electionstats:ballot_questions/search/', {'prov:label': 'PD43+: Election Stats', prov.model.PROV_TYPE: 'ont:DataResource', 'ont:Extension': 'html'})
        get_ballotQuestions = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_ballotQuestions, this_script)
        doc.usage(get_ballotQuestions, resource, startTime, None, {prov.model.PROV_TYPE: 'ont:Retrieval', 'ont:Query': 'year_from:2000/year_to:2018'})

        ballotQuestionsEntity = doc.entity('dat:'+TEAM_NAME+'#ballotQuestions', {prov.model.PROV_LABEL: 'MA Ballot Questions 2000-2018', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(ballotQuestionsEntity, this_script)
        doc.wasGeneratedBy(ballotQuestionsEntity, get_ballotQuestions, endTime)
        doc.wasDerivedFrom(ballotQuestionsEntity, resource, get_ballotQuestions, get_ballotQuestions, get_ballotQuestions)

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