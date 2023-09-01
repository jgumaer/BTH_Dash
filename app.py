import dash
from dash import Dash, dash_table, dcc, html, Input, Output, callback, State
import pandas as pd
import numpy as np
import geopandas as gdp
import plotly.express as px
import dash_bootstrap_components as dbc
from urllib.request import urlopen
import json

with open('richmond.geojson') as response:
    geojson = json.load(response)
gdf = gdp.read_file('richmond.geojson')


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

dropdown = dbc.Select(
    id = 'feature_drop',
    options = [{'label':i,'value':i} for i in list(gdf.columns)],
    value =  'Sensitivit'
)

map = dcc.Graph(figure=graph_map(), id='ch_map')

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

app.layout = html.Div([dropdown,map])

@app.callback(
    Output('ch_map','figure'),
    Input('feature_drop','value')
)

def change_feature(drop_v):
    return graph_map(drop_v)

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=80, debug=True)