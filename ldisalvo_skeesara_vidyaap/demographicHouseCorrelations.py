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

from scipy import stats

from ldisalvo_skeesara_vidyaap.helper.constants import TEAM_NAME, \
    DEMOGRAPHIC_DATA_DISTRICT_HOUSE_NAME, WEIGHTED_HOUSE_IDEOLOGIES_NAME, DEMOGRAPHIC_HOUSE_CORRELATIONS, \
    DEMOGRAPHIC_HOUSE_CORRELATIONS_NAME


class demographicHouseCorrelations(dml.Algorithm):
    contributor = TEAM_NAME
    reads = [DEMOGRAPHIC_DATA_DISTRICT_HOUSE_NAME, WEIGHTED_HOUSE_IDEOLOGIES_NAME]
    writes = [DEMOGRAPHIC_HOUSE_CORRELATIONS_NAME]

    @staticmethod
    def execute(trial=False):
        """
            Read from Demographic Data District Senate and Weighted Senate Ideologies tables to find correlation between
            Democratic percentage and each demographic data point, and the correlation between Republican percentage
            and each demographic point
            Democrat table: ex) {
                    "District" : "1st Hampden and Hampshire",
                    "Corr_Population estimates, July 1, 2017,  (V2017)": #,
                    "Corr_Population estimates base, April 1, 2010,  (V2017)": #
                    ...
                }

            Republican table: ex) {
                    "District" : "1st Hampden and Hampshire",
                    "Corr_Population estimates, July 1, 2017,  (V2017)": #,
                    "Corr_Population estimates base, April 1, 2010,  (V2017)": #
                    ...
                }
        """
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate(TEAM_NAME, TEAM_NAME)


        demographicHouse = list(repo[DEMOGRAPHIC_DATA_DISTRICT_HOUSE_NAME].find({}))
        # empty dictionaries to be of the form {stat_name: [[ideology ratio],[stat]], stat_name:[[],[]], ...}
        pointsDem = {}
        pointsRep = {}


        for tup in demographicHouse:
            # find the row in weighted senate ideologies for this district to get the ratios
            ratios = list(repo[WEIGHTED_HOUSE_IDEOLOGIES_NAME].find(
                {"district":tup["House District"]
                 }))

            if len(ratios) != 0:
                # get the ratio of how Democratic or Republican this district is
                dem_ratio = ratios[0]["Democratic ratio"]
                rep_ratio = ratios[0]["Republican ratio"]

            # go through all the stats for this district and add to individual lists to
            # later make points of the form (ratio, stat)
            for key in tup:
                if key != "House District" and key != "_id":
                    # add the (ratio, stat) point for the current stat for this district to the Democratic points list
                    if key in pointsDem:
                        pointsDem[key][0] += [dem_ratio]
                        pointsDem[key][1] += [tup[key]]
                    else:
                        pointsDem[key] = [[dem_ratio], [tup[key]]]

                    # add the (ratio, stat) point for the current stat for this district to the Republican points list
                    if key in pointsRep:
                        pointsRep[key][0] += [rep_ratio]
                        pointsRep[key][1] += [tup[key]]
                    else:
                        pointsRep[key] = [[rep_ratio], [tup[key]]]

        # empty dictionaries that will eventually be of the form {stat_name: correlation, stat_name: correlation, ...}
        corrs_dem = {"Party": "Democratic"}
        corrs_rep = {"Party": "Republican"}

        # go through the points with the Democratic ratios and find the correlation for each stat
        for key in pointsDem:
            all_ratios = pointsDem[key][0]
            all_stats = pointsDem[key][1]

            corr = stats.pearsonr(all_ratios, all_stats)[0]
            corrs_dem[key] = corr

        # go through the points with the Republican ratios and find the correlation for each stat
        for key in pointsRep:
            all_ratios = pointsRep[key][0]
            all_stats = pointsRep[key][1]

            corr = stats.pearsonr(all_ratios, all_stats)[0]
            corrs_rep[key] = corr


        total_corrs = [corrs_dem, corrs_rep]


        # create database for the correlations
        repo.dropCollection(DEMOGRAPHIC_HOUSE_CORRELATIONS)
        repo.createCollection(DEMOGRAPHIC_HOUSE_CORRELATIONS_NAME)
        repo[DEMOGRAPHIC_HOUSE_CORRELATIONS_NAME].insert_many(total_corrs)
        repo[DEMOGRAPHIC_HOUSE_CORRELATIONS_NAME].metadata({'complete': True})
        print(repo[DEMOGRAPHIC_HOUSE_CORRELATIONS_NAME].metadata())

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

        this_script = doc.agent('alg:ldisalvo_skeesara_vidyaap#demographicHouseCorrelations',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        demographicHouseDataEntity = doc.entity('dat:' + TEAM_NAME + '#demographicDataDistrictHouse',
                                               {prov.model.PROV_LABEL: '2017 Census Data by District for State House',
                                                prov.model.PROV_TYPE: 'ont:DataSet'})
        weightedHouseIdeologyEntity = doc.entity('dat:' + TEAM_NAME + '#transformationWeightedHouseIdeology', {
            prov.model.PROV_LABEL: 'State House voting patterns',
            prov.model.PROV_TYPE: 'ont:DataSet'})

        get_house_correlations = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_house_correlations, this_script)

        doc.usage(get_house_correlations, demographicHouseDataEntity, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Computation',
                   'ont:Query': 'Name'
                   }
                  )
        doc.usage(get_house_correlations, weightedHouseIdeologyEntity, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Computation',
                   'ont:Query': 'Election ID'
                   }
                  )

        house_correlations = doc.entity('dat:ldisalvo_skeesara_vidyaap#demographicSenateCorrelations',
                          {prov.model.PROV_LABEL: 'Correlations between Census data and Senate voting patterns', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(house_correlations, this_script)
        doc.wasGeneratedBy(house_correlations, get_house_correlations, endTime)
        doc.wasDerivedFrom(house_correlations, demographicHouseDataEntity, get_house_correlations, get_house_correlations, get_house_correlations)
        doc.wasDerivedFrom(house_correlations, weightedHouseIdeologyEntity, get_house_correlations, get_house_correlations, get_house_correlations)

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