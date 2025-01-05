from datetime import date

import dash
from dash import dcc, html, callback
from dash import Input, Output, State
import plotly.express as px
import pandas as pd
from datareader import DataReader
from pages.common import Config

reader = DataReader()
config = Config()

dash.register_page(__name__)

fix = px.line(x=[1, 2, 3], y=[1, 2, 3])

layout = html.Div(
    [
        html.H2("API-URL発行"),
        html.Div(
            [
                html.Label("開始日:"),
                dcc.DatePickerSingle(
                    id="start-date",
                    date=date(2024, 12, 1),
                    display_format="YYYY-MM-DD",
                ),
                html.Label("終了日:"),
                dcc.DatePickerSingle(
                    id="end-date",
                    date=date(2024, 12, 7),
                    display_format="YYYY-MM-DD",
                ),
                html.Button("表示", id="api-publish-button", n_clicks=0),
            ]
        ),
        html.Div(id="api-url-container"),
    ]
)


# コールバックの定義
@callback(
    Output("api-url-container", "children"),
    Input("api-publish-button", "n_clicks"),
    [
        State("start-date", "date"),
        State("end-date", "date"),
    ],
)
def update_api_url(n_clicks, start_date, end_date):
    if n_clicks > 0 and start_date and end_date:
        start = pd.to_datetime(start_date).strftime("%Y%m%d")
        end = pd.to_datetime(end_date).strftime("%Y%m%d")
        url = f"http://<address>:<port>/api?begin={start}&end={end}"
        return html.Div(url)
    return html.Div("期間を選択し、表示ボタンを押してください。")
