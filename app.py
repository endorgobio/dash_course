import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import numpy as np
from dash.dependencies import Input, Output
import plotly.express as px
from plotly import graph_objs as go

# Leer datos preprocesados
df_precioProm = pd.read_csv(r'https://raw.githubusercontent.com/endorgobio/dash_course/master/data/output.csv', index_col=0)
df_promRec = pd.read_csv(r'https://raw.githubusercontent.com/endorgobio/dash_course/master/data/promRec.csv')
df_promRec.reset_index(drop=True, inplace=True)

# obetner listas para usar en el layout
ciudades = df_precioProm['ciudad'].unique()
ciudades = np.sort(ciudades)
ciudades_dict =[{"label": k, "value": k} for k in ciudades]
productos = df_precioProm['producto'].unique()
productos = np.sort(productos)
productos_dict =[{"label": k, "value": k} for k in productos]


# Define stylesheets
# Aquí deben adicionarse algunos estilos que deseen adicionarse
external_stylesheets = [dbc.themes.BOOTSTRAP,]

# Crea la app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                title="dash_board",
                suppress_callback_exceptions=True)


# Define el layout
app.layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row([html.Img(src='assets/images/heading.png',
                         style={'width':'100%'}),
                 html.P(" Esta es una herramienta interactiva que permite visualizar la información de precios "
                        "y cantidades de los distintos productos comercializados en las centrales mayoristas "
                        "del país. La información es tomada del SIPSA. Esta plataforma es administrada por el "
                        "Departamento Administrativo Nacional de Estadística ( DANE) y recopila información "
                        "que diariamente se registra desde las centales de abastos",
                        style={'margin':30,
                               'padding': 10})]),
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
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.P('Las cantidades comercializadas en cada central '
                                   'de abastos son de interes para tener una idea de '
                                   'la oferta de productos agrícolas en el país.'
                                   'Seleccione un producto y la fecha para la que '
                                   'desea conocer la cantidad comercializada')
                        ]
                    ),
                ),
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
                    style={'marginTop': 10,
                           'marginBottom': 10,
                           'align': 'center'})
                ],
                width=4),
            dbc.Col(dcc.Graph(id="map_graph"), width=8)],
            align='center',
            justify='center'
        ),
        dbc.Row(html.Img(src='assets/images/footnote.png', style={'width':'100%'})),

    ],
)

# Callback para actualizar gráfico de línea
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
                  labels={'precioPromedio': 'precio (kg)',
                          'fechaCaptura': 'Fecha registro'}
                  )
    fig.update_layout(title_x=0.5)
    df_filtered.sort_values(by=['fechaCaptura'], inplace=True)
    return fig

# Callback para actualizar mapa
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
    # Crea el mapa
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