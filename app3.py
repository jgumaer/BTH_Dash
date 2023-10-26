import dash
from dash import Dash, dash_table, dcc, html, Input, Output, callback, State
import pandas as pd
import numpy as np
import geopandas as gdp
import plotly.express as px
import dash_bootstrap_components as dbc
from urllib.request import urlopen
import json
from PIL import Image
import plotly.io as pio
import io
import base64

response = urlopen('https://raw.githubusercontent.com/jgumaer/BTH_Dash/main/richmond.geojson')
geojson = json.loads(response.read())
gdf = gdp.read_file('https://raw.githubusercontent.com/jgumaer/BTH_Dash/main/richmond.geojson')
gdf_trees = gdp.read_file('https://raw.githubusercontent.com/jgumaer/BTH_Dash/main/trees2.geojson')
tree_response = urlopen('https://raw.githubusercontent.com/jgumaer/BTH_Dash/main/trees2.geojson')
geojson_tree = json.loads(tree_response.read())

df = pd.DataFrame()
df['PER_O65'] = pd.qcut(gdf['PER_O65'],5,labels=False)
df['PER_NW'] = pd.qcut(gdf['PER_NW'],5,labels=False)
df['PER_NO_HS_'] = pd.qcut(gdf['PER_NO_HS_'],5,labels=False)
df['PER_HH_ALO'] = pd.qcut(gdf['PER_HH_ALO'],5,labels=False)
df['HH_LMTD_EN'] = pd.qcut(gdf['HH_LMTD_EN'],5,labels=False,duplicates='drop')
df['PER_HH_POV'] = pd.qcut(gdf['PER_HH_POV'],5,labels=False)
df['PER_u5'] = pd.qcut(gdf['PER_u5'],5,labels=False)

df_temp = pd.DataFrame()
df_temp['BGavgam'] = pd.qcut(gdf['BGavgam'],5,labels=False)
df_temp['BGavgaf'] = pd.qcut(gdf['BGavgaf'],5,labels=False)
df_temp['BGavgpm'] = pd.qcut(gdf['BGavgpm'],5,labels=False)

# .apply(lambda x: 1 if x == pd.qcut(gdf['PER_O65'],5,labels=False).max() else 0)

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
        dbc.Checklist(
            options=[
                {"label": "Percent of Population over 65", "value": "PER_O65"},
                {"label": "Percent of the Population under the age of 5", "value": "PER_u5"},
                {"label": "Percent of Households with someone over the age of 65 living alone", "value": "PER_HH_ALO"},
                {"label": "Percent of Population other than White", "value": "PER_NW"},
                {"label": "Percent of Households with Limited English", "value": "HH_LMTD_EN"},
                {"label": "Percent of Households under the Poverty line in the past 12 months", "value": "PER_HH_POV"},
                {"label": "Percent of Population over 25 without HS Diploma", "value": "PER_NO_HS_"}
            ],
            value=["PER_O65"],
            id="switches-input",
            switch=True,
        )
    ],title="Susceptibility"
    )
]
)

temp_selection = dbc.Accordion([
    dbc.AccordionItem([
        dbc.Checklist(
            options =[
                {"label": "Block Group Average Morning Temperature", "value":"BGavgam"},
                {"label": "Block Group Average Afternoon Temperature", "value":"BGavgaf"},
                {"label": "Block Group Average Evening Temperature", "value":"BGavgpm"}
            ],
            value = ["BGavgam"],
            id="temp-switch",
            switch=True,
        )

    ],title="Exposure")

])

map = dcc.Graph(figure=graph_map(), id='ch_map')

priority_check = dbc.Checklist(
    options = [{'label':'Priority','value':1}],
    value = [],
    id = 'pri-check',
    switch=True
)

store_button = dbc.Button("Store Image", id="store-button",n_clicks=0)

image_store = html.Div([
    dcc.Store(id='image-store',data=None),
    html.Img(id='display-image')   
]
)



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

app.layout = html.Div(dbc.Row([dbc.Col([feature_selection,temp_selection],width=5),dbc.Col([map,priority_check,store_button,image_store],width=5)]))

@app.callback(
    Output('ch_map','figure'),
    Input('switches-input','value'),
    Input('temp-switch','value'),
    Input('pri-check','value')
)

def plot_index(check_v,temp_v,pri_v):
    
    
    df_quant = df[check_v]
    
    demo_list = df_quant.sum(axis=1)
    demo_list -= demo_list.min()
    demo_list /= demo_list.max() + .000001
    
    df_temp_quant = df_temp[temp_v]

    temp_list = df_temp_quant.sum(axis=1)
    temp_list -= temp_list.min()
    temp_list /= temp_list.max() + .000001

    

    gdf['INDEX'] = np.round(demo_list + temp_list,3)

    gdf['Demo_Pri'] = (demo_list >= demo_list.quantile(.80)).astype(int)
    gdf['Temp_Pri'] = (temp_list >= temp_list.quantile(.80)).astype(int)

    gdf['PRIORITY'] = gdf['Demo_Pri'] + gdf['Temp_Pri']
    #gdf['PRIORITY'] = gdf['INDEX'].apply(lambda x: 1 if x == pd.qcut(gdf['INDEX'],5,labels=False,duplicates='drop').max() else 0)

    if len(pri_v) == 0:
        return graph_map('INDEX')
    
    else:
        return graph_map('PRIORITY')

@app.callback(
    Output('image-store','data'),
    Output('store-button','n_clicks'),
    Input('store-button','n_clicks'),
    Input('ch_map','figure')
)

def create_and_store_image(n_clicks, figure):
    if n_clicks == 0:
        raise dash.exceptions.PreventUpdate
    
    img_bytes = pio.to_image(figure, format="png")
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')

    return img_base64, 0

@app.callback(
    Output('display-image', 'src'),
    Input('image-store', 'data'),
    Input('store-button', 'n_clicks')
)
def display_stored_image(image_data, n_clicks):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate
    
    if image_data is not None:
        return f'data:image/png;base64,{image_data}'
    else:
        return ''


if __name__ == "__main__":
    app.run_server(debug=True)