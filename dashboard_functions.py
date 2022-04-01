from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash import dash_table


# Plotting the figures
def drawFigure(figure, text, id):
    return html.Div([
        dbc.Card([
            dbc.CardHeader(text),
            dbc.CardBody([
                dcc.Graph(
                    id=id,
                    animate=False,
                    figure=figure.update_layout(
                        template='plotly_dark',
                        plot_bgcolor='rgba(0, 0, 0, 0)',
                        paper_bgcolor='rgba(0, 0, 0, 0)'
                    ),
                    config={
                        'displayModeBar': False
                    }
                )
            ])
        ], style={'textAlign': 'center'}),
    ])

# Text field
def drawText(text):
    return html.Div([
        dbc.Card(
            dbc.CardBody(
                html.Div([
                    html.H2(text),
                ], style={'textAlign': 'center'})
            )
        ),
    ])


# Creating a table
def drawTable(data, text):
    return html.Div([
        dbc.Card([
            dbc.CardHeader(text),
            dbc.CardBody([
                dash_table.DataTable(
                    id='table',
                    columns=[{'name': col, 'id': col}
                             for col in data.columns],
                    data=data.to_dict('records'),
                    filter_action='native',
                    style_header={
                        'backgroundColor': '#32383E',
                        'fontWeight': 'bold',
                        'color': '#AAAAAA',
                        'font-family': 'sans-serif'
                    },
                    style_table={
                        'height': 400,
                        'color': 'grey',
                        'font-family': 'sans-serif'
                    },
                    style_data={
                        'width': '100px', 'minWidth': '80px', 'maxWidth': '80px',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                    },
                    style_cell={
                        'fontSize': 14,
                        'font-family': 'sans-serif'},
                    style_as_list_view=True,
                    fixed_rows={'headers': True},
                    page_size=100
                )
            ])
        ], style={'textAlign': 'center'})
    ])
