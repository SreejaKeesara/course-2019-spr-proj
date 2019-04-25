"""
CS504 : test.py
Team : Vidya Akavoor, Lauren DiSalvo, Sreeja Keesara
Description :

Notes :

April 16, 2019
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as graph_objs
import sd_material_ui
from dash.dependencies import Input, Output
import dml
from ldisalvo_skeesara_vidyaap.helper.constants import TEAM_NAME, HISTORICAL_RATIOS_NAME

mapbox_access_token = "pk.eyJ1Ijoic2tlZXNhcmEiLCJhIjoiY2p1bXB5bGF6MHNsZTQzczh4djh1eDI3aCJ9.vTi1hnCqCO7txE_veUAaEg"

# BINS = [-.8, -.6, -.4, -.2, 0, .2, .4, .6, .8, 1]
# COLORSCALE = ["#e50b00", "#cb0a15", "#b2092a", "#98083f", "#7f0754", "65066a", "4c057f", "320494", "1903a9", "0003bf"]

# def get_data_for_year(year):
#
#     # Set up the database connection.
#     client = dml.pymongo.MongoClient()
#     repo = client.repo
#     repo.authenticate(TEAM_NAME, TEAM_NAME)
#
#     # Get data for year
#     year_ratios = list(repo[HISTORICAL_RATIOS_NAME].find({ "year": year }))

data = graph_objs.Data([
    graph_objs.Scattermapbox(
        lat=['45.5017'],
        lon=['-73.5673'],
        mode='markers',
    )
])

layout = graph_objs.Layout(
    height=400,
    autosize=True,
    hovermode='closest',
    margin = dict(l = 0, r = 0, t = 0, b = 0),
    mapbox=dict(
        layers=[
            dict(
                sourcetype = 'geojson',
                source = "http://datamechanics.io/data/ldisalvo_skeesara_vidyaap/MA_House_Shapes.json",
                type = 'fill',
                color = 'rgba(163,22,19,0.8)'
            )
        ],
        accesstoken=mapbox_access_token,
        bearing=0,
        center=dict(
            lat=42.4,
            lon=-71.38
        ),
        pitch=0,
        zoom=6.5,
        style='light',
    ),
)

fig = dict(data=data, layout=layout)

app = dash.Dash(__name__)

app.css.append_css({'external_url': 'https://codepen.io/plotly/pen/EQZeaW.css'})

spacer = html.Div(children=[], style=dict(height=20))

app.layout  = \
    html.Div([
        html.Div([
            html.Div([
                html.H3(children='Local Politics in Massachusetts'),
                html.P('Choose between State House or State Senate elections to view voting patterns in those districts.'),
            ], style=dict(padding='10px')),

            html.Div(children=[
                html.Div([
                    sd_material_ui.RaisedButton(id='houseButton',
                                                label='House',
                                                buttonStyle=dict(width=275)),
                ], style={'display': 'inline-block', 'padding': '10px'}),

                html.Div([
                    sd_material_ui.RaisedButton(id='senateButton',
                                                label='Senate',
                                                buttonStyle=dict(width=275)),
                ], style={'display': 'inline-block', 'padding': '10px'}),

                sd_material_ui.Toggle(id='historical', label="Average ideology by district from 2010 to 2018", labelPosition='right', style=dict(padding='10px'), labelStyle={'font-size': 18}),

                spacer,

                sd_material_ui.Divider(),

                spacer,
            ]),

            html.Div([
                dcc.Graph(
                    id='district-level-choropleth',
                    figure=fig,
                    style={'padding-left': '10px'}
                ),

                spacer,

                dcc.Slider(
                    min=2010,
                    max=2018,
                    marks={
                        2010: '2010',
                        2012: '2012',
                        2014: '2014',
                        2016: '2016',
                        2018: '2018',
                    },
                    value=2018,
                )
            ], style=dict(padding='10px'))


        ], className='six columns'),

        html.Div([
            # html.P('Select a voting district: ', style={'margin-top': '8rem'}),
            dcc.Dropdown(
                options=[],
                multi=True,
                value="",
                style=dict(width=275, display='inline-block', padding='10px'),
            ),

            dcc.Dropdown(
                options=[
                    {'label': 'District Demographics', 'value': 'demo'},
                    {'label': 'Election Outcome Correlations', 'value': 'correlations'},
                    {'label': 'Canvassing Budget Plan', 'value': 'canvass-budget-constraint'}
                ],
                multi=False,
                value="basic-demo",
                style=dict(width=275, display='inline-block', padding='10px'),
            )
        ], className='six columns'),
    ])

# @app.callback(
#     [Output('houseButton', 'disabled'),
#      Output('senateButton', 'disabled'),
#      Output('district-level-choropleth', 'figure')],
#     [Input('houseButton', 'n_clicks')])
# def create_house_graph(n_clicks):
#     layout = graph_objs.Layout(
#         height=400,
#         autosize=True,
#         hovermode='closest',
#         margin=dict(l=0, r=0, t=0, b=0),
#         mapbox=dict(
#             layers=[
#                 dict(
#                     sourcetype='geojson',
#                     source="http://datamechanics.io/data/ldisalvo_skeesara_vidyaap/MA_House_Shapes.json",
#                     type='fill',
#                     color='rgba(163,22,19,0.8)'
#                 )
#             ],
#             accesstoken=mapbox_access_token,
#             bearing=0,
#             center=dict(
#                 lat=42.4,
#                 lon=-71.38
#             ),
#             pitch=0,
#             zoom=6.5,
#             style='light',
#         ),
#     )
#
#     figure = dict(data=data, layout=layout)
#     return True, False, figure
#
#
# @app.callback(
#     [Output('senateButton', 'disabled'),
#      Output('houseButton', 'disabled'),
#      Output('district-level-choropleth', 'figure')],
#     [Input('senateButton', 'n_clicks')])
# def create_senate_graph(n_clicks):
#     layout = graph_objs.Layout(
#         height=400,
#         autosize=True,
#         hovermode='closest',
#         margin=dict(l=0, r=0, t=0, b=0),
#         mapbox=dict(
#             layers=[
#                 dict(
#                     sourcetype='geojson',
#                     source="http://datamechanics.io/data/ldisalvo_skeesara_vidyaap/MA_Senate_Shapes.json",
#                     type='fill',
#                     color='rgba(163,22,19,0.8)'
#                 )
#             ],
#             accesstoken=mapbox_access_token,
#             bearing=0,
#             center=dict(
#                 lat=42.4,
#                 lon=-71.38
#             ),
#             pitch=0,
#             zoom=6.5,
#             style='light',
#         ),
#     )
#
#     figure = dict(data=data, layout=layout)
#     return True, False, figure


if __name__ == '__main__':
    app.run_server(debug=True)
