import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
from dash import no_update
from dash.dependencies import Input, Output, State
import plotly.express as px
from plotly import graph_objs as go

# Leer datos preprocesados
df_precioProm = pd.read_csv('data/output.csv', index_col=0)
df_promRec = pd.read_csv('data/promRec.csv')
df_promRec.reset_index(drop=True, inplace=True)

# get data from the dataframe to be used in the layout
import numpy as np
ciudades = df_precioProm['ciudad'].unique()
ciudades = np.sort(ciudades)
ciudades_dict =[{"label": k, "value": k} for k in ciudades]
productos = df_precioProm['producto'].unique()
productos = np.sort(productos)
productos_dict =[{"label": k, "value": k} for k in productos]
controls = dbc.Row([
        dbc.Col(
            dbc.Card(
              dbc.CardBody(
                  [
                      dcc.Dropdown(
                                  id='prod-dropdown',
                                  options=productos_dict,
                                  value=productos[0]
                              ),
                  ]
              ),
          ),
          md=6
        ),
        dbc.Col(
            dbc.Card(
              dbc.CardBody(
                  [
                      dcc.Dropdown(
                                  id='city-dropdown',
                                  options=ciudades_dict,
                                  value=ciudades[0]
                              ),
                  ]
              ),
          ),
          md=6
        ),
    ]
)


# Define the stylesheets
external_stylesheets = [dbc.themes.BOOTSTRAP,
    #'https://codepen.io/chriddyp/pen/bWLwgP.css'
    'https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap',
    #'https://fonts.googleapis.com/css2?family=Roboto&display=swap" rel="stylesheet'
]

# Creates the app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                title="dash_board",
                suppress_callback_exceptions=True)


# Define Layout
app.layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row([html.Img(src='assets/images/imagenBanner_Zonificacion1.jpg',
                         style={'width':'100%'}),
                 html.P(" Este es un texto de ensayo")]),
        dbc.Row([
            dbc.Col(
                dcc.Dropdown(
                    id='prod-dropdown',
                    options=productos_dict,
                    value=productos[0]),
                width=6),
            dbc.Col(
             dcc.Dropdown(
                 id='city-dropdown',
                 options=ciudades_dict,
                 value=ciudades[0]),
                width=6)
            ],
            style={'marginTop': 10,
                   'marginBottom': 10}),
        dbc.Row(
            dbc.Col(dcc.Graph(id="line_graph"), width=12)
        ),
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id='prod2-dropdown',
                    options=productos_dict,
                    value=productos[0]),
                dcc.DatePickerSingle(
                    id='date-picker',
                    min_date_allowed=df_promRec['enmaFecha'].min(),
                    max_date_allowed=df_promRec['enmaFecha'].max(),
                    initial_visible_month=df_promRec['enmaFecha'].min(),
                    date=df_promRec['enmaFecha'].max(),
                    display_format='DD/MM/YYYY',
                ),
            ],
                width=4),
            dbc.Col(dcc.Graph(id="map_graph"), width=8)]
        )

    ],
)

# Callback to update the graph
@app.callback(
    Output('line_graph', 'figure'),
    Input(component_id='prod-dropdown', component_property='value'),
    Input(component_id='city-dropdown', component_property='value')
    )
def crear_figura(producto, ciudad):
    # filtra el dataframe
    df_filtered = df_precioProm[(df_precioProm['producto'] == producto) & (df_precioProm['ciudad'] == ciudad)][['fechaCaptura', 'precioPromedio']]

    # Sort the values based on recording data
    df_filtered.sort_values(by=['fechaCaptura'], inplace=True)

    # create the figure
    fig = px.line(df_filtered, x='fechaCaptura', y='precioPromedio',
                  title="Precio por kg de {} en las distintas plazas de mercado".format(producto),
                  labels={'value': 'precio (kg)',
                          'fechaCaptura': 'Fecha registro'}
                  )
    df_filtered.sort_values(by=['fechaCaptura'], inplace=True)
    return fig

# Callback to update the graph
@app.callback(
    Output('map_graph', 'figure'),
    Input(component_id='prod2-dropdown', component_property='value'),
    Input(component_id='date-picker', component_property='date')
    )
def crear_mapa(producto, fecha):
    # Filtra datos
    df_filtered = df_promRec[(df_promRec['enmaFecha'] == fecha) & (df_promRec['artiNombre'] == producto)][
        ['fuenNombre', 'promedioKg', 'LATITUD', 'LONGITUD']]
    df_filtered.reset_index(inplace=True)
    # Agregamos una columna que indique la razon de cada cantidad recogida respecto al valor máximo
    maxRec = df_filtered['promedioKg'].max() / 50
    df_filtered['size'] = df_filtered['promedioKg'] / maxRec

    map = go.Figure()

    map.add_trace(go.Scattermapbox(
        lat=df_filtered['LATITUD'],
        lon=df_filtered['LONGITUD'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=df_filtered['size'],
            color='yellow',
            opacity=0.5
        ),
        text=df_filtered['fuenNombre'],
        hoverinfo='text',
        name="producción"
    ))

    # Actualizamos el layout indicandole el estilo de mapa y algunas propiedades
    map.update_layout(
        mapbox_style="open-street-map",
        autosize=True,
        hovermode='closest',
        showlegend=True,
        height=600
    )

    # Centramos el mapa y le damos el zoom apropiado
    map.update_mapboxes(
        center=go.layout.mapbox.Center(
            lat=df_filtered.loc[0, 'LATITUD'],
            lon=df_filtered.loc[0, 'LONGITUD'],
        ),
        zoom=5
    ),

    return map

# main to run the app
if __name__ == "__main__":
    app.run_server(debug=True)