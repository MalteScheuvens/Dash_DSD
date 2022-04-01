import plotly.express as px
import pandas as pd
from dash.exceptions import PreventUpdate
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_daq as daq
import json
import gunicorn

import dashboard_functions as dash_func
from whitenoise import WhiteNoise

# Collect data
file_path = 'data/gtd_df_red.csv'
df_gtd = pd.read_csv(file_path)
df_gtd.drop(['Unnamed: 0'], axis=1, inplace=True)

df_gtd.replace(to_replace="Vehicle (not to include vehicle-borne explosives, i.e., car or truck bombs)",
               value="Vehicle", inplace=True)
df_gtd.replace(to_replace="Sabotage Equipment",
               value="Sabotage", inplace=True)

file_path = 'data/polity_gti.csv'
df_gti = pd.read_csv(file_path)
df_gti.drop(['Unnamed: 0'], axis=1, inplace=True)

# Build App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])
server = app.server
server.wsgi_app = WhiteNoise(server.wsgi_app, root='static/')

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

app.layout = html.Div([
    dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dash_func.drawText("Global Terrorism Dashboard")
                ], width=12),
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dbc.Card([
                            dbc.CardHeader('General Information'),
                            dbc.CardBody([
                                daq.NumericInput(
                                    id='year_input',
                                    min=1974,
                                    max=2017,
                                    label="Select a year",
                                    value=2000,
                                    size='100%'
                                ),
                                html.Br(),
                                dcc.Dropdown(
                                    id="map_dropdown",
                                    options=[
                                        {'label': 'GTI', 'value': 'absolute_terrorism_score'},
                                        {'label': 'Polity', 'value': 'polity2'}
                                    ],
                                    value='absolute_terrorism_score',
                                    placeholder="Select a world metric"
                                ),
                            ])
                        ], style={'textAlign': 'center',
                                  'max-width': '200px'})
                    ]),
                    html.Br(),
                    html.Div([
                        dbc.Card([
                            dbc.CardHeader('Detailed Information'),
                            dbc.CardBody([
                                dcc.Dropdown(
                                    id="y_metric_dropdown",
                                    options=[
                                        {'label': 'Incidents', 'value': 'index'},
                                        {'label': 'Casualties', 'value': 'number_of_killed'},
                                        {'label': 'Wounded', 'value': 'number_of_wounded'}
                                    ],
                                    value='index',
                                    placeholder="Select a metric"
                                ),
                                html.Br(),
                                dcc.Dropdown(
                                    id="x_metric_dropdown",
                                    options=[
                                        {'label': 'Attack Type', 'value': 'attack_type'},
                                        {'label': 'Weapon Type', 'value': 'weapon_type'},
                                        {'label': 'Target Type', 'value': 'target_type'}
                                    ],
                                    value='attack_type',
                                    placeholder="Select a metric"
                                )
                            ])
                        ], style={'textAlign': 'center',
                                  'max-width': '200px'})
                    ])
                ], width=2),
                dbc.Col([
                    html.Div(
                        html.Div([
                            dbc.Card([
                                dbc.CardHeader("Choropleth Map"),
                                dbc.CardBody([
                                    dcc.Graph(
                                        id="choropleth",
                                        config={

                                            'animate': True,
                                            'modeBarButtonsToRemove':[
                                                'select',
                                                'lasso2d']
                                        }
                                    )
                                ])
                            ], style={'textAlign': 'center'}),
                        ])
                    )
                ], width=6),
                dbc.Col([
                    html.Div(id='pie')
                ], width=4),
            ], align='start'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.Div(id='line')
                ], width=6),
                dbc.Col([
                    html.Div(id='hist')
                ], width=6),
            ], align='start'),
        ]), color='dark'
    )
], style={'fluid': True}
)


@app.callback(Output('select-data', 'children'),
              Input('choropleth', 'selectedData'))
def display_click_data(clickData):
    if clickData is None:
        return "hello"
    else:
        return json.dumps(clickData, indent=2)


# Update histogram based on selections
@app.callback(Output(component_id='hist', component_property='children'),
              Input(component_id='year_input', component_property='value'),
              Input(component_id='x_metric_dropdown', component_property='value'),
              Input(component_id='y_metric_dropdown', component_property='value'),
              Input('choropleth', 'selectedData'))
def plot_hist(year, x_metric, y_metric, selectedData):
    if selectedData is None:
        df = df_gtd.query('year == @year')
        txt1 = ' globally'
    else:
        country_code = selectedData['points'][0]['location']
        df_temp = df_gtd.query('year == @year')
        df = df_temp.query('country_code == @country_code')
        txt1 = ' in ' + str(selectedData['points'][0]['hovertext'])

    if y_metric == 'index':
        y_metric = None
        txt2 = 'number of incidents'
    else:
        txt2 = str(y_metric)

    fig_hist = px.histogram(df, x=x_metric, y=y_metric)
    fig_hist.update_layout(xaxis={'categoryorder': 'total descending'})
    fig_hist.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                           height=350)

    return dash_func.drawFigure(fig_hist,
                                'Bar chart of ' + x_metric + ' and ' + txt2 + ' in the year ' + str(year) + txt1,
                                "bar_chart")


