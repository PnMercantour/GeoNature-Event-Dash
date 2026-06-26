from dash import html
import dash_bootstrap_components as dbc


def card(title, nb, id):
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.P(title, className="metric-label"),
                    html.H2(nb, className="metric-value", id=id),
                ],
                className="text-center metric-card-body",
            ),
        ],
        className="metric-card h-100",
    )
