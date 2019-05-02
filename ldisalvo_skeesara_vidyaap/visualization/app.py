"""
CS504 : app
Team : Vidya Akavoor, Lauren DiSalvo, Sreeja Keesara
Description :

Notes : 

April 28, 2019
"""
import sd_material_ui
import plotly.graph_objs as go

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State

from ldisalvo_skeesara_vidyaap.visualization.charts.senateCorr import fig as senateCorrChart
from ldisalvo_skeesara_vidyaap.visualization.charts.houseCorr import fig as houseCorrChart
from ldisalvo_skeesara_vidyaap.visualization.charts.race import getValues, race
from ldisalvo_skeesara_vidyaap.visualization.charts.correlationsGraph import create_firms_graph
from ldisalvo_skeesara_vidyaap.visualization.charts.canvassingVisual import calculate_budget
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
                       style = {'fontWeight':600, 'padding-right': '10px'}),
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
            html.P('Select a chart type and voting district to view more information.', style=dict(marginTop='8rem', paddingLeft='10px')),
            html.Div([
                html.Div(
                    dcc.Dropdown(
                        id='Graph-type',
                        options=[
                            {'label': 'Election Outcome Correlations', 'value': 'correlations'},
                            {'label': 'Canvassing Budget Plan', 'value': 'canvass-budget-constraint'},
                            {'label': 'Racial Breakdown', 'value': 'race'},
                            {'label': 'Firms Ownership Breakdown', 'value': 'firms'},
                        ],
                        multi=False,
                        value="correlations",
                        style=dict(width=250, display='inline-block'),
                        placeholder='Select a chart type.'
                    ),
                style=dict(padding='10px', display='inline-block', verticalAlign='middle')),

                html.Div(
                    dcc.Dropdown(
                        id='District',
                        options=[],
                        multi=False,
                        value="",
                        style=dict(width=250, display='inline-block'),
                        placeholder='Select a district to learn more...'
                    ),
                style=dict(padding='10px', display='inline-block', verticalAlign='middle')),

                html.Div(
                    sd_material_ui.RaisedButton(
                        label='Submit',
                        id='button',
                        buttonStyle = dict(display='inline-block', height='34px'),
                    ),
                style=dict(padding='10px', display='inline-block')),
            ]),
            html.Div(
                id='chart-content',
                children=[
                    html.Div(id='constraint-message'),
                    html.Div(dcc.Input(id='constraint-input', type='text')),
                    html.Button('Calculate', id='constraint-submit'),

                    dcc.Graph(
                        id='constraint-chart',
                        style={'padding-left': '10px'}
                    ),
                ]
            ),
        ], className='six columns'),
    ])

@app.callback(
    [Output('senateButton', 'buttonStyle'),
     Output('houseButton', 'buttonStyle'),
     Output('District', 'options')],
    [Input('houseButton', 'n_clicks'),
     Input('senateButton', 'n_clicks')],
    [State('houseButton', 'n_clicks_previous'),
     State('senateButton', 'n_clicks_previous')])
def update_buttons(n_clicks_house, n_clicks_senate, n_clicks_prev_house, n_clicks_prev_senate):
    if n_clicks_senate:
        if (n_clicks_senate == 1 and n_clicks_prev_senate == None) or (n_clicks_senate > n_clicks_prev_senate):
            options = [dict(label=district, value=district) for district in SENATE_MAP_POINTS['name'].tolist()]
            return dict(width=275, backgroundColor='lightgrey'), dict(width=275), options
        else:
            options = [dict(label=district, value=district) for district in HOUSE_MAP_POINTS['name'].tolist()]
            return dict(width=275), dict(width=275, backgroundColor='lightgrey'), options
    else:
        options = [dict(label=district, value=district) for district in HOUSE_MAP_POINTS['name'].tolist()]
        return dict(width=275), dict(width=275, backgroundColor='lightgrey'), options

@app.callback(
    [Output('year-slider', 'disabled'),
     Output('choropleth-title', 'children')],
    [Input('historical', 'toggled')])
def update_slider(wantsAverage):
    if wantsAverage:
        return True, "Average Political Party Alignment by Voting District from Republican to Democrat (-1, 1)"
    else:
        return False, "Political Party Alignment by Voting District and Year from Republican to Democrat (-1, 1)"

