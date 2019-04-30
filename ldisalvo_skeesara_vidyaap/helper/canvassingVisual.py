import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pymongo
import math
import z3
import re
from dash.dependencies import Input, Output, State
from ldisalvo_skeesara_vidyaap.helper.constants import TEAM_NAME, DEMOGRAPHIC_DATA_TOWN_NAME, VOTING_DISTRICT_TOWNS_NAME


# Set up the database connection.
client = pymongo.MongoClient()
repo = client.repo
repo.authenticate(TEAM_NAME, TEAM_NAME)


# populate the District drop down menu
senateList = list(repo[VOTING_DISTRICT_TOWNS_NAME].find({"Type": "Senate"}, {"District":1}))
districts = []
for x in senateList:
    districts +=[x["District"]]



# Get full list of voting districts and towns within them (limit 50 if trial flag set)
votingDistricts = list(repo[VOTING_DISTRICT_TOWNS_NAME].find(
    {"Type": "Senate", "District":"Berkshire, Hampshire and Franklin"},
    {"Towns":1}))
# With enough budget to canvass 100,000 people in the district,
# which towns within that district should I canvass?

# Empty list that will eventually hold the populations of each town in the district
popList = []
availableTowns = []
excludedTowns = []

percent_tup = [0, 0]

for district in votingDistricts:
    towns = district["Towns"]

    # NOTE: We first need to make sure that demographic data is available for every town in this district.
    #       If not, we remove that town from the constraint variables.

    # Iterate through each town to get population (2017 estimates) if available
    for town in towns:
        townDemo = list(repo[DEMOGRAPHIC_DATA_TOWN_NAME].find({"Town": re.compile("^" + town + "")}))
        if townDemo and not math.isnan(townDemo[0]["Population, Census, April 1, 2010"]):
            popList.append(townDemo[0]["Population, Census, April 1, 2010"])
            availableTowns.append(town)
        else:
            excludedTowns.append(town)

percent_tup[1] = len(availableTowns)

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

vals = []
if str(S.check()) == "sat":
    model = S.model()
    vals = [(str(d), int(str(model[d]))) for d in model]

towns = []
if len(vals) != 0:
    for i in range(len(vals)):
        if vals[i][1] == 1:
            towns += [vals[i][0]]

percent_tup[0] = len(towns)
percent = percent_tup[0]/percent_tup[1]

string = ""
if len(towns) != 0:
    for town in towns[:-1]:
        string += town + ", "
    string += towns[-1]


######### GAUGE CHART #########
fig = go.Figure()
fig.add_barpolar(r = [1, 1, 1, 1, 1],
                 theta = [0, 36, 72, 108, 144],
                 showlegend=False,
                 offset=0,
                 width=36,
                 ids=["-","0", "20", "40", "60", "80", "100"],
                 marker={'color': ["rgb(71, 36, 107)", "rgb(108, 73, 139)", "rgb(145, 110, 171)",  "rgb(182, 147, 203)", "rgb(220, 185, 236)"]})

# Configure polar 1
fig.layout.title = "Percent of Towns Visited"
fig.layout.polar.hole = 0.4
fig.layout.polar.angularaxis.showgrid = False
fig.layout.polar.radialaxis.showgrid = False
fig.layout.polar.radialaxis.range = [0, 1]
fig.layout.polar.radialaxis.tickvals = []
fig.layout.polar.angularaxis.tickvals = [0, 36, 72, 108, 144, 180]
fig.layout.polar.angularaxis.ticktext = [100, 80, 60, 40, 20, 0]
fig.layout.polar.bargap = 0.9
fig.layout.polar.sector = [0, 180]
fig.layout.polar.domain.x = [0, 1]

needle = fig.add_scatterpolar(r=[1, 0, 0, 1],
                              theta=[0, -20, 20, 0],
                              showlegend=False,
                              fill='tonext',
                              mode='lines',
                              subplot = 'polar2')
# Configure polar 2 for needle
fig.layout.polar2 = {}
fig.layout.polar2.hole = 0.1
fig.layout.polar2.angularaxis.showgrid = False
fig.layout.polar2.radialaxis.showgrid = False
fig.layout.polar2.radialaxis.range = [0, 1]
fig.layout.polar2.radialaxis.tickvals = []
fig.layout.polar2.bargap = 0.9
fig.layout.polar2.sector = [0, 180]
fig.layout.polar2.domain.x = [0, 1]
fig.layout.polar2.domain.y = [0, 0.35]
fig.layout.polar2.angularaxis.tickvals = []
fig.layout.polar2.radialaxis.tickvals = []
fig.layout.polar2.angularaxis.showline = False
fig.layout.polar2.radialaxis.showline = False


fig.layout.polar2.angularaxis.rotation = (180*(1-percent))



app = dash.Dash()

