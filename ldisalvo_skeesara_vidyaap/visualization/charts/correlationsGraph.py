import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pymongo
from dash.dependencies import Input, Output, State
from ldisalvo_skeesara_vidyaap.helper.constants import TEAM_NAME, DEMOGRAPHIC_DATA_DISTRICT_SENATE_NAME, VOTING_DISTRICT_TOWNS_NAME


# Set up the database connection.
client = pymongo.MongoClient()
repo = client.repo
repo.authenticate(TEAM_NAME, TEAM_NAME)


# populate the District drop down menu
senateList = list(repo[VOTING_DISTRICT_TOWNS_NAME].find({"Type": "Senate"}, {"District":1}))
districts = []
for x in senateList:
    districts +=[x["District"]]



tup = list(repo[DEMOGRAPHIC_DATA_DISTRICT_SENATE_NAME].find({
                                                                "Senate District": "Berkshire, Hampshire and Franklin"
                                                            },
                                                            {
                                                                "All firms, 2012": 1,
                                                                "Men-owned firms, 2012": 1,
                                                                "Women-owned firms, 2012": 1,
                                                                "Minority-owned firms, 2012": 1,
                                                                "Nonminority-owned firms, 2012": 1,
                                                                "Veteran-owned firms, 2012": 1,
                                                                "Nonveteran-owned firms, 2012": 1
                                                            }))
x_vals = []
y_vals = []
if len(tup) != 0:
    item = tup[0]
    all_firms = item["All firms, 2012"]

    x_vals = ["Men-owned", "Women-owned", "Minority-owned", "Non-minority-owned", "Veteran-owned", "Non-veteran-owned"]

    y_vals += [item["Men-owned firms, 2012"]/all_firms]
    y_vals += [item["Women-owned firms, 2012"]/all_firms]
    y_vals += [item["Minority-owned firms, 2012"]/all_firms]
    y_vals += [item["Nonminority-owned firms, 2012"]/all_firms]
    y_vals += [item["Veteran-owned firms, 2012"]/all_firms]
    y_vals += [item["Nonveteran-owned firms, 2012"]/all_firms]



trace0 = go.Bar(
    x=x_vals,
    y=y_vals,
    marker=dict(
        color='rgb(15, 130, 43)',
        line=dict(
            color='rgb(8,48,107)',
            width=1.5,
        )
    ),
    opacity=0.6
)

data = [trace0]
layout = go.Layout(
    title='Firms Ownership Breakdown in Berkshire, Hampshire and Franklin',
)

graph = go.Figure(data=data, layout=layout)

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

            dcc.Graph(
                id='graph',
                figure=graph,
                style={'padding-left': '10px'}
            ),
        ], className='six columns'),

    ])


@app.callback(
    Output('graph', 'figure'),
    [Input('button', 'n_clicks')],
    [State('District', 'value'), State('Graph-type', 'value')])

def update_output(n_clicks, d_value, g_value):

    if d_value[0] != "":
        new_tup = list(repo[DEMOGRAPHIC_DATA_DISTRICT_SENATE_NAME].find({"Senate District": d_value[0]},
            {
                "All firms, 2012": 1,
                "Men-owned firms, 2012": 1,
                "Women-owned firms, 2012": 1,
                "Minority-owned firms, 2012": 1,
                "Nonminority-owned firms, 2012": 1,
                "Veteran-owned firms, 2012": 1,
                "Nonveteran-owned firms, 2012": 1
            }))


        new_x_vals = []
        new_y_vals = []

        if len(new_tup) != 0:
            new_item = new_tup[0]
            new_all_firms = new_item["All firms, 2012"]

            new_x_vals = ["Men-owned", "Women-owned", "Minority-owned", "Non-minority-owned", "Veteran-owned",
                      "Non-veteran-owned"]

            new_y_vals += [new_item["Men-owned firms, 2012"] / new_all_firms]
            new_y_vals += [new_item["Women-owned firms, 2012"] / new_all_firms]
            new_y_vals += [new_item["Minority-owned firms, 2012"] / new_all_firms]
            new_y_vals += [new_item["Nonminority-owned firms, 2012"] / new_all_firms]
            new_y_vals += [new_item["Veteran-owned firms, 2012"] / new_all_firms]
            new_y_vals += [new_item["Nonveteran-owned firms, 2012"] / new_all_firms]

    if g_value == "firms":
        trace = go.Bar(
            x=new_x_vals,
            y=new_y_vals,
            marker=dict(
                color='rgb(15, 130, 43)',
                line=dict(
                    color='rgb(8,48,107)',
                    width=1.5,
                )
            ),
            opacity=0.6
        )

        new_data = [trace]
        new_layout = go.Layout(
            title='Firms Ownership Breakdown in {}'.format(d_value[0]),
        )

        return dict(data=new_data, layout=new_layout)


if __name__ == '__main__':
    app.run_server(debug=True)