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
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = "Enforcement Action Analysis"

# Navbar with Datsura Inc. logo on the right
navbar = dbc.Navbar(
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H2("Enforcement Action Analysis", style={'color': 'white', 'fontSize': '24px'})),
        ]),
        dbc.Row([
            dbc.Col(html.Img(src="https://via.placeholder.com/150x50.png?text=Datsura+Inc", height="40px"), width="auto"),
        ], className="ms-auto")  # Push the logo to the right
    ]),
    color="dark",
    dark=True,
    style={'marginBottom': '20px'}
)

# Layout
app.layout = dbc.Container([
    navbar,  # Top navigation bar

    # Filters and Graph (Row 1)
    dbc.Row([
        # Filters Column
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Filters", style={'backgroundColor': '#343a40', 'color': 'white'}),
                dbc.CardBody([
                    dbc.Label("Enforcement Type", style={'color': 'white'}),
                    dcc.Dropdown(
                        id='enforcement-type-dropdown',
                        options=[{'label': etype, 'value': etype} for etype in data['Enforcement Type'].unique()],
                        placeholder="Select Enforcement Type",
                        style={
                            'marginBottom': '10px',
                            'backgroundColor': '#f8f9fa',  # Light background for better contrast
                            'color': 'black',  # Black text for dropdown values
                            'border': '1px solid #495057',
                            'borderRadius': '5px',
                            'padding': '5px'
                        }
                    ),
                    dbc.Label("Organization", style={'color': 'white'}),
                    dcc.Dropdown(
                        id='organization-dropdown',
                        placeholder="Select Organization",
                        style={
                            'marginBottom': '10px',
                            'backgroundColor': '#f8f9fa',
                            'color': 'black',
                            'border': '1px solid #495057',
                            'borderRadius': '5px',
                            'padding': '5px'
                        }
                    ),
                    dbc.Label("Month Fined", style={'color': 'white'}),
                    dcc.Dropdown(
                        id='month-dropdown',
                        placeholder="Select Month Fined",
                        style={
                            'marginBottom': '10px',
                            'backgroundColor': '#f8f9fa',
                            'color': 'black',
                            'border': '1px solid #495057',
                            'borderRadius': '5px',
                            'padding': '5px'
                        }
                    ),
                ])
            ], style={'backgroundColor': '#212529'})
        ], width=3),
        # Graph Column
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Fines by Organization", style={'backgroundColor': '#343a40', 'color': 'white'}),
                dbc.CardBody([
                    dcc.Graph(id='fines-bar-chart', style={'height': '300px'})
                ])
            ], style={'backgroundColor': '#212529'})
        ], width=9),
    ], style={'marginBottom': '20px'}),

    # Metrics and Placeholder (Row 2)
    dbc.Row([
        # Metrics Column
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Key Metrics", style={'backgroundColor': '#343a40', 'color': 'white'}),
                dbc.CardBody([
                    html.Div(id='organization-count', style={'fontSize': '16px', 'color': 'white'}),
                    html.Div(id='total-fines', style={'fontSize': '16px', 'color': 'white'}),
                    html.Div(id='average-fine', style={'fontSize': '16px', 'color': 'white'}),
                    html.Div(id='largest-fine', style={'fontSize': '16px', 'color': 'white'})
                ])
            ], style={'backgroundColor': '#212529'})
        ], width=6),
        # Placeholder Column
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Future Development", style={'backgroundColor': '#343a40', 'color': 'white'}),
                dbc.CardBody("This space is reserved for future upgrades.", style={'color': 'white'})
            ], style={'backgroundColor': '#212529'})
        ], width=6),
    ])
], fluid=True, style={'backgroundColor': '#2c2f33', 'padding': '20px'})

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
     Output('total-fines', 'children'),
     Output('average-fine', 'children'),
     Output('largest-fine', 'children')],
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
    avg_fine = filtered_data['Fined Value'].mean() if not filtered_data.empty else 0
    largest_fine = filtered_data['Fined Value'].max() if not filtered_data.empty else 0
    return (
        f"Number of Organizations: {org_count}",
        f"Total Fines: ${total_fines:,.2f}",
        f"Average Fine: ${avg_fine:,.2f}",
        f"Largest Fine: ${largest_fine:,.2f}"
    )

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
    fig.update_layout(plot_bgcolor='#2c2f33', paper_bgcolor='#2c2f33', font_color='#f8f9fa')
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
