"""
Dash port of Shiny iris k-means example:

https://shiny.rstudio.com/gallery/kmeans-example.html
"""
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from sklearn import datasets
from sklearn.cluster import KMeans

from .dash import Dash

iris_raw = datasets.load_iris()
iris = pd.DataFrame(iris_raw["data"], columns=iris_raw["feature_names"])

controls = dbc.Card(
    [
        # dbc.FormGroup(
        #     [
        #         dbc.Label("X variable"),
        #         dcc.Dropdown(
        #             id="x-variable",
        #             options=[{"label": col, "value": col} for col in iris.columns],
        #             value="sepal length (cm)",
        #         ),
        #     ]
        # ),
        # dbc.FormGroup(
        #     [
        #         dbc.Label("Y variable"),
        #         dcc.Dropdown(
        #             id="y-variable",
        #             options=[{"label": col, "value": col} for col in iris.columns],
        #             value="sepal width (cm)",
        #         ),
        #     ]
        # ),
        # dbc.FormGroup(
        #     [
        #         dbc.Label("Cluster count"),
        #         dbc.Input(id="cluster-count", type="number", value=3),
        #     ]
        # ),
    ],
    body=True,
)

app_layout = dbc.Container(
    [
        html.H1("Iris k-means clustering"),
        html.Hr(),
        dbc.Row(
            [dbc.Col(controls, md=4), dbc.Col(dcc.Graph(id="cluster-graph"), md=8),],
            align="center",
        ),
    ],
    fluid=True,
)


# make sure that x and y values can't be the same variable
def filter_options(v):
    """Disable option v"""
    return [{"label": col, "value": col, "disabled": col == v} for col in iris.columns]


def make_graph(x, y, n_clusters):
    # minimal input validation, make sure there's at least one cluster
    km = KMeans(n_clusters=max(n_clusters, 1))
    df = iris.loc[:, [x, y]]
    km.fit(df.values)
    df["cluster"] = km.labels_

    centers = km.cluster_centers_

    data = [
        go.Scatter(
            x=df.loc[df.cluster == c, x],
            y=df.loc[df.cluster == c, y],
            mode="markers",
            marker={"size": 8},
            name="Cluster {}".format(c),
        )
        for c in range(n_clusters)
    ]

    data.append(
        go.Scatter(
            x=centers[:, 0],
            y=centers[:, 1],
            mode="markers",
            marker={"color": "#000", "size": 12, "symbol": "diamond"},
            name="Cluster centers",
        )
    )

    layout = {"xaxis": {"title": x}, "yaxis": {"title": y}}

    return go.Figure(data=data, layout=layout)


def init_callbacks(dash_app):
    dash_app.callback(
        Output("cluster-graph", "figure"),
        [
            Input("x-variable", "value"),
            Input("y-variable", "value"),
            Input("cluster-count", "value"),
        ],
    )(make_graph)
    # functionality is the same for both dropdowns, so we reuse filter_options
    dash_app.callback(Output("x-variable", "options"), [Input("y-variable", "value")],)(
        filter_options
    )
    dash_app.callback(Output("y-variable", "options"), [Input("x-variable", "value")],)(
        filter_options
    )

    return dash_app


def init_dash(server):
    """Create a Plotly Dash dashboard."""
    dash_app = Dash(server=server, routes_pathname_prefix="/iris-k-means/",)

    # create dash layout
    dash_app.layout = app_layout

    # initialize callbacks
    init_callbacks(dash_app)

    return dash_app.server


if __name__ == "__main__":
    # Only for debugging while developing
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    init_callbacks(app)
    app.run_server(debug=True, port=8080)
