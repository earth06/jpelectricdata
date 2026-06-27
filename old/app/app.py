import argparse

import dash
import pandas as pd
from dash import Input, Output, State, dcc, html
from datareader import DataReader
from flask import jsonify, request
from pages.common import Config

reader = DataReader()
config = Config()

external_stylesheets = [
    "https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css",
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, use_pages=True)
app.title = "JP Electric Dashboard"
server = app.server

SIDEBAR_BASE_CLASS = "sidebar flex min-h-screen flex-col bg-gray-100 text-gray-900 shadow-xl transition-all duration-300"


def build_sidebar_links():
    base_class = (
        "sidebar-link group flex items-center gap-3 rounded-md px-4 py-3 text-sm font-medium "
        "tracking-wide text-gray-700 transition-colors duration-150 hover:bg-yellow-100 hover:text-gray-900"
    )
    links = []
    for item in config.navigation:
        link_children = [
            html.I(className=f"sidebar-icon fa-solid {item['icon']}", **{"aria-hidden": "true"}),
            html.Span(item["label"], className="sidebar-label"),
        ]
        links.append(
            dcc.Link(
                link_children,
                href=item["path"],
                id=item["id"],
                className=base_class,
            )
        )
    return links


app.layout = html.Div(
    className="min-h-screen bg-gray-50 text-black",
    children=[
        dcc.Location(id="url"),
        dcc.Store(id="sidebar-collapsed", data=False),
        html.Div(
            className="flex min-h-screen",
            children=[
                html.Nav(
                    id="sidebar",
                    className=SIDEBAR_BASE_CLASS,
                    **{"data-collapsed": "false"},
                    children=[
                        html.Div(
                            className="flex flex-col gap-1 border-b border-gray-200 px-5 py-5",
                            children=[
                                html.Span(
                                    "JP Electric Data",
                                    className="text-sm font-semibold uppercase tracking-[0.2em] text-yellow-500",
                                ),
                                html.Span(
                                    "電力需給ダッシュボード",
                                    className="sidebar-label text-base font-semibold text-gray-900",
                                ),
                            ],
                        ),
                        html.Div(build_sidebar_links(), className="flex flex-col gap-1 px-3 py-4"),
                    ],
                ),
                html.Div(
                    id="content-wrapper",
                    className="flex flex-1 flex-col",
                    children=[
                        html.Header(
                            className=(
                                "flex items-center justify-between border-b border-gray-200 bg-white/90 px-6 py-4 "
                                "backdrop-blur"
                            ),
                            children=[
                                html.Button(
                                    html.I(id="sidebar-toggle-icon", className="fa-solid fa-chevron-left"),
                                    id="sidebar-toggle",
                                    className=(
                                        "inline-flex h-10 w-10 items-center justify-center rounded-md border border-gray-200 "
                                        "bg-white text-gray-700 transition hover:bg-yellow-100 focus:outline-none "
                                        "focus:ring-2 focus:ring-yellow-400 focus:ring-offset-2 focus:ring-offset-white"
                                    ),
                                ),
                                html.Div(
                                    className="flex flex-col gap-1",
                                    children=[
                                        html.H1(
                                            "電力需給・電力市場ダッシュボード",
                                            className="text-lg font-semibold text-gray-900",
                                        ),
                                        html.Span(
                                            "電力需給と市場価格データの可視化",
                                            className="text-sm text-gray-700",
                                        ),
                                    ],
                                ),
                                html.Div(
                                    className="hidden items-center gap-2 text-sm text-gray-700 md:flex",
                                    children=[
                                        html.I(className="fa-solid fa-bolt text-yellow-500"),
                                        html.Span("最新データを確認"),
                                    ],
                                ),
                            ],
                        ),
                        html.Main(
                            className="flex-1 overflow-y-auto bg-gray-50 px-6 py-8",
                            children=[
                                html.Div(
                                    className=(
                                        "mx-auto flex w-full max-w-6xl flex-col gap-8"
                                    ),
                                    children=[dash.page_container],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)


@app.callback(
    Output("sidebar", "className"),
    Output("sidebar", "data-collapsed"),
    Output("sidebar-collapsed", "data"),
    Output("sidebar-toggle-icon", "className"),
    Input("sidebar-toggle", "n_clicks"),
    State("sidebar-collapsed", "data"),
    prevent_initial_call=True,
)
def toggle_sidebar(n_clicks, is_collapsed):
    collapsed = not is_collapsed
    icon_class = "fa-solid fa-chevron-right" if collapsed else "fa-solid fa-chevron-left"
    sidebar_class = SIDEBAR_BASE_CLASS + (" collapsed" if collapsed else "")
    return sidebar_class, str(collapsed).lower(), collapsed, icon_class


@app.callback(
    [Output(item["id"], "className") for item in config.navigation],
    Input("url", "pathname"),
)
def highlight_active_link(pathname):
    base_class = (
        "sidebar-link group flex items-center gap-3 rounded-md px-4 py-3 text-sm font-medium "
        "tracking-wide text-gray-700 transition-colors duration-150 hover:bg-yellow-100 hover:text-gray-900"
    )
    classes = []
    normalized_path = pathname or "/"
    for item in config.navigation:
        is_active = normalized_path == item["path"]
        class_name = base_class + (" active" if is_active else "")
        classes.append(class_name)
    return classes


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
