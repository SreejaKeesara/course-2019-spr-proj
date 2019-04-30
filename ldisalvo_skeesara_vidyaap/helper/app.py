"""
CS504 : app
Team : Vidya Akavoor, Lauren DiSalvo, Sreeja Keesara
Description :

Notes : 

April 28, 2019
"""

import sd_material_ui

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State

from ldisalvo_skeesara_vidyaap.helper.dataRetrieval import dataRetrieval
from ldisalvo_skeesara_vidyaap.helper.constants import BINS,COLORSCALE, MAPBOX_ACCESS_TOKEN,\
    URL_YEAR_TEMPLATE, URL_AVG_TEMPLATE, SENATE_KEY, HOUSE_KEY
from ldisalvo_skeesara_vidyaap.helper.dataRetrieval import SENATE_BY_YEAR, HOUSE_BY_YEAR, \
    SENATE_AVERAGE, HOUSE_AVERAGE, SENATE_MAP_POINTS, HOUSE_MAP_POINTS

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

                sd_material_ui.Toggle(id='historical',
                                      label="Average ideology by district from 2010 to 2018",
                                      labelPosition='right', style=dict(padding='10px'),
                                      labelStyle={'font-size': 18}),

                spacer,

                sd_material_ui.Divider(),

                spacer,
            ]),

            html.Div([
                html.P(id = 'choropleth-title',
                       style = {'fontWeight':600}),
                dcc.Loading(id='loading-1', children=[dcc.Graph(
                    id='district-level-choropleth',
                    animate=True,
                    style={'padding-left': '10px'}
                )], type='graph'),

                spacer,

                html.Div(
                    id='slider-div',
                    children=[dcc.Slider(
                        id='year-slider',
                        min=2012,
                        max=2018,
                        marks={
                            2012: '2012',
                            2014: '2014',
                            2016: '2016',
                            2018: '2018',
                        },
                        value=2018,
                    )]
                ),

            ], style=dict(padding='10px'))


        ], className='six columns'),

        html.Div([
            html.P('Select a voting district to view more information about demographics and recent elections.', style=dict(marginTop='8rem', paddingLeft='10px')),
            html.Div(
                dcc.Dropdown(
                    options=[
                        {'label': 'District Demographics', 'value': 'demo'},
                        {'label': 'Election Outcome Correlations', 'value': 'correlations'},
                        {'label': 'Canvassing Budget Plan', 'value': 'canvass-budget-constraint'}
                    ],
                    multi=False,
                    value="basic-demo",
                    style=dict(width=275, display='inline-block'),
                    placeholder='Select a chart type.'
                ),
            style=dict(padding='10px', display='inline-block')),

            html.Div(
                dcc.Dropdown(
                    id='district-dropdown',
                    options=[],
                    multi=False,
                    value="",
                    style=dict(width=275, display='inline-block'),
                    placeholder='Select a district to learn more...'
                ),
            style=dict(padding='10px', display='inline-block')),
        ], className='six columns'),
    ])

@app.callback(
    [Output('senateButton', 'buttonStyle'),
     Output('houseButton', 'buttonStyle'),
     Output('district-dropdown', 'options'),
     Output('district-dropdown', 'value')],
    [Input('houseButton', 'n_clicks'),
     Input('senateButton', 'n_clicks')],
    [State('houseButton', 'n_clicks_previous'),
     State('senateButton', 'n_clicks_previous')])
def update_buttons(n_clicks_house, n_clicks_senate, n_clicks_prev_house, n_clicks_prev_senate):
    if n_clicks_senate:
        if (n_clicks_senate == 1 and n_clicks_prev_senate == None) or (n_clicks_senate > n_clicks_prev_senate):
            options = [dict(label=district, value=district) for district in SENATE_MAP_POINTS['name'].tolist()]
            return dict(width=275, backgroundColor='lightgrey'), dict(width=275), options, 'all'
        else:
            options = [dict(label=district, value=district) for district in HOUSE_MAP_POINTS['name'].tolist()]
            return dict(width=275), dict(width=275, backgroundColor='lightgrey'), options, 'all'
    else:
        options = [dict(label=district, value=district) for district in HOUSE_MAP_POINTS['name'].tolist()]
        return dict(width=275), dict(width=275, backgroundColor='lightgrey'), options, 'all'

@app.callback(
    [Output('year-slider', 'disabled'),
     Output('choropleth-title', 'children')],
    [Input('historical', 'toggled')])
