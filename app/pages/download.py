from datetime import date

import dash
from dash import Input, Output, State, callback, dash_table, dcc, html
from datareader import DataReader
from pages.common import Config

reader = DataReader()
config = Config()

dash.register_page(__name__)

CARD_CLASS = "rounded-2xl border border-gray-200 bg-white p-6 shadow-lg"
SECTION_TITLE_CLASS = "text-xs font-semibold uppercase tracking-[0.35em] text-yellow-600"
BLOCK_TITLE_CLASS = "text-xl font-semibold text-gray-900"
SUBTEXT_CLASS = "text-sm text-gray-700"
LABEL_CLASS = "block text-sm font-medium text-gray-700"


def layout(**kwargs):
    return html.Div(
        className="space-y-8",
        children=[
            html.Div(
                className="space-y-2",
                children=[
                    html.Span("データダウンロード", className=SECTION_TITLE_CLASS),
                    html.H2("任意期間のスポット価格をダウンロード", className=BLOCK_TITLE_CLASS),
                    html.P(
                        "期間を指定してスポット価格データを抽出し、CSVで出力できます。",
                        className=SUBTEXT_CLASS,
                    ),
                ],
            ),
            html.Div(
                className="grid gap-6 lg:grid-cols-[1.2fr,2fr]",
                children=[
                    html.Div(
                        className=f"{CARD_CLASS} space-y-6",
                        children=[
                            html.Div(
                                className="space-y-1",
                                children=[
                                    html.H3("抽出条件", className="text-lg font-semibold text-gray-900"),
                                    html.P(
                                        "開始日と終了日を入力し、表示ボタンからデータを読み込みます。",
                                        className=SUBTEXT_CLASS,
                                    ),
                                ],
                            ),
                            html.Div(
                                className="space-y-4",
                                children=[
                                    html.Div(
                                        className="grid gap-4 sm:grid-cols-2",
                                        children=[
                                            html.Div(
                                                className="space-y-2",
                                                children=[
                                                    html.Label("開始日", className=LABEL_CLASS),
                                                    dcc.DatePickerSingle(
                                                        id="start-date",
                                                        date=date(2024, 12, 1),
                                                        display_format="YYYY-MM-DD",
                                                        className="tailwind-date-picker",
                                                    ),
                                                ],
                                            ),
                                            html.Div(
                                                className="space-y-2",
                                                children=[
                                                    html.Label("終了日", className=LABEL_CLASS),
                                                    dcc.DatePickerSingle(
                                                        id="end-date",
                                                        date=date(2024, 12, 7),
                                                        display_format="YYYY-MM-DD",
                                                        className="tailwind-date-picker",
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        className="flex justify-end",
                                        children=[
                                            html.Button(
                                                "表示",
                                                id="submit-button",
                                                n_clicks=0,
                                                className=(
                                                    "inline-flex items-center gap-2 rounded-lg border border-yellow-500/50 "
                                                    "bg-yellow-400/90 px-4 py-2 text-sm font-semibold text-gray-900 "
                                                    "transition hover:bg-yellow-400 focus:outline-none focus:ring-2 "
                                                    "focus:ring-yellow-400 focus:ring-offset-2 focus:ring-offset-white"
                                                ),
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        className=f"{CARD_CLASS} space-y-4",
                        children=[
                            html.Div(
                                className="flex items-center justify-between",
                                children=[
                                    html.H3("取得データプレビュー", className="text-lg font-semibold text-gray-900"),
                                    html.Span("CSVエクスポート対応", className="text-xs text-gray-700"),
                                ],
                            ),
                            html.Div(
                                id="table-container",
                                className="rounded-xl border border-dashed border-gray-200 bg-gray-50 p-4 text-sm text-gray-700",
                                children="期間を選択し、表示ボタンを押してください。",
                            ),
                        ],
                    ),
                ],
            ),
        ],
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

        return dash_table.DataTable(
            data=df.to_dict("records"),
            columns=[{"name": col, "id": col} for col in df.columns],
            export_format="csv",
            export_headers="display",
            fill_width=True,
            style_header={
                "backgroundColor": "#f9fafb",
                "border": "1px solid #e5e7eb",
                "color": "#111827",
                "fontWeight": "600",
                "textAlign": "left",
            },
            style_cell={
                "backgroundColor": "#ffffff",
                "border": "1px solid #e5e7eb",
                "color": "#1f2937",
                "padding": "0.5rem",
                "textAlign": "left",
                "fontSize": "0.9rem",
            },
            style_data_conditional=[
                {
                    "if": {"state": "selected"},
                    "backgroundColor": "#fde68a",
                    "color": "#78350f",
                }
            ],
            style_table={"overflowX": "auto", "maxHeight": "26rem", "border": "1px solid #e5e7eb"},
        )
    return html.Div(
        "期間を選択し、表示ボタンを押してください。",
        className="text-sm text-gray-700",
    )
