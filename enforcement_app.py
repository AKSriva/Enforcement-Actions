# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 23:01:20 2024

@author: sandh
"""
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Sample data (replace with your dataset)
data = pd.read_csv('Enforcement_Actions_.csv')

# Initialize Dash app with a Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
app.title = "Enforcement Action Analysis"

# Navbar
navbar = dbc.NavbarSimple(
    brand="Enforcement Action Analysis",
    brand_href="#",
    color="primary",
    dark=True,
    style={'marginBottom': '20px'}
)

# Layout
app.layout = dbc.Container([
    navbar,  # Top navigation bar

    # Filters section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Filters"),
                dbc.CardBody([
                    dbc.Label("Enforcement Type"),
                    dcc.Dropdown(
                        id='enforcement-type-dropdown',
                        options=[{'label': etype, 'value': etype} for etype in data['Enforcement Type'].unique()],
                        placeholder="Select Enforcement Type",
                    ),
                    dbc.Label("Organization", style={'marginTop': '10px'}),
                    dcc.Dropdown(id='organization-dropdown', placeholder="Select Organization"),
                    dbc.Label("Month Fined", style={'marginTop': '10px'}),
                    dcc.Dropdown(id='month-dropdown', placeholder="Select Month Fined")
                ])
            ])
        ], width=3),  # Filters column
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Fines by Organization"),
                dbc.CardBody([
                    dcc.Graph(id='fines-bar-chart')
                ])
            ])
        ], width=9)  # Graph column
    ]),

    # Metrics and Placeholder sections
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Key Metrics"),
                dbc.CardBody([
                    html.Div(id='organization-count', style={'fontSize': '20px'}),
                    html.Div(id='total-fines', style={'fontSize': '20px'})
                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Future Development"),
                dbc.CardBody("This space is reserved for future upgrades.")
            ])
        ], width=6)
    ], style={'marginTop': '20px'}),

    # Footer
    dbc.Row([
        dbc.Col(html.Div("© 2024 Datsura Inc. All Rights Reserved.", style={
            'textAlign': 'center',
            'marginTop': '20px',
            'fontSize': '14px',
            'color': '#888'
        }))
    ])
], fluid=True)

# Callbacks
@app.callback(
    Output('organization-dropdown', 'options'),
    Input('enforcement-type-dropdown', 'value')
)
def update_organization_options(enforcement_type):
    if enforcement_type:
        filtered_data = data[data['Enforcement Type'] == enforcement_type]
        organizations = filtered_data['Organization'].unique()
    else:
        organizations = data['Organization'].unique()
    return [{'label': org, 'value': org} for org in organizations]

@app.callback(
    Output('month-dropdown', 'options'),
    [Input('enforcement-type-dropdown', 'value'),
     Input('organization-dropdown', 'value')]
)
def update_month_options(enforcement_type, organization):
    filtered_data = data.copy()
    if enforcement_type:
        filtered_data = filtered_data[filtered_data['Enforcement Type'] == enforcement_type]
    if organization:
        filtered_data = filtered_data[filtered_data['Organization'] == organization]
    months = filtered_data['Month Fined'].unique()
    return [{'label': month, 'value': month} for month in months]

@app.callback(
    [Output('organization-count', 'children'),
     Output('total-fines', 'children')],
    [Input('enforcement-type-dropdown', 'value'),
     Input('organization-dropdown', 'value'),
     Input('month-dropdown', 'value')]
)
def update_metrics(enforcement_type, organization, month):
    filtered_data = data.copy()
    if enforcement_type:
        filtered_data = filtered_data[filtered_data['Enforcement Type'] == enforcement_type]
    if organization:
        filtered_data = filtered_data[filtered_data['Organization'] == organization]
    if month:
        filtered_data = filtered_data[filtered_data['Month Fined'] == month]
    org_count = filtered_data['Organization'].nunique()
    total_fines = filtered_data['Fined Value'].sum()
    return f"Number of Organizations: {org_count}", f"Total Fines: ${total_fines:,.2f}"

@app.callback(
    Output('fines-bar-chart', 'figure'),
    [Input('enforcement-type-dropdown', 'value'),
     Input('organization-dropdown', 'value')]
)
def update_bar_chart(enforcement_type, organization):
    filtered_data = data.copy()
    if enforcement_type:
        filtered_data = filtered_data[filtered_data['Enforcement Type'] == enforcement_type]
    if organization:
        filtered_data = filtered_data[filtered_data['Organization'] == organization]
    if filtered_data.empty:
        return px.bar(title="No data available")
    fines_by_org = filtered_data.groupby('Organization')['Fined Value'].sum().reset_index()
    fines_by_org = fines_by_org.sort_values(by='Fined Value', ascending=False)
    fig = px.bar(fines_by_org, x='Organization', y='Fined Value', title="Fined Value by Organization")
    fig.update_layout(plot_bgcolor='#f7f9fc', paper_bgcolor='#f7f9fc', font_color='#2c3e50')
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