def update_slider(wantsAverage):
    if wantsAverage:
        return True, "Average Political Party Alignment by Voting District from Republican (-1) to Democrat (1)"
    else:
        return False, "Political Party Alignment by Voting District and Year from Republican (-1) to Democrat (1)"

@app.callback(
    Output('district-level-choropleth', 'figure'),
    [Input('houseButton', 'buttonStyle'),
     Input('senateButton', 'buttonStyle'),
     Input('historical', 'toggled'),
     Input('year-slider', 'value'),
     Input('district-dropdown', 'value')],
    [State('district-level-choropleth', 'figure')])
def update_graph(btn_house_style, btn_senate_style, wantsAverage, year, districtSelected, figure):
    annotations = [dict(
        showarrow=False,
        align='right',
        text='Political Party Alignment',
        x=0.95,
        y=0.95,
    )]

    for i in range(1, len(BINS)):
        color = COLORSCALE[i - 1]
        text = str(BINS[i - 1]) + " to " + str(BINS[i])
        annotations.append(
            dict(
                arrowcolor=color,
                text=text,
                x=0.95,
                y=0.85 - (i / 20),
                ax=-60,
                ay=0,
                arrowwidth=10,
                arrowhead=0,
            )
        )

    layout = dict(
                height=400,
                autosize=True,
                hovermode='closest',
                margin=dict(l=0, r=0, t=0, b=0),
                annotations=annotations,
                mapbox=dict(
                    layers=[],
                    accesstoken=MAPBOX_ACCESS_TOKEN,
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

    if btn_senate_style == dict(width=275, backgroundColor='lightgrey'):
        for x in range(1, len(BINS)):
            lower = BINS[x - 1]
            upper = BINS[x]

            source = URL_AVG_TEMPLATE.format(type=SENATE_KEY, upper=upper, lower=lower) if wantsAverage else URL_YEAR_TEMPLATE.format(type=SENATE_KEY, year=year, upper=upper, lower=lower)

            layer = dict(
                sourcetype = 'geojson',
                source = source,
                type = 'fill',
                color = COLORSCALE[x-1],
            )

            layout['mapbox']['layers'].append(layer)


        districtList = SENATE_MAP_POINTS['name']
        ratiosList = dataRetrieval.get_ratios_list(SENATE_AVERAGE, True, districtList, year) if wantsAverage else dataRetrieval.get_ratios_list(SENATE_BY_YEAR, False, districtList, year)
        hoverList = []

        for x in range(len(districtList)):
            hoverList.append('{district}<br>Population: {pop}<br>Score: {score}'.format(
                district=districtList[x], pop=SENATE_MAP_POINTS['population'][x],
                score=ratiosList[x]))

        data = [dict(
            lat=SENATE_MAP_POINTS['lat'],
            lon=SENATE_MAP_POINTS['lon'],
            text=hoverList,
            type='scattermapbox',
            hoverinfo='text',
            marker=dict(size=5, color='white', opacity=0)
        )]

    else:
        for x in range(1, len(BINS)):
            lower = BINS[x - 1]
            upper = BINS[x]

            source = URL_AVG_TEMPLATE.format(type=HOUSE_KEY, upper=upper, lower=lower) if wantsAverage else URL_YEAR_TEMPLATE.format(type=HOUSE_KEY, year=year, upper=upper, lower=lower)

            layer = dict(
                sourcetype='geojson',
                source=source,
                type='fill',
                color=COLORSCALE[x - 1],
            )

            layout['mapbox']['layers'].append(layer)

        districtList = HOUSE_MAP_POINTS['name']
        ratiosList = dataRetrieval.get_ratios_list(HOUSE_AVERAGE, True, districtList, year) if wantsAverage else dataRetrieval.get_ratios_list(HOUSE_BY_YEAR, False, districtList, year)
        hoverList = []

        for x in range(len(districtList)):
            hoverList.append('{district}<br>Population: {pop}<br>Score: {score}'.format(
                district=districtList[x], pop=HOUSE_MAP_POINTS['population'][x],
                score=ratiosList[x].tolist()[0]))

        data = [dict(
            lat=HOUSE_MAP_POINTS['lat'],
            lon=HOUSE_MAP_POINTS['lon'],
            text=hoverList,
            type='scattermapbox',
            hoverinfo='text',
            marker=dict(size=5, color='white', opacity=0)
        )]

    fig = dict(data=data, layout=layout)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)