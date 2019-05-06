import pymongo
from ldisalvo_skeesara_vidyaap.helper.constants import TEAM_NAME, \
    DEMOGRAPHIC_DATA_DISTRICT_SENATE_NAME, DEMOGRAPHIC_DATA_DISTRICT_HOUSE_NAME, SENATE_KEY, HOUSE_KEY

# Set up the database connection.
client = pymongo.MongoClient()
repo = client.repo
repo.authenticate(TEAM_NAME, TEAM_NAME)

## below is setup code for race ##
race = ['White', 'Black or African American', 'American Indian and Alaska Native', 'Asian', 'Native Hawaiian and Other Pacific Islander', 'Hispanic or Latino']

def getValues(district, districtType):
    if districtType == SENATE_KEY:
        val = list(repo[DEMOGRAPHIC_DATA_DISTRICT_SENATE_NAME].find({"Senate District": district}, {"White alone, percent": 1,
                                                                     "Black or African American alone, percent":1,
                                                                     "American Indian and Alaska Native alone, percent":1,
                                                                     "Asian alone, percent":1,
                                                                     "Native Hawaiian and Other Pacific Islander alone, percent":1,
                                                                     "Hispanic or Latino, percent":1}))
    elif districtType == HOUSE_KEY:
        val = list(repo[DEMOGRAPHIC_DATA_DISTRICT_HOUSE_NAME].find({"House District": district},
                                                                    {"White alone, percent": 1,
                                                                     "Black or African American alone, percent": 1,
                                                                     "American Indian and Alaska Native alone, percent": 1,
                                                                     "Asian alone, percent": 1,
                                                                     "Native Hawaiian and Other Pacific Islander alone, percent": 1,
                                                                     "Hispanic or Latino, percent": 1}))
    finVal = list(val[0].values())[1:]
    return finVal