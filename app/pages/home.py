from datetime import date, datetime, timedelta

import dash
import plotly.express as px
from dash import Input, Output, callback, dcc, html
from datareader import DataReader
from pages.common import Config

reader = DataReader()
config = Config()

dash.register_page(__name__, path="/")


CARD_CLASS = "rounded-2xl border border-gray-200 bg-white p-6 shadow-lg"
SECTION_TITLE_CLASS = "text-xs font-semibold uppercase tracking-[0.35em] text-yellow-600"
BLOCK_TITLE_CLASS = "text-xl font-semibold text-gray-900"
SUBTEXT_CLASS = "text-sm text-gray-700"
LABEL_CLASS = "block text-sm font-medium text-gray-700"

def layout(**kwargs):
    # layout変数を定義しておくとマルチページ読み込みのときにapp.layoutに設定してくれるらしい
    fig = px.line(x=[1, 2, 3], y=[1, 2, 3])
    home_page = html.Div(
        className="space-y-8",
        children=[
            html.Div(
                className="space-y-2",
                children=[
                    html.Span("ホーム", className=SECTION_TITLE_CLASS),
                    html.H2("市場価格と全エリアの需給", className=BLOCK_TITLE_CLASS),
                    html.P(
                        "直近の推論実行日を基点に、スポット市場価格と需給実績を横断的に確認できます。",
                        className=SUBTEXT_CLASS,
                    ),
                ],
            ),
            html.Div(
                className="grid gap-6 xl:grid-cols-[1.2fr,2fr]",
                children=[
                    html.Div(
                        className=f"{CARD_CLASS} space-y-6",
                        children=[
                            html.Div(
                                className="space-y-1",
                                children=[
                                    html.H3("ビュー設定", className="text-lg font-semibold text-gray-900"),
                                    html.P(
                                        "対象期間とエリアを切り替えて表示をカスタマイズします。",
                                        className=SUBTEXT_CLASS,
                                    ),
                                ],
                            ),
                            html.Div(
                                className="space-y-4",
                                children=[
                                    html.Div(
                                        className="space-y-2",
                                        children=[
                                            html.Label("推論実行日", className=LABEL_CLASS),
                                            dcc.DatePickerSingle(
                                                id="plot_base_date",
                                                min_date_allowed=date(2024, 4, 1),
                                                max_date_allowed=date.today() + timedelta(days=2),
                                                date=date.today(),
                                                display_format="YYYY-MM-DD",
                                                className="tailwind-date-picker",
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        className="space-y-2",
                                        children=[
                                            html.Label("予測対象エリア", className=LABEL_CLASS),
                                            dcc.Checklist(
                                                config.target_areas,
                                                ["chubu"],
                                                inline=True,
                                                className="flex flex-wrap gap-2 text-sm text-gray-800",
                                                inputStyle={"marginRight": "0.50rem"},
                                                labelStyle={
                                                    "background": "#f3f4f6",
                                                    "color": "#1f2937",
                                                    "padding": "0.375rem 0.75rem",
                                                    "borderRadius": "9999px",
                                                    "border": "1px solid #e5e7eb",
                                                    "display": "flex",
                                                    "alignItems": "center",
                                                    "gap": "0.4rem",
                                                },
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        className="space-y-2",
                                        children=[
                                            html.Label("需給項目", className=LABEL_CLASS),
                                            dcc.Dropdown(
                                                options=config.demand_supply2_jpnames,
                                                value="area_demand",
                                                id="demand_supply_selector",
                                                className="tailwind-dropdown text-sm",
                                                clearable=False,
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        className="space-y-6",
                        children=[
                            html.Div(
                                className=f"{CARD_CLASS} card-plotly space-y-4",
                                children=[
                                    html.Div(
                                        className="flex items-center justify-between",
                                        children=[
                                            html.H3("スポット市場価格", className="text-lg font-semibold text-gray-900"),
                                            html.Span("単位: 円/kWh", className="text-xs text-gray-700"),
                                        ],
                                    ),
                                    dcc.Graph(
                                        id="price-graph",
                                        figure=fig,
                                        config={"displaylogo": False, "responsive": True},
                                        responsive=True,
                                        style={"width": "100%", "height": "420px"},
                                        className="rounded-xl border border-gray-100 bg-gray-50 p-2",
                                    ),
                                ],
                            ),
                            html.Div(
                                className=f"{CARD_CLASS} card-plotly space-y-4",
                                children=[
                                    html.Div(
                                        className="flex items-center justify-between",
                                        children=[
                                            html.H3("需給実績", className="text-lg font-semibold text-gray-900"),
                                            html.Span("エリア別の時系列", className="text-xs text-gray-700"),
                                        ],
                                    ),
                                    dcc.Graph(
                                        id="demand-graph",
                                        figure=fig,
                                        config={"displaylogo": False, "responsive": True},
                                        responsive=True,
                                        style={"width": "100%", "height": "420px"},
                                        className="rounded-xl border border-gray-100 bg-gray-50 p-2",
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
    return home_page


# date singlepickerのdate属性をとる
@callback(
    Output("demand-graph", "figure"),
    Input("plot_base_date", "date"),
    Input("demand_supply_selector", "value"),
)
def update_demand_graph(base_date, dem_sup_col):
    print(base_date)
    py_base_date = datetime.strptime(base_date, "%Y-%m-%d")
    begin = (py_base_date - timedelta(days=7)).strftime("%Y-%m-%d")
    end = py_base_date.strftime("%Y-%m-%d")
    df = reader.read_demand_supply(begin, end)
    fig = px.line(
        df,
        x="date_time",
        y=dem_sup_col,
        color="area_name",
    )
    config.format_legend(fig)
    col = config.demand_supply2_jpnames[dem_sup_col]
    config.apply_chart_theme(fig)
    fig.update_layout(title=f"{col}")

    return fig


@callback(
    Output("price-graph", "figure"),
    Input("plot_base_date", "date"),
)
def update_price_graph(base_date):
    print(base_date)
    py_base_date = datetime.strptime(base_date, "%Y-%m-%d")
    begin = (py_base_date - timedelta(days=7)).strftime("%Y-%m-%d")
    end = py_base_date.strftime("%Y-%m-%d")
    df = reader.read_spot_price(begin, end)
    fig = px.line(df, x="date_time", y=[f"area_price_{area}" for area in config.target_areas])
    config.format_legend(fig)
    config.apply_chart_theme(fig)
    fig.update_layout(title="スポット市場価格")
    return fig
