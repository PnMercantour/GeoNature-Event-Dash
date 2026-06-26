from typing import List
from datetime import datetime
from dash import Dash, html, dcc, callback, Output, Input, dash_table, ctx
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.javascript import assign

import plotly.express as px

import pandas as pd

from layouts import card
from style_config import (
    TABLE_STYLE_CELL,
    TABLE_STYLE_HEADER,
    TABLE_STYLE_DATA,
    style_pie_chart,
    HERO_TITLE_TEXT,
    HERO_KICKER_TEXT,
    HERO_SUBTITLE_TEXT,
    HERO_LOGO_SRC,
    HERO_LOGO_ALT,
)

from queries import (
    get_total_obs,
    get_new_species,
    get_new_species_commune,
    get_all_data_geo,
    get_species_in_event,
    get_group2_inpn,
    get_group3_inpn,
    get_ordres,
    get_familles,
    get_observers,
    get_communal_limit,
    get_communal_bounds
)
from utils import format_columns, pointToLayer
from config import *


app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = EVENT_TITLE


# observations
observation_geom = get_all_data_geo()
limit_commune = get_communal_limit()
communal_bounds = get_communal_bounds()


def build_pie_chart(data, title, names_column="group2_inpn"):
    df = pd.DataFrame.from_records(data)
    if df.empty:
        fig = px.pie(names=["Aucune donnee"], values=[1], hole=0.3)
    else:
        if names_column not in df.columns:
            names_column = "group2_inpn"
        fig = px.pie(df, names=names_column, hole=0.3)
    return style_pie_chart(fig, title)


######################
##### GLOBAL vars ####
######################

def refresh_data_cache():
    global g_species_in_event
    global species_in_event_df
    global g_new_species_commune
    global new_species_commune_df
    global g_new_species
    global new_species_df
    global observation_geom
    global observers
    global last_sync_label

    g_species_in_event = get_species_in_event()
    species_in_event_df = pd.DataFrame.from_dict(g_species_in_event)

    g_new_species_commune = get_new_species_commune()
    new_species_commune_df = pd.DataFrame.from_dict(g_new_species_commune)

    g_new_species = get_new_species()
    new_species_df = pd.DataFrame.from_dict(g_new_species)

    observation_geom = get_all_data_geo()

    observers = get_observers()
    last_sync_label = f"Derniere synchronisation: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


refresh_data_cache()

species_event_chart = build_pie_chart(g_species_in_event, "Répartition des taxons observés")
new_species_commune_chart = build_pie_chart(g_new_species_commune, "Nouveautés sur la commune")
new_species_chart = build_pie_chart(g_new_species, "Nouveautés pour le Parc")


