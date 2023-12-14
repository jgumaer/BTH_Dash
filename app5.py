import dash
from dash import Dash, dash_table, dcc, html, Input, Output, callback, State
import pandas as pd
import numpy as np
import geopandas as gdp
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from urllib.request import urlopen
import json
from PIL import Image
import plotly.io as pio
import io
import base64
import censusgeocode as cg

response = urlopen('https://raw.githubusercontent.com/jgumaer/BTH_Dash/main/richmond_block.geojson')
geojson = json.loads(response.read())
gdf = gdp.read_file('https://raw.githubusercontent.com/jgumaer/BTH_Dash/main/richmond_block.geojson')
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
df_temp["AVG_AM_TEMP"] = pd.qcut(gdf["AVG_AM_TEMP"], 5, labels=False)
df_temp["AVG_AF_TEMP"] = pd.qcut(gdf["AVG_AF_TEMP"], 5, labels=False)
#df_temp["AVG_PM_TEMP"] = pd.qcut(gdf["AVG_PM_TEMP"], 5, labels=False)
df_temp["AVG_AM_HI"] = pd.qcut(gdf["AVG_AM_HI"], 5, labels=False)
df_temp["AVG_AF_HI"] = pd.qcut(gdf["AVG_AF_HI"], 5, labels=False)
df_temp["AVG_PM_HI"] = pd.qcut(gdf["AVG_PM_HI"], 5, labels=False)

# .apply(lambda x: 1 if x == pd.qcut(gdf['PER_O65'],5,labels=False).max() else 0)

def graph_map(indicator='PER_O65',layer=[]):
    fig = px.choropleth_mapbox(gdf, geojson=geojson, color=indicator,
                           featureidkey="properties.GEOID20",
                           locations="GEOID20",
                           color_continuous_scale="Viridis",
                           mapbox_style="carto-positron",
                           zoom=11, center = {"lat": 39.8289, "lon": -84.8902},
                           opacity=0.3
                          )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
    if len(layer) > 1:
        lat = layer[0]
        lon = layer[1]

        point_trace = go.Scattermapbox(
            lat=[lat],
            lon=[lon],
            mode='markers',
            text="texts",
            marker_size=10,
            marker_color='rgb(235, 0, 100)'
        )

        fig.add_trace(point_trace)
    return fig

def address_code(add_v):
    results = cg.address(add_v, city='Richmond', state='IN')
    block = results[0]['geographies']['2020 Census Blocks'][0]['GEOID']
    coordinates = results[0]['coordinates']

    coord_list = [coordinates['y'],coordinates['x']]

    text_list = [block,coord_list]

    return text_list

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
                {"label": "Average Morning Temperature", "value":"AVG_AM_TEMP"},
                {"label": "Average Afternoon Temperature", "value":"AVG_AF_TEMP"},
                {"label": "Average Evening Temperature", "value":"AVG_PM_TEMP", "disabled": True},
                {"label": "Average Morning Heat Index", "value":"AVG_AM_HI"},
                {"label": "Average Afternoon Heat Index", "value":"AVG_AF_HI"},
                {"label": "Average Evening Heat Index", "value":"AVG_PM_HI"}
            ],
            value = ["AVG_AM_TEMP"],
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

add_search = html.Div([
    dbc.Input(id="add-input", placeholder="Street Address", type="text", debounce=True),
    html.Br(),
    html.P(id="add-output"),
    dcc.Store(id='coord-store',data=[39.82996991036466, -84.8952663493386])
])

map_explore_1 = dcc.Graph(figure=graph_map(), id='ex_map_1')

