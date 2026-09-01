from datetime import date, datetime, timedelta

import dash
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html
from datareader import DataReader
from pages.common import Config

reader = DataReader()
config = Config()

dash.register_page(__name__)

# layout変数を定義しておくとマルチページ読み込みのときにapp.layoutに設定してくれるらしい

CARD_CLASS = "rounded-2xl border border-gray-200 bg-white p-6 shadow-lg"
SECTION_TITLE_CLASS = "text-xs font-semibold uppercase tracking-[0.35em] text-yellow-600"
BLOCK_TITLE_CLASS = "text-xl font-semibold text-gray-900"
SUBTEXT_CLASS = "text-sm text-gray-700"
LABEL_CLASS = "block text-sm font-medium text-gray-700"

def layout(**kwargs):
    fig = px.line(x=[1, 2, 3], y=[1, 2, 3])
    balance_page = html.Div(
        className="space-y-8",
        children=[
            html.Div(
                className="space-y-2",
                children=[
                    html.Span("需給バランス", className=SECTION_TITLE_CLASS),
                    html.H2("各エリアの需給構造と市場価格", className=BLOCK_TITLE_CLASS),
                    html.P(
                        "スポット市場価格とエリア別需給構成を並べて比較し、変化の兆しを素早く捉えます。",
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
                                        "比較したい期間とエリアを選択します。",
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
                                                date=date.today() - timedelta(2),
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
                                            html.Label("需給バランス対象エリア", className=LABEL_CLASS),
                                            dcc.Dropdown(
                                                config.area2jparea,
                                                "chubu",
                                                id="area_selector",
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
                                        id="price-graph2",
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
                                            html.H3("需給実績の積み上げ", className="text-lg font-semibold text-gray-900"),
                                            html.Span("単位: 万kWh", className="text-xs text-gray-700"),
                                        ],
                                    ),
                                    dcc.Graph(
                                        id="balance-graph",
                                        figure=fig,
                                        config={"displaylogo": False, "responsive": True},
                                        responsive=True,
                                        style={"width": "100%", "height": "460px"},
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
    return balance_page


@callback(
    Output("price-graph2", "figure"),
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


# # date singlepickerのdate属性をとる
@callback(
    Output("balance-graph", "figure"),
    Input("plot_base_date", "date"),
    Input("area_selector", "value"),
)
def update_balance_graph(base_date, area):
    print(base_date)
    py_base_date = datetime.strptime(base_date, "%Y-%m-%d")
    begin = (py_base_date - timedelta(days=7)).strftime("%Y-%m-%d")
    end = py_base_date.strftime("%Y-%m-%d")
    df = reader.read_demand_supply(begin, end, ignore_negative_value=True).query(f"area_name=='{area}'")
    fig = px.area(
        df,
        x="date_time",
        y=config.supply_names,
        color_discrete_sequence=config.supply_colors,
    )
    for trace in fig.data:
        if getattr(trace, "fill", None) in ("tonexty", "tozeroy"):
            trace.update(line={"width": 0.4}, opacity=0.85)
    fig.add_trace(
        go.Scatter(
            x=df["date_time"],
            y=df["area_demand"],
            name="エリア需要",
            line={"color": "#1e3a8a", "width": 3},
        )
    )
    config.format_legend(fig)
    jparea = config.area2jparea[area]
    config.apply_chart_theme(fig)
    fig.update_layout(title=f"{jparea}:需給")

    return fig
