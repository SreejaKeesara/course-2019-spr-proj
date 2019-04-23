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

mapbox_access_token = "pk.eyJ1Ijoic2tlZXNhcmEiLCJhIjoiY2p1bXB5bGF6MHNsZTQzczh4djh1eDI3aCJ9.vTi1hnCqCO7txE_veUAaEg"

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

app = dash.Dash(__name__, static_folder='static')

app.css.append_css({'external_url': 'https://codepen.io/plotly/pen/EQZeaW.css'})


app.layout  = \
    html.Div([
        html.Div([
            html.Div([
                html.H4(children='Local Politics in Massachusetts'),
                html.P('Choose between State House or State Senate Elections to view voting patterns in those districts.'),
            ]),

            html.Div([
                dcc.RadioItems(
                    options=[
                        {'label': 'House', 'value': 'House'},
                        {'label': 'Senate', 'value': 'Senate'},
                    ],
                    value='Senate',
                    labelStyle={'display': 'inline-block', 'padding-right': '50px'},
                )
            ], style={'width':400, 'margin':25}),
            dcc.Graph(
                id='graph',
                figure=fig,
                style={'padding-left': '10px'}
            ),
        ], className='six columns'),
    ])


if __name__ == '__main__':
    app.run_server(debug=True)