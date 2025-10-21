import copy
from datetime import date, datetime, timedelta

import dash
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html
from datareader import DataReader
from pages.common import Config

reader = DataReader()
config = Config()

custom_area_options = config.area2jparea.copy()
custom_area_options["all"] = "全国"

dash.register_page(__name__)

# layout変数を定義しておくとマルチページ読み込みのときにapp.layoutに設定してくれるらしい

CARD_CLASS = "rounded-2xl border border-gray-200 bg-white p-6 shadow-lg"
SECTION_TITLE_CLASS = "text-xs font-semibold uppercase tracking-[0.35em] text-yellow-600"
BLOCK_TITLE_CLASS = "text-xl font-semibold text-gray-900"
SUBTEXT_CLASS = "text-sm text-gray-700"
LABEL_CLASS = "block text-sm font-medium text-gray-700"

def layout(**kwargs):
    fig = px.line(x=[1, 2, 3], y=[1, 2, 3])
    trend_page = html.Div(
        className="space-y-8",
        children=[
            html.Div(
                className="space-y-2",
                children=[
                    html.Span("1か月トレンド", className=SECTION_TITLE_CLASS),
                    html.H2("需給と市場価格のトレンド把握", className=BLOCK_TITLE_CLASS),
                    html.P(
                        "直近1か月の推移を俯瞰し、スポット指標と需給バランスの相関を確認します。",
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
                                        "分析対象の期間と指標を切り替えます。",
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
                                            html.Label("基準日", className=LABEL_CLASS),
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
                                            html.Label("スポット取引結果項目", className=LABEL_CLASS),
                                            dcc.Dropdown(
                                                [
                                                    {"label": "価格", "value": "price"},
                                                    {"label": "ブロック取引量", "value": "block"},
                                                ],
                                                "price",
                                                id="spot_selector",
                                                className="tailwind-dropdown text-sm",
                                                clearable=False,
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        className="space-y-2",
                                        children=[
                                            html.Label("需給バランス対象エリア", className=LABEL_CLASS),
                                            dcc.Dropdown(
                                                [
                                                    {"label": label, "value": value}
                                                    for value, label in custom_area_options.items()
                                                ],
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
                                            html.H3("スポット市場", className="text-lg font-semibold text-gray-900"),
                                            html.Span("30日間の推移", className="text-xs text-gray-700"),
                                        ],
                                    ),
                                    dcc.Graph(
                                        id="trend-price-graph",
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
                                            html.H3("需給バランス", className="text-lg font-semibold text-gray-900"),
                                            html.Span("積み上げ表示", className="text-xs text-gray-700"),
                                        ],
                                    ),
                                    dcc.Graph(
                                        id="trend-graph",
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
    return trend_page


@callback(Output("trend-price-graph", "figure"), Input("plot_base_date", "date"), Input("spot_selector", "value"))
def update_price_graph(base_date, spot_col):
    print(base_date)
    py_base_date = datetime.strptime(base_date, "%Y-%m-%d")
    begin = (py_base_date - timedelta(days=30)).strftime("%Y-%m-%d")
    end = py_base_date.strftime("%Y-%m-%d")
    df = reader.read_spot_price(begin, end)

    if spot_col == "price":
        cols = [f"area_price_{area}" for area in config.target_areas]
    elif spot_col == "block":
        cols = [f"sell_block_amount", "sell_block_contract_amount", "buy_block_amount", "buy_block_contract_amount"]
    fig = px.line(
        df,
        x="date_time",
        y=cols,
        color_discrete_sequence=["red", "pink", "blue", "aqua"],
    )
    config.format_legend(fig)
    fig.update_layout(
        height=500,
        title="スポット市場価格",
        yaxis={"fixedrange": False},
        xaxis={"rangeslider": {"visible": True, "thickness": 0.1}, "type": "date"},
    )
    config.apply_chart_theme(fig)
    return fig


# # date singlepickerのdate属性をとる
@callback(
    Output("trend-graph", "figure"),
    Input("plot_base_date", "date"),
    Input("area_selector", "value"),
)
def update_trend_graph(base_date, area):
    print(base_date)
    py_base_date = datetime.strptime(base_date, "%Y-%m-%d")
    begin = (py_base_date - timedelta(days=30)).strftime("%Y-%m-%d")
    end = py_base_date.strftime("%Y-%m-%d")
    if area != "all":
        df = reader.read_demand_supply(begin, end, ignore_negative_value=True).query(f"area_name=='{area}'")
    else:
        df = reader.read_demand_supply(begin, end, ignore_negative_value=True)
        df = df.groupby("date_time").sum().reset_index()
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
    jparea = custom_area_options[area]
    fig.update_layout(
        height=500,
        title=f"{jparea}:需給",
        yaxis={"fixedrange": False},
        xaxis={"rangeslider": {"visible": True, "thickness": 0.1}, "type": "date"},
        legend={
            "orientation": "h",
            "entrywidth": 0.2,
            "yanchor": "top",
            "xanchor": "right",
            "y": -0.35,
            "x": 1,
            "entrywidthmode": "fraction",
            "bgcolor": "rgba(17, 24, 39, 0.75)",
            "bordercolor": "#1f2937",
            "borderwidth": 1,
        },
    )
    config.apply_chart_theme(fig)

    return fig