map_select_1 = dbc.Select(
    id = 'explore_select_1',
    options=[
        {"label": "Percent of Population over 65", "value": "PER_O65"},
        {"label": "Percent of the Population under the age of 5", "value": "PER_u5"},
        {"label": "Percent of Households with someone over the age of 65 living alone", "value": "PER_HH_ALO"},
        {"label": "Percent of Population other than White", "value": "PER_NW"},
        {"label": "Percent of Households with Limited English", "value": "HH_LMTD_EN"},
        {"label": "Percent of Households under the Poverty line in the past 12 months", "value": "PER_HH_POV"},
        {"label": "Percent of Population over 25 without HS Diploma", "value": "PER_NO_HS_"},
        {"label": "Average Morning Temperature", "value":"AVG_AM_TEMP"},
        {"label": "Average Afternoon Temperature", "value":"AVG_AF_TEMP"},
        {"label": "Average Evening Temperature", "value":"AVG_PM_TEMP", "disabled": True},
        {"label": "Average Morning Heat Index", "value":"AVG_AM_HI"},
        {"label": "Average Afternoon Heat Index", "value":"AVG_AF_HI"},
        {"label": "Average Evening Heat Index", "value":"AVG_PM_HI"}
    ],
    value=["PER_O65"]
)

map_explore_2 = dcc.Graph(figure=graph_map(), id='ex_map_2')

map_select_2 = dbc.Select(
    id = 'explore_select_2',
    options=[
        {"label": "Percent of Population over 65", "value": "PER_O65"},
        {"label": "Percent of the Population under the age of 5", "value": "PER_u5"},
        {"label": "Percent of Households with someone over the age of 65 living alone", "value": "PER_HH_ALO"},
        {"label": "Percent of Population other than White", "value": "PER_NW"},
        {"label": "Percent of Households with Limited English", "value": "HH_LMTD_EN"},
        {"label": "Percent of Households under the Poverty line in the past 12 months", "value": "PER_HH_POV"},
        {"label": "Percent of Population over 25 without HS Diploma", "value": "PER_NO_HS_"},
        {"label": "Average Morning Temperature", "value":"AVG_AM_TEMP"},
        {"label": "Average Afternoon Temperature", "value":"AVG_AF_TEMP"},
        {"label": "Average Evening Temperature", "value":"AVG_PM_TEMP", "disabled": True},
        {"label": "Average Morning Heat Index", "value":"AVG_AM_HI"},
        {"label": "Average Afternoon Heat Index", "value":"AVG_AF_HI"},
        {"label": "Average Evening Heat Index", "value":"AVG_PM_HI"}
    ],
    value=["PER_O65"]
)

tab_content_1 = html.Div(dbc.Row([dbc.Col([feature_selection,temp_selection,add_search],width=5),dbc.Col([map,priority_check,store_button,image_store],width=5)]))

tab_content_2 = html.Div(dbc.Row([dbc.Col([map_select_1,map_explore_1]),dbc.Col([map_select_2,map_explore_2])]))

tabs = dbc.Tabs(
    [
        dbc.Tab(tab_content_1, label='Index'),
        dbc.Tab(tab_content_2, label='Explorer')
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

app.layout = tabs

@app.callback(
    Output('add-output','children'),
    Output('coord-store','data'),
    Input("add-input","value")
)
def display_input_text(text_v):
    if text_v is not None:  
        block = address_code(text_v)[0]
        coord_list = address_code(text_v)[1]  
        return str(block) + "  " + str(coord_list), coord_list
    else:
        return 'No Address', []

@app.callback(
    Output('ch_map','figure'),
    Input('switches-input','value'),
    Input('temp-switch','value'),
    Input('pri-check','value'),
    Input('coord-store','data')
)

def plot_index(check_v,temp_v,pri_v,layer_v):
    
    
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
        return graph_map('INDEX',layer_v)
    
    else:
        return graph_map('PRIORITY',layer_v)

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

@app.callback(
    Output('ex_map_1','figure'),
    Input('explore_select_1','value')
)

def explore_map_select_1(val):
    return graph_map(val)

@app.callback(
    Output('ex_map_2','figure'),
    Input('explore_select_2','value')
)

def explore_map_select_2(val):
    return graph_map(val)


if __name__ == "__main__":
    app.run_server(debug=True)