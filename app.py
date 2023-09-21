import dash
from dash import Dash, dash_table, dcc, html, Input, Output, callback, State
import pandas as pd
import numpy as np
import geopandas as gdp
import plotly.express as px
import dash_bootstrap_components as dbc
from urllib.request import urlopen
import json

response = urlopen('https://raw.githubusercontent.com/jgumaer/BTH_Dash/main/richmond.geojson')
geojson = json.loads(response.read())
gdf = gdp.read_file('https://raw.githubusercontent.com/jgumaer/BTH_Dash/main/richmond.geojson')
gdf_trees = gdp.read_file('https://raw.githubusercontent.com/jgumaer/BTH_Dash/main/trees2.geojson')
tree_response = urlopen('https://raw.githubusercontent.com/jgumaer/BTH_Dash/main/trees2.geojson')
geojson_tree = json.loads(tree_response.read())

def graph_map(indicator='Sensitivit'):
    fig = px.choropleth_mapbox(gdf, geojson=geojson, color=indicator,
                           featureidkey="properties.NUMGEOID",
                           locations="NUMGEOID",
                           color_continuous_scale="Viridis",
                           mapbox_style="carto-positron",
                           zoom=11, center = {"lat": 39.8289, "lon": -84.8902},
                           opacity=0.3
                          )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
    return fig

dropdown = dbc.Col(dbc.Select(
    id = 'feature_drop',
    options = [{'label':i,'value':i} for i in list(gdf.columns)],
    value =  'Sensitivit'
),width=6)

priority_section = dbc.Col([
    dbc.Accordion(
        dbc.AccordionItem(
            dbc.Col([
                dbc.Row(
                    dbc.Checklist(
                        options = [{'label':'Priority 1', 'value':'1'}],
                        id="priority-1-check",
                        switch=True
                    )
                ),
                dbc.Row(dbc.Col(html.Div(
                    dcc.Slider(
                        min=0,
                        max=100,
                        step=10,
                        value=50
                    ),id="slider-test-1",hidden=True),width=6)
                ),
                dbc.Row(
                    dbc.Checklist(
                        options = [{'label':'Priority 2', 'value':'2'}],
                        id="priority-2-check",
                        switch=True
                    )
                ),
                dbc.Row(dbc.Col(html.Div(
                    dcc.Slider(
                        min=0,
                        max=100,
                        step=10,
                        value=50
                    ),id="slider-test-2",hidden=True),width=6)
                )
            ]),title="Select Priority Areas"
        ),start_collapsed=True
    )
],width=6)

map = dbc.Col(dcc.Graph(figure=graph_map(), id='ch_map'),width=6)

test_text = html.Div(id="text-check")

app = dash.Dash(__name__,
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}, {
                    'http-equiv': 'content-language', 'content': 'en-us'}],
                title="BTH Dashboard",
                external_stylesheets=[dbc.themes.BOOTSTRAP]
                )

server = app.server

app.index_string = '''
<!DOCTYPE html>
<html lang='en'>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = html.Div([priority_section,map,dropdown,test_text])

@app.callback(
    Output('ch_map','figure'),
    Input('feature_drop','value')
)

def change_feature(drop_v):
    return graph_map(drop_v)

@app.callback(
    Output('slider-test-1','hidden'),
    Input('priority-1-check','value')
)

def show_slider_1(check_v):
    if check_v is None:
        return True
    elif check_v == []:
        return True
    else:
        return False
    
@app.callback(
    Output('slider-test-2','hidden'),
    Input('priority-2-check','value')
)

def show_slider_2(check_v):
    if check_v is None:
        return True
    elif check_v == []:
        return True
    else:
        return False

if __name__ == "__main__":
    app.run_server(debug=True)