from datetime import date

import dash
import pandas as pd
from dash import Input, Output, State, callback, dcc, html
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
                    html.Span("API発行", className=SECTION_TITLE_CLASS),
                    html.H2("指定期間のAPI URLを生成", className=BLOCK_TITLE_CLASS),
                    html.P(
                        "APIに渡す期間パラメータをGUIから生成し、即座に共有できます。",
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
                                    html.H3("パラメータ設定", className="text-lg font-semibold text-gray-900"),
                                    html.P(
                                        "開始日と終了日を指定し、API URL を生成します。",
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
                                                "URL生成",
                                                id="api-publish-button",
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
                                    html.H3("生成されたURL", className="text-lg font-semibold text-gray-900"),
                                    html.Span("コピーして共有", className="text-xs text-gray-700"),
                                ],
                            ),
                            html.Div(
                                id="api-url-container",
                                className="rounded-xl border border-dashed border-gray-200 bg-gray-50 p-4",
                                children=html.Div(
                                    "期間を選択し、URL生成ボタンを押してください。",
                                    className="text-sm text-gray-700",
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        ],
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
        return html.Div(
            className="flex flex-wrap items-start justify-between gap-3",
            children=[
                html.Div(
                    className="space-y-2",
                    children=[
                        html.Span("API Endpoint", className="text-xs font-semibold uppercase tracking-wide text-gray-700"),
                        html.Div(
                            url,
                            id="generated-api-url",
                            className="max-w-full truncate rounded-lg border border-yellow-400/60 bg-yellow-50 px-3 py-2 font-mono text-sm text-yellow-700",
                        ),
                    ],
                ),
                dcc.Clipboard(
                    target_id="generated-api-url",
                    title="コピー",
                    className=(
                        "inline-flex h-9 items-center justify-center rounded-md border border-gray-200 "
                        "bg-white px-3 text-xs font-semibold text-gray-700 transition hover:bg-yellow-100"
                    ),
                ),
            ],
        )
    return html.Div(
        "期間を選択し、URL生成ボタンを押してください。",
        className="text-sm text-gray-700",
    )
