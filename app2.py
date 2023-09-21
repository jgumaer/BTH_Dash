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

df = pd.DataFrame()
df['BGavgam'] = gdf['BGavgam']
df['BGavgaf'] = gdf['BGavgaf']
df['BGavgpm'] = gdf['BGavgpm']
df['PER_O65'] = gdf['PER_O65']
df['PER_NW'] = gdf['PER_NW']
df['PER_NO_HS_'] = gdf['PER_NO_HS_']
df['PER_HH_ALO'] = gdf['PER_HH_ALO']
df['HH_LMTD_EN'] = gdf['HH_LMTD_EN']
df['PER_HH_POV'] = gdf['PER_HH_POV']
df['PER_u5'] = gdf['PER_u5']



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

feature_selection = dbc.Accordion([
    dbc.AccordionItem([
        html.P("Average Morning Temperature"),
        dcc.Slider(
            min=0,
            max=100,
            step=10,
            value=50,
            id='avg-morn-temp'
        ),
        html.P("Average Afternoon Temperature"),
        dcc.Slider(
            min=0,
            max=100,
            step=10,
            value=50,
            id='avg-aft-temp'
        ),
        html.P("Average Evening Temperature"),
        dcc.Slider(
            min=0,
            max=100,
            step=10,
            value=50,
            id='avg-even-temp'
        )
    ],title="Temperature"

    ),
    dbc.AccordionItem([
        html.P("Percent of Population over 65"),
        dcc.Slider(
            min=0,
            max=100,
            step=10,
            value=50,
            id='pop-over-65'
        ),
        html.P("Percent of Population other than White"),
        dcc.Slider(
            min=0,
            max=100,
            step=10,
            value=50,
            id='pop-other-white'
        ),
        html.P("Percent of Population over 25 without HS Diploma"),
        dcc.Slider(
            min=0,
            max=100,
            step=10,
            value=50,
            id='pop-no-hs'
        ),
        html.P("Percent of Households with someone over the age of 65 living alone"),
        dcc.Slider(
            min=0,
            max=100,
            step=10,
            value=50,
            id='pop-living-65'
        ),
        html.P("Percent of Households with Limited English"),
        dcc.Slider(
            min=0,
            max=100,
            step=10,
            value=50,
            id='pop-limit-eng'
        ),
        html.P("Percent of Households under the Poverty line in the past 12 months"),
        dcc.Slider(
            min=0,
            max=100,
            step=10,
            value=50,
            id='pop-poverty'
        ),
        html.P("Percent of the Population under the age of 5"),
        dcc.Slider(
            min=0,
            max=100,
            step=10,
            value=50,
            id='pop-under-5'
        ),
    ],title="Demographics"
    )
],start_collapsed=True
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

app.layout = html.Div(dbc.Row([dbc.Col(feature_selection,width=5),dbc.Col(map,width=5)]))

@app.callback(
    Output('ch_map','figure'),
    Input('avg-morn-temp','value'),
    Input('avg-aft-temp','value'),
    Input('avg-even-temp','value'),
    Input('pop-over-65','value'),
    Input('pop-other-white','value'),
    Input('pop-no-hs','value'),
    Input('pop-living-65','value'),
    Input('pop-limit-eng','value'),
    Input('pop-poverty','value'),
    Input('pop-under-5','value'),
)

def plot_index(avg_m,avg_a,avg_e,pop_65,pop_nw,pop_hs,pop_living_65,pop_eng,pop_pov,pop_5):
    lst = [avg_m,avg_a,avg_e,pop_65,pop_nw,pop_hs,pop_living_65,pop_eng,pop_pov,pop_5]
    weight_vec = np.array(lst)/100
    gdf['INDEX'] = df.dot(weight_vec)



    return graph_map('INDEX')

if __name__ == "__main__":
    app.run_server(debug=True)