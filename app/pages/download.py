from datetime import date

import dash
import plotly.express as px
from dash import Input, Output, State, callback, dcc, html
from datareader import DataReader
from pages.common import Config

reader = DataReader()
config = Config()

dash.register_page(__name__)

fix = px.line(x=[1, 2, 3], y=[1, 2, 3])

layout = html.Div(
    [
        html.H2("期間フィルターダッシュボード"),
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
                html.Button("表示", id="submit-button", n_clicks=0),
            ]
        ),
        html.Div(id="table-container"),
    ]
)


# コールバックの定義
@callback(
    Output("table-container", "children"),
    Input("submit-button", "n_clicks"),
    [
        State("start-date", "date"),
        State("end-date", "date"),
    ],
)
def update_table(n_clicks, start_date, end_date):
    if n_clicks > 0 and start_date and end_date:
        df = reader.read_spot_price(start_date, end_date)

        return dash.dash_table.DataTable(
            data=df.to_dict("records"),
            columns=[{"name": col, "id": col} for col in df.columns],
            export_format="csv",
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left"},
        )
    return html.Div("期間を選択し、表示ボタンを押してください。")
