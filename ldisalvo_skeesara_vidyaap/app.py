import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.graph_objs as graph_objs
import sd_material_ui
from dash.dependencies import Input, Output, State
import pymongo
import math


from ldisalvo_skeesara_vidyaap.helper.constants import TEAM_NAME, VOTING_DISTRICT_TOWNS_NAME, \
    DEMOGRAPHIC_DATA_DISTRICT_SENATE_NAME, DEMOGRAPHIC_SENATE_CORRELATIONS_NAME, DEMOGRAPHIC_HOUSE_CORRELATIONS_NAME
from dash.dependencies import Input, Output

# Set up the database connection.
client = pymongo.MongoClient()
repo = client.repo
repo.authenticate(TEAM_NAME, TEAM_NAME)

senateList = list(repo[VOTING_DISTRICT_TOWNS_NAME].find({"Type": "Senate"}, {"District":1}))
districts = []
for x in senateList:
    districts +=[x["District"]]
#print(districts)

print(districts[0])
race = ['White', 'Black or African American', 'American Indian and Alaska Native', 'Asian', 'Native Hawaiian and Other Pacific Islander', 'Hispanic or Latino']
initial = list(repo[DEMOGRAPHIC_DATA_DISTRICT_SENATE_NAME].find({"Senate District": districts[0]}, {"White alone, percent": 1,
                                                                 "Black or African American alone, percent":1,
                                                                 "American Indian and Alaska Native alone, percent":1,
                                                                 "Asian alone, percent":1,
                                                                 "Native Hawaiian and Other Pacific Islander alone, percent":1,
                                                                 "Hispanic or Latino, percent":1}))
initialValue = list(initial[0].values())[1:]

def getValues(district):
    val = list(repo[DEMOGRAPHIC_DATA_DISTRICT_SENATE_NAME].find({"Senate District": district}, {"White alone, percent": 1,
                                                                 "Black or African American alone, percent":1,
                                                                 "American Indian and Alaska Native alone, percent":1,
                                                                 "Asian alone, percent":1,
                                                                 "Native Hawaiian and Other Pacific Islander alone, percent":1,
                                                                 "Hispanic or Latino, percent":1}))
    finVal = list(val[0].values())[1:]
    return finVal

def getCorr():
    ans = []  # format: [[dem factors, dem values], [rep factors, rep values]]
    for x in range(2):
        party = list(repo[DEMOGRAPHIC_SENATE_CORRELATIONS_NAME].find())[x]

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
DemLabel = corrDem[0]
DemValue = corrDem[1]
RepLabel = corrRep[0]
RepValue = corrRep[1]
app = dash.Dash()

mapbox_access_token = "pk.eyJ1Ijoic2tlZXNhcmEiLCJhIjoiY2p1bXB5bGF6MHNsZTQzczh4djh1eDI3aCJ9.vTi1hnCqCO7txE_veUAaEg"

app.css.append_css({'external_url': 'https://codepen.io/plotly/pen/EQZeaW.css'})

spacer = html.Div(children=[], style=dict(height=20))

app.layout  = \
    html.Div([
        html.Div([
            dcc.Dropdown(
                id="District",
                options=[{
                    'label': i,
                    'value': i
                } for i in districts],
                value='All Districts',
                multi=False),

            dcc.Dropdown(
                id="Graph-type",
                options=[
                    {'label': 'Racial Breakdown', 'value': 'race'},
                    {'label': 'Strongest Political Party Predictors', 'value': 'corr'}
                ],
                multi=False,
                value="basic-demo",
            ),
            html.Button('Submit',
                id='button',
                style = dict(display='inline-block')),

            dcc.Graph(id='Race',
                      figure=go.Figure(
                          data=[go.Pie(labels=race,
                                       values=initialValue)],
                          layout=go.Layout(
                              legend=dict(x=-.2, y=-.2),
                                height = 800,
                                width = 600,
                                margin=dict(
                                  l=50,
                                  r=100,
                                  b=20,
                                  t=50,
                                  pad=0
                              ),
                              title='Racial Breakdown')
                      )),

        ], className='six columns'),

    ])
#
@app.callback(
    Output('Race', 'figure'),
    [Input('button', 'n_clicks')],
    [State('District', 'value'), State('Graph-type', 'value')])

def update_output(n_clicks, d_value, g_value):
    if g_value == "race":
        vals = getValues(d_value)
        figure = go.Figure(
            data=[go.Pie(labels=race,
                         values=vals)],
            layout=go.Layout(
                legend=dict(x=-.2, y=-.2),
                height=800,
                width=600,
                margin=dict(
                    l=50,
                    r=100,
                    b=20,
                    t=50,
                    pad=0
                ),
                title='Racial Breakdown')
        )
        return figure


if __name__ == '__main__':
    app.run_server(debug=True)