app.css.append_css({'external_url': 'https://codepen.io/plotly/pen/EQZeaW.css'})

spacer = html.Div(children=[], style=dict(height=20))

app.layout  = \
    html.Div([

        html.Div([
            # html.P('Select a voting district: ', style={'margin-top': '8rem'}),
            dcc.Dropdown(
                id="District",
                options=[{
                    'label': i,
                    'value': i
                } for i in districts],
                value='All Districts',
                multi=True,),

            dcc.Dropdown(
                id="Graph-type",
                options=[
                    {'label': 'District Demographics', 'value': 'demo'},
                    {'label': 'Firms Data', 'value': 'firms'},
                    {'label': 'Election Outcome Correlations', 'value': 'correlations'},
                    {'label': 'Canvassing Budget Plan', 'value': 'canvass-budget-constraint'}
                ],
                multi=False,
                value="basic-demo",
                style=dict(width=275, display='inline-block'),
            ),

            html.Button('Submit',
                        id='button',
                        style = dict(display='inline-block')),

            html.Div(dcc.Input(id='input-box', type='text')),
            html.Button('Calculate', id='submit'),
            html.Div(id='container-button-basic',
                     children='With a budget of 100000 people, you can visit these towns in Berkshire : {}'.format(string)),

            dcc.Graph(
                id='graph',
                figure=fig,
                style={'padding-left': '10px'}
            ),
        ], className='six columns'),

    ])



@app.callback(
    [Output('container-button-basic', 'children'), Output('graph', 'figure')],
    [Input('button', 'n_clicks'), Input('submit', 'n_clicks')],
    [State('District', 'value'), State('Graph-type', 'value'), State('input-box', 'value')]
)

def update_budget(n_clicks, n_submit, d_value, g_value, i_value):
    if g_value == "canvass-budget-constraint":
        if n_clicks and not n_submit:
            ret = "Enter a budget and press submit to see which towns in {} you can visit".format(d_value[0])
        elif n_submit:
            new_votingDistricts = list(repo[VOTING_DISTRICT_TOWNS_NAME].find(
                {"Type": "Senate", "District": d_value[0]},
                {"Towns": 1}))

            # Empty list that will eventually hold the populations of each town in the district
            new_popList = []
            new_availableTowns = []
            new_excludedTowns = []

            new_percent_tup = [0, 0]

            for d in new_votingDistricts:
                new_towns = d["Towns"]

                # Iterate through each town to get population (2017 estimates) if available
                for t in new_towns:
                    new_townDemo = list(repo[DEMOGRAPHIC_DATA_TOWN_NAME].find({"Town": re.compile("^" + t + "")}))
                    if new_townDemo and not math.isnan(new_townDemo[0]["Population, Census, April 1, 2010"]):
                        new_popList.append(new_townDemo[0]["Population, Census, April 1, 2010"])
                        new_availableTowns.append(t)
                    else:
                        new_excludedTowns.append(t)

            new_percent_tup[1] = len(new_availableTowns)

            # Set up z3 variables for towns (0,1) and their populations
            new_numTowns = len(new_availableTowns)
            new_xs = [z3.Real(new_availableTowns[i]) for i in range(new_numTowns)]
            new_ps = [z3.Real('new_pop' + new_availableTowns[i]) for i in range(new_numTowns)]

            new_S = z3.Solver()

            # Add the constraints saying what each town's population is and whether we visit that town (1) or not (0)
            for i in range(new_numTowns):
                new_S.add(new_ps[i] == new_popList[i])
                new_S.add(z3.Or(new_xs[i] == 1, new_xs[i] == 0))

            # Add constraint that total number of people visited must not exceed the budget (100,000 people)
            new_totalPeopleVisited = sum([new_xs[j] * new_ps[j] for j in range(new_numTowns)])
            new_S.add(new_totalPeopleVisited <= i_value)

            new_vals = []

            if str(new_S.check()) == "sat":
                new_model = new_S.model()
                new_vals = [(str(d), int(str(new_model[d]))) for d in new_model]


            new_towns = []
            if len(new_vals) != 0:
                for i in range(len(new_vals)):
                    if new_vals[i][1] == 1:
                        new_towns += [new_vals[i][0]]

            new_percent_tup[0] = len(new_towns)
            new_percent = new_percent_tup[0] / new_percent_tup[1]


            fig.layout.polar2.angularaxis.rotation = (180 * (1-new_percent))

            new_string = ""
            if len(new_towns) != 0:
                for t0 in new_towns[:-1]:
                    new_string += t0 + ", "
                new_string += new_towns[-1]


            if len(new_string) == 0:
                ret = "You cannot visit any towns in {} with a budget of {} people".format(d_value[0], i_value)
            else:
                ret = "You can visit the following towns with this budget: " + new_string

    else:
        ret = ""
    return ret, fig



if __name__ == '__main__':
    app.run_server(debug=True)