# Update histogram based on selections
@app.callback(Output(component_id='line', component_property='children'),
              Input(component_id='y_metric_dropdown', component_property='value'),
              Input('choropleth', 'selectedData'))
def plot_line(y_metric, selectedData):
    if y_metric == 'index':
        if selectedData is None:
            df = df_gtd.groupby(['year']).count()
            txt1 = 'globally'
        else:
            country_code = selectedData['points'][0]['location']
            df_temp = df_gtd.query('country_code == @country_code')
            df = df_temp.groupby(['year']).count()
            txt1 = 'in ' + str(selectedData['points'][0]['hovertext'])

        txt2 = 'number of terroristic incidents'
    else:
        if selectedData is None:
            df = df_gtd.groupby(['year']).sum()
            txt1 = 'globally'
        else:
            country_code = selectedData['points'][0]['location']
            df_temp = df_gtd.query('country_code == @country_code')
            df = df_temp.groupby(['year']).sum()
            txt1 = 'in ' + str(selectedData['points'][0]['hovertext'])
        txt2 = str(y_metric)

    df.reset_index(inplace=True)
    fig_line = px.line(df, x='year', y=y_metric)
    fig_line.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                           height=350)

    return dash_func.drawFigure(fig_line, 'Line chart showing ' + txt2 + ' ' + txt1, 'line_chart')


# Update map based on selections
@app.callback(Output(component_id='choropleth', component_property='figure'),
              Input(component_id='year_input', component_property='value'),
              Input(component_id='map_dropdown', component_property='value'))
def plot_map(year, metric):
    fig_map = px.choropleth(df_gti.query('year == @year'), locations="country_code",
                            color=metric,
                            hover_name="country",
                            color_continuous_scale=px.colors.sequential.OrRd,
                            projection="natural earth")
    if metric == 'polity2':
        fig_map.update_coloraxes(colorscale=px.colors.sequential.RdBu)

    fig_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                          template='plotly_dark',
                          plot_bgcolor='rgba(0, 0, 0, 0)',
                          paper_bgcolor='rgba(0, 0, 0, 0)',
                          height=400)
    fig_map.update_geos(bgcolor='rgba(0, 0, 0, 0)')
    fig_map.update_coloraxes(colorbar=dict(orientation="h"), colorbar_title_text="")
    fig_map.update_layout(clickmode='event+select')

    return fig_map
    # return dash_func.drawFigure(fig_map, 'Choropleth map of ' + metric + ' in the year ' + str(year), "choropleth")


# Update pie chart based on dropdown selections
@app.callback(Output(component_id='pie', component_property='children'),
              Input(component_id='year_input', component_property='value'),
              Input(component_id='y_metric_dropdown', component_property='value'),
              Input('choropleth', 'selectedData'))
def plot_pie(year, metric, selectedData):
    country_code = None
    if selectedData is None:
        df = df_gtd.query('year == @year')
        txt1 = ' globally'

        if metric == 'index':
            df = df.groupby(['country_code', 'country']).count()
            txt2 = 'number of incidents'
        else:
            df = df.groupby(['country_code', 'country']).sum()
            txt2 = str(metric)

        df_sorted = df.sort_values(by=[metric], ascending=False)
        df_sorted.reset_index(inplace=True)
        df_sorted.iloc[5:, ]['country_code']='Rest of the world'
        df_sorted.iloc[5:, ]['country']='Rest of the world'
        df = df_sorted

    else:
        country_code = selectedData['points'][0]['location']
        df_temp = df_gtd.query('year == @year')
        df_temp.loc[df_temp['country_code'] != country_code, 'country_code'] = 'Rest of the world'
        df = df_temp
        txt1 = ' in ' + str(selectedData['points'][0]['hovertext'])

        if metric == 'index':
            df = df.groupby(['country_code', 'country']).count()
            txt2 = 'number of incidents'
        else:
            txt2 = str(metric)

    df.reset_index(inplace=True)
    fig_pie = px.pie(df,
                     names='country_code',
                     values=metric,
                     color_discrete_sequence=px.colors.sequential.RdBu)
    fig_pie.update_traces(sort=True, selector=dict(type='pie'))
    fig_pie.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                          height=400)

    return dash_func.drawFigure(fig_pie,
                                'Pie chart of ' + txt2 + ' in the year ' + str(year) + ' compared to the world',
                                'pie_chart')


if __name__ == '__main__':
    app.run_server(debug=False)
