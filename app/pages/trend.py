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


def layout(**kwargs):
    fig = px.line(x=[1, 2, 3], y=[1, 2, 3])
    balance_page = html.Div(
        children=[
            html.H2(children="需給バランス"),
            # 期間の設定
            html.Div(
                children=[
                    "推論実行日:",
                    dcc.DatePickerSingle(
                        id="plot_base_date",
                        min_date_allowed=date(2024, 4, 1),
                        max_date_allowed=date.today() + timedelta(days=2),
                        date=date.today() - timedelta(2),  # callbackで参照させるときはここの引数の名前になる
                    ),
                ]
            ),
            # 需給の対象エリア
            html.Div(
                children=[
                    "スポット取引結果項目:",
                    dcc.Dropdown(
                        ["block", "price"],
                        "price",
                        id="spot_selector",
                    ),
                ]
            ),
            html.Div(
                children=[
                    "需給バランス対象エリア:",
                    dcc.Dropdown(
                        custom_area_options,
                        "chubu",
                        id="area_selector",
                    ),
                ]
            ),
            dcc.Graph(id="trend-price-graph", figure=fig),  # defaultをNoneは許容されない
            dcc.Graph(id="trend-graph", figure=fig),
        ]
    )
    return balance_page


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
    fig.add_trace(
        go.Scatter(
            x=df["date_time"],
            y=df["area_demand"],
            name="エリア需要",
            marker={"color": "black"},
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
        },
    )

    return fig