app.layout = dbc.Container(
    [
        html.Div(
            className="hero-banner",
            children=[
                html.Div(
                    className="hero-content",
                    children=[
                        
                        html.Div(
                            className="hero-copy",
                            children=[
                                html.Span(HERO_KICKER_TEXT, className="hero-kicker"),
                                html.H1(HERO_TITLE_TEXT, className="hero-title"),
                                html.P(
                                    HERO_SUBTITLE_TEXT,
                                    className="hero-subtitle",
                                ),
                            ],
                        ),
                        html.Div(
                            className="hero-logo-wrap",
                            children=[
                                html.Img(
                                    src=HERO_LOGO_SRC,
                                    alt=HERO_LOGO_ALT,
                                    className="hero-logo",
                                )
                            ],
                        ),
                    ],
                )
            ],
        ),
        html.Div(
            className="filter-panel",
            children=[
                html.H2("Explorer les observations", className="panel-title"),
                html.P(
                    "Affinez la lecture par grands groupes, ordres ou familles pour faire ressortir les dynamiques de l'événement.",
                    className="panel-intro",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Dropdown(
                                get_group2_inpn(),
                                id="group2-dropdown",
                                clearable=True,
                                placeholder="Filtrer par groupe 2 INPN",
                                className="mb-3 mb-lg-0",
                            ),
                            md=3,
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                get_group3_inpn(),
                                id="group3-dropdown",
                                clearable=True,
                                placeholder="Filtrer par groupe 3 INPN",
                                className="mb-3 mb-lg-0",
                            ),
                            md=3,
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                get_ordres(),
                                id="ordre-dropdown",
                                clearable=True,
                                placeholder="Filtrer par ordre",
                                className="mb-3 mb-lg-0",
                            ),
                            md=3,
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                get_familles(),
                                id="famille-dropdown",
                                clearable=True,
                                placeholder="Filtrer par famille",
                            ),
                            md=3,
                        ),
                    ]
                ),
                dbc.Row(
                    className="g-2 mt-3 align-items-center",
                    children=[
                        dbc.Col(
                            dbc.Button(
                                "Synchroniser",
                                id="sync-button",
                                color="success",
                                n_clicks=0,
                            ),
                            width="auto",
                        ),
                        dbc.Col(
                            html.Small(
                                last_sync_label,
                                id="sync-status",
                                className="text-muted",
                            ),
                            width="auto",
                        ),
                    ],
                ),
            ],
        ),
        dbc.Row(
            className="metrics-row",
            children=[
                dbc.Col(card("Nombre de données", "", id="nb_data"), xl=3, md=6),
                dbc.Col(card("Nombre de taxons", "", id="nb_species"), xl=3, md=6),
                dbc.Col(
                    card("Nouveaux taxons pour la commune", "", id="nb_new_species_commune"),
                    xl=3,
                    md=6,
                ),
                dbc.Col(card("Nouveaux taxons pour le Parc", "", id="nb_new_species_pne"), xl=3, md=6),
            ],
        ),
        html.Div(
            className="section-panel",
            children=[
                html.H2("Taxons observés pendant l'événement", className="panel-title"),
                dbc.Row(
                    className="section-grid g-4",
                    children=[
                        dbc.Col(
                            dash_table.DataTable(
                                data=[],
                                columns=format_columns(g_species_in_event),
                                page_size=15,
                                sort_action="native",
                                id="datable_species",
                                markdown_options={"html": True},
                                style_cell=TABLE_STYLE_CELL,
                                style_header=TABLE_STYLE_HEADER,
                                style_data=TABLE_STYLE_DATA,
                                style_table={"overflowX": "auto"},
                            ),
                            lg=7,
                        ),
                        dbc.Col(
                            dcc.Graph(
                                id="species-event-chart",
                                figure=species_event_chart,
                                className="chart-wrap",
                                config={"displayModeBar": False},
                                style={"height": "100%", "minHeight": "420px"},
                            ),
                            lg=5,
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            className="section-panel",
            children=[
                html.H2("Nouveaux taxons sur la commune", className="panel-title"),
                dbc.Row(
                    className="section-grid g-4",
                    children=[
                        dbc.Col(
                            dash_table.DataTable(
                                data=[],
                                columns=format_columns(g_new_species_commune),
                                page_size=15,
                                sort_action="native",
                                id="datable_new_species_commune",
                                markdown_options={"html": True},
                                style_cell=TABLE_STYLE_CELL,
                                style_header=TABLE_STYLE_HEADER,
                                style_data=TABLE_STYLE_DATA,
                                style_table={"overflowX": "auto"},
                            ),
                            lg=7,
                        ),
                        dbc.Col(
                            dcc.Graph(
                                id="new-species-commune-chart",
                                figure=new_species_commune_chart,
                                className="chart-wrap",
                                config={"displayModeBar": False},
                                style={"height": "100%", "minHeight": "420px"},
                            ),
                            lg=5,
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            className="section-panel",
            children=[
                html.H2("Nouveaux taxons pour le Parc", className="panel-title"),
                dbc.Row(
                    className="section-grid g-4",
                    children=[
                        dbc.Col(
                            dash_table.DataTable(
                                data=[],
                                columns=format_columns(g_new_species),
                                page_size=15,
                                sort_action="native",
                                id="new_species_in_structure",
                                markdown_options={"html": True},
                                style_cell=TABLE_STYLE_CELL,
                                style_header=TABLE_STYLE_HEADER,
                                style_data=TABLE_STYLE_DATA,
                                style_table={"overflowX": "auto"},
                            ),
                            lg=7,
                        ),
                        dbc.Col(
                            dcc.Graph(
                                id="new-species-chart",
                                figure=new_species_chart,
                                className="chart-wrap",
                                config={"displayModeBar": False},
                                style={"height": "100%", "minHeight": "420px"},
                            ),
                            lg=5,
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            className="map-panel",
            children=[
                html.H2("Observations durant l'événement", className="panel-title"),
                dl.Map(
                    children=[
                        dl.TileLayer(
                            url="https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&STYLE=normal&TILEMATRIXSET=PM&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&LAYER=GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2&FORMAT=image/png",
                            attribution="&copy; IGN ",
                        ),
                        dl.GeoJSON(data=limit_commune, style=dict(zIndex=500, color="#E61991", fillOpacity=0.1)),
                        dl.GeoJSON(data=observation_geom, id="observations-geojson", cluster=True, pointToLayer=assign(pointToLayer), style=dict(zIndex=100), zoomToBoundsOnClick=True),
                    ],
                    bounds=communal_bounds,
                    zoom=13,
                    style={"height": "80vh"},
                    className="mb-0",
                ),
            ],
        ),
        html.Div(
            className="observers-panel",
            children=[
                html.H2(
                    f"{len(observers)} observateurs mobilisés",
                    className="panel-title",
                    id="observers-title",
                ),
                dash_table.DataTable(
                    data=observers,
                    page_size=15,
                    sort_action="native",
                    id="observers",
                    style_cell=TABLE_STYLE_CELL,
                    style_header=TABLE_STYLE_HEADER,
                    style_data=TABLE_STYLE_DATA,
                    style_table={"overflowX": "auto"},
                ),
            ],
        ),
    ],
    fluid=True,
    className="dashboard-shell",
)


def filter_df(df: pd.DataFrame, column: str, value: str) -> List:
    """
    Filter the dataframe in parameter according to column and value
    return a list of dict for Dash Datatable and plots
    """
    filter_df = df[df[column] == value]
    return filter_df.to_dict("records")


def on_update(column, value, group2_value=None):
    chart_group_col = "group3_inpn" if column == "group2_inpn" else "group2_inpn"

    if value:
        filter_species_in_event = filter_df(species_in_event_df, column, value)
        filter_new_species_commune = filter_df(new_species_commune_df, column, value)
        filter_new_species_struct = filter_df(new_species_df, column, value)
        filter_observation_geom = get_all_data_geo(column=column, filter=value)
        return (
            get_total_obs(column=column, filter=value),
            len(filter_species_in_event),
            filter_species_in_event,
            build_pie_chart(filter_species_in_event, "Répartition des taxons observés", chart_group_col),
            len(filter_new_species_commune),
            filter_new_species_commune,
            build_pie_chart(filter_new_species_commune, "Nouveautés sur la commune", chart_group_col),
            len(filter_new_species_struct),
            filter_new_species_struct,
            build_pie_chart(filter_new_species_struct, "Nouveautés pour le Parc", chart_group_col),
            filter_observation_geom,
            observers,
            f"{len(observers)} observateurs mobilisés",
            get_group2_inpn(),
            get_group3_inpn(group2_value),
            get_ordres(),
            get_familles(),
            last_sync_label,
        )
    else:
        return (
            get_total_obs(),
            len(species_in_event_df),
            g_species_in_event,
            species_event_chart,
            len(new_species_commune_df),
            g_new_species_commune,
            new_species_commune_chart,
            len(g_new_species),
            g_new_species,
            new_species_chart,
            observation_geom,
            observers,
            f"{len(observers)} observateurs mobilisés",
            get_group2_inpn(),
            get_group3_inpn(group2_value),
            get_ordres(),
            get_familles(),
            last_sync_label,
        )


@callback(
    [
        Output(component_id="nb_data", component_property="children"),
        Output(component_id="nb_species", component_property="children"),
        Output("datable_species", "data"),
        Output("species-event-chart", "figure"),
        Output("nb_new_species_commune", "children"),
        Output("datable_new_species_commune", "data"),
        Output("new-species-commune-chart", "figure"),
        Output("nb_new_species_pne", "children"),
        Output("new_species_in_structure", "data"),
        Output("new-species-chart", "figure"),
        Output("observations-geojson", "data"),
        Output("observers", "data"),
        Output("observers-title", "children"),
        Output("group2-dropdown", "options"),
        Output("group3-dropdown", "options"),
        Output("ordre-dropdown", "options"),
        Output("famille-dropdown", "options"),
        Output("sync-status", "children"),
    ],
    [
        Input("group2-dropdown", "value"),
        Input("group3-dropdown", "value"),
        Input("ordre-dropdown", "value"),
        Input("famille-dropdown", "value"),
        Input("sync-button", "n_clicks"),
    ],
)
def update_output_div(group2, group3, ordre, famille, _sync_clicks):
    if ctx.triggered_id == "sync-button":
        refresh_data_cache()

    if famille:
        return on_update("famille", famille, group2)
    elif ordre:
        return on_update("ordre", ordre, group2)
    elif group3:
        return on_update("group3_inpn", group3, group2)
    elif group2:
        return on_update("group2_inpn", group2, group2)
    else:
        return on_update(None, None, group2)


if __name__ == "__main__":
    app.run(debug=True)