@app.callback(
    Output('District', 'disabled'),
    [Input('Graph-type', 'value')])
def disable_district(g_value):
    if g_value == "correlations":
        return True
    return False

@app.callback(
    Output('district-level-choropleth', 'figure'),
    [Input('houseButton', 'buttonStyle'),
     Input('senateButton', 'buttonStyle'),
     Input('historical', 'toggled'),
     Input('year-slider', 'value')],
    [State('district-level-choropleth', 'figure'),
     State('District', 'value')])
def update_graph(btn_house_style, btn_senate_style, wantsAverage, year, figure, district):
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
                score=ratiosList[x].tolist()[0]))

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

@app.callback(
    Output('chart-content', 'children'),
    [Input('houseButton', 'buttonStyle'),
     Input('senateButton', 'buttonStyle'),
     Input('button', 'n_clicks')],
    [State('District', 'value'),
     State('Graph-type', 'value')])
def return_chart(btn_house_style, btn_senate_style, n_clicks, district, graphType):
    if graphType == 'correlations':
        if btn_senate_style == dict(width=275, backgroundColor='lightgrey'):
            correlation_chart = senateCorrChart
        else:
            correlation_chart = houseCorrChart
        return dcc.Graph(id='Correlation', figure=correlation_chart)

    elif graphType == 'race':
        if btn_senate_style == dict(width=275, backgroundColor='lightgrey'):
            vals = getValues(district, SENATE_KEY)
        else:
            vals = getValues(district, HOUSE_KEY)

        race_chart = go.Figure(
            data=[go.Pie(labels=race,
                         values=vals)],
            layout=go.Layout(
                legend=dict(x=-.2, y=-.2, bgcolor='rgba(0,0,0,0)'),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                autosize=True,
                title='Racial Breakdown')
        )

        return dcc.Graph(id='Race', figure=race_chart)
    elif graphType == "firms":
        if btn_senate_style == dict(width=275, backgroundColor='lightgrey'):
            chart = create_firms_graph(district, SENATE_KEY)
        else:
            chart = create_firms_graph(district, HOUSE_KEY)
        return dcc.Graph(id='graph', figure=chart, style={'padding-left': '10px'})

    elif graphType == "canvass-budget-constraint":
        return [
                        html.Div(id='constraint-message',
                                 children='Enter a budget and press "Calculate" to see which towns in {} you can visit'.format(
                                     district),
                                 style=dict(padding='10px')),
                        html.Div(dcc.Input(id='constraint-input', type='text'), style=dict(padding='10px', display='inline-block')),
                        html.Div(html.Button('Calculate', id='constraint-submit'), style=dict(padding='10px', display='inline-block')),

                        dcc.Graph(
                            id='constraint-chart',
                            style={'padding-left': '10px'}
                        ),
                ]

@app.callback(
    [Output('constraint-message', 'children'),
    Output('constraint-chart', 'figure')],
    [Input('constraint-submit', 'n_clicks')],
    [State('District', 'value'),
     State('constraint-input', 'value'),
     State('houseButton', 'buttonStyle'),
     State('senateButton', 'buttonStyle')]
)
def create_constraint_chart(n_clicks, district, budget_constraint, btn_house_style, btn_senate_style):
    if n_clicks != None:
        budget_constraint = int(budget_constraint.replace(',',''))
        if btn_senate_style == dict(width=275, backgroundColor='lightgrey'):
            msg, constraint_chart = calculate_budget(district, budget_constraint, SENATE_KEY)
        else:
            msg, constraint_chart = calculate_budget(district, budget_constraint, HOUSE_KEY)

        return msg, constraint_chart
    return "", [
                html.Div(id='constraint-message', children='Enter a budget and press "Calculate" to see which towns in {} you can visit'.format(district)),
                html.Div(dcc.Input(id='constraint-input', type='text')),
                html.Button('Calculate', id='constraint-submit'),
                dcc.Graph(
                    id='constraint-chart',
                    style={'padding-left': '10px'}
                ),
    ]

if __name__ == '__main__':
    app.run_server(debug=True)