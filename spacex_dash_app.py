# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown', 
                                            options=[
                                                {'label': 'All Sites', 'value': 'ALL'},
                                                {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                                {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                            ],
                                            value='ALL',
                                            placeholder='Select a Launch Site',
                                            searchable=True
                                            ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider', min=0, max=int(1e4), step=int(1e3),
                                                value=[min_payload, max_payload],
                                                marks={x:str(x) for x in range(0,int(1e4),int(1e3))}
                                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # return pie chart with all launch sites
        fig = px.pie(spacex_df, values='class', names='Launch Site', 
                    title='Launch Outcome, All Launch Sites')
    else:
        # return the outcomes piechart for a selected site
        site_df = spacex_df[spacex_df['Launch Site']==entered_site].copy()
        print(spacex_df.shape, site_df.shape)
        site_df['class_name'] = site_df['class'].apply(lambda x : 'Success' if x==1 else 'Failure')
        # Plotly doesn't like plotting values of 0 in a pie chart, so add 1
        site_df['class'] = site_df['class'] + 1
        fig = px.pie(site_df, values='class', names='class_name', 
                    title='Launch Outcome at Launch Site {}'.format(entered_site))
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
# Scatter plot, payload vs class/success
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
            Input(component_id='payload-slider', component_property='value'),
              Input(component_id='site-dropdown', component_property='value'))
def get_payload_scatter(slider_value, selected_site):
    x_min, x_max = slider_value
    df = spacex_df[(spacex_df['Payload Mass (kg)'] >= x_min) & (spacex_df['Payload Mass (kg)'] <= x_max)]
    print(x_min, x_max, df.shape)
    if selected_site == 'ALL':
        fig = px.scatter(df, x='Payload Mass (kg)', y='class', color='Booster Version Category', 
            title='Launch Outcome, All Launch Sites'
        )
    else:
        site_df = df[df['Launch Site']==selected_site]
        fig = px.scatter(site_df, x='Payload Mass (kg)', y='class', color='Booster Version Category', 
            title='Launch Outcome, All Launch Sites'
        )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
