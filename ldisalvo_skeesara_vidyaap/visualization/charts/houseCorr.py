"""
CS504 : houseCorr
Team : Vidya Akavoor, Lauren DiSalvo, Sreeja Keesara
Description :

Notes : 

April 30, 2019
"""

import plotly.graph_objs as go
import pymongo
from plotly import tools

import math


from ldisalvo_skeesara_vidyaap.helper.constants import TEAM_NAME, VOTING_DISTRICT_TOWNS_NAME, DEMOGRAPHIC_HOUSE_CORRELATIONS_NAME

# Set up the database connection.
client = pymongo.MongoClient()
repo = client.repo
repo.authenticate(TEAM_NAME, TEAM_NAME)

senateList = list(repo[VOTING_DISTRICT_TOWNS_NAME].find({"Type": "Senate"}, {"District":1}))
districts = []
for x in senateList:
    districts +=[x["District"]]

### below is setup code for corr figure ###
def getCorr():
    ans = []  # format: [[dem factors, dem values], [rep factors, rep values]]
    for x in range(2):
        party = list(repo[DEMOGRAPHIC_HOUSE_CORRELATIONS_NAME].find())[x]

        temp = []
        dictList = []

        del party['_id']
        del party['Party']

        for key, value in party.items():
            if not math.isnan(value):
                temp = [key, value]
                dictList.append(temp)

        dictList.sort(key = lambda y: y[1], reverse=True)
        dictList = dictList[:5]  # taking top 5 metrics
        val = list(zip(*dictList))
        valList = map(list, val)
        ans += valList
    return ans


correlations = getCorr()
corrDem = correlations[:2]
corrRep = correlations[2:]
DemLabel = [x.split(",")[0] if "spoken at home" not in x else "2+ language at home" for x in corrDem[0]]
DemValue = corrDem[1]
RepLabel = [x.split(",")[0] if "White alone" not in x else x for x in corrRep[0]]
RepValue = corrRep[1]

trace0 = go.Bar(x=DemLabel,
                y=DemValue,
                marker=dict(
                color='rgb(0,0,139)')
                    )

trace1 = go.Bar(x=RepLabel,
                y=RepValue,
                marker=dict(
        color='rgb(139,0,0)')
                    )

fig = tools.make_subplots(rows=1, cols=2, specs=[[{}, {}]], shared_xaxes=True,
                          shared_yaxes=True, vertical_spacing=0.5, horizontal_spacing=.1, subplot_titles=["Democratic Party", "Republican Party"])
fig.append_trace(trace0, 1, 1)
fig.append_trace(trace1, 1, 2)
fig['layout'].update(height=550, width=600, title='Metrics Most Correlated to Political Ideology', showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
fig['layout']['xaxis1'].update(automargin=True, tickfont=dict(
            size=11,
            color='black'
        ), ticks='outside', tickangle=-45)
fig['layout']['xaxis2'].update(automargin=True, tickfont=dict(
            size=11,
            color='black'
        ), ticks='outside', tickangle=-45)

