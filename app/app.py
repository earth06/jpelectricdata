import argparse
import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from datareader import DataReader
from pages.common import Config
from flask import request, jsonify


reader = DataReader()
config = Config()

# bootstrapを適用するにはstylesheetを指定する必要がある
external_stylesheets = [dbc.themes.FLATLY]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, use_pages=True)


app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H1("電力需給・電力市場DashBoard"),
                width=12,
                style={"background-color": "palegreen", "color": "white"},
            )
        ),
        dbc.Row(
            [dbc.Col(config.sidebar, width=2), dbc.Col(dash.page_container, width=10)],
            style={"height": "90vh"},
        ),
    ],
    fluid=True,
)


@app.server.route("/api")
def download_data():
    begin = request.args.get("begin", "20241201")
    end = request.args.get("end", "20241201")
    s_begin = pd.to_datetime(begin, format="%Y%m%d").strftime("%Y-%m-%d 00:00")
    s_end = pd.to_datetime(end, format="%Y%m%d").strftime("%Y-%m-%d 23:59")
    print(s_begin, s_end)
    df = reader.read_spot_price(s_begin, s_end)
    return jsonify(df[["date_time", "area_price_chubu"]].to_dict())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8050)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=args.debug)

    # app.run_server(mode="inline") #jupyter
