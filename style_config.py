from config import EVENT_TITLE


MERCANTOUR_COLORS = ["#78B63C", "#4A5C37", "#D7E8EA", "#E6C98A", "#88B7A5", "#C5D4A3"]

HERO_TITLE_TEXT = EVENT_TITLE
HERO_KICKER_TEXT = "Parc national du Mercantour"
HERO_SUBTITLE_TEXT = "Tableau de bord pour explorer les observations realisees lors de l'evenement Explor'Nature."
HERO_LOGO_SRC = "https://media.mercantour.eu/logos/logo_auto-productions_pnm_quadri_txt_vert.png"
HERO_LOGO_ALT = "Logo du Parc national du Mercantour"

TABLE_STYLE_CELL = {
    "textAlign": "left",
    "padding": "12px",
    "fontFamily": '"Manrope", sans-serif',
    "fontSize": "0.95rem",
    "border": "none",
    "backgroundColor": "rgba(255, 255, 255, 0)",
}

TABLE_STYLE_HEADER = {
    "backgroundColor": "#78B63C",
    "color": "white",
    "fontWeight": "700",
    "border": "none",
    "padding": "14px 12px",
}

TABLE_STYLE_DATA = {
    "backgroundColor": "rgba(255, 255, 255, 0.88)",
    "border": "none",
}


def style_pie_chart(fig, title):
    fig.update_traces(
        textinfo="value+percent",
        marker={"colors": MERCANTOUR_COLORS, "line": {"color": "#ffffff", "width": 2}},
        hovertemplate="%{label}<br>%{value} taxons<extra></extra>",
    )
    fig.update_layout(
        title={"text": title, "x": 0.5, "xanchor": "center"},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": '"Manrope", sans-serif', "color": "#223127"},
        legend={"orientation": "h", "yanchor": "bottom", "y": -0.15, "x": 0.5, "xanchor": "center"},
        margin={"l": 20, "r": 20, "t": 70, "b": 70},
    )
    return fig
