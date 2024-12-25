from datetime import date
from datetime import datetime, timedelta
import dash
from dash import dcc, html, callback
from dash import Input, Output
import plotly.express as px

from datareader import DataReader
from pages.common import Config

reader = DataReader()
config = Config()

dash.register_page(__name__)

# layout変数を定義しておくとマルチページ読み込みのときにapp.layoutに設定してくれるらしい

fig = px.line(x=[1, 2, 3], y=[1, 2, 3])
layout = html.Div(
    children=[
        html.H1(children="Hello Dash"),
        # 期間の設定
        html.Div(
            children=[
                "推論実行日:",
                dcc.DatePickerSingle(
                    id="plot_base_date",
                    min_date_allowed=date(2024, 4, 1),
                    max_date_allowed=date.today() + timedelta(days=2),
                    date=date.today()
                    - timedelta(10),  # callbackで参照させるときはここの引数の名前になる
                ),
            ]
        ),
        # 予測対象エリアの設定
        html.Div(
            children=[
                "予測対象エリア:",
                dcc.Checklist(config.target_areas, ["chubu"], inline=True),
            ]
        ),
        # 需給の対象エリア
        html.Div(
            children=[
                "需給バランス対象エリア:",
                dcc.Dropdown(
                    config.areas,
                    "chubu",
                    id="area_selector",
                ),
            ]
        ),
        dcc.Graph(id="price-graph2", figure=fig),  # defaultをNoneは許容されない
        dcc.Graph(id="balance-graph", figure=fig),
    ]
)


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
    fig = px.line(
        df, x="date_time", y=[f"area_price_{area}" for area in config.target_areas]
    )
    config.format_legend(fig)
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
    df = reader.read_demand_supply(begin, end).query(f"area_name=='{area}'")
    fig = px.area(
        df,
        x="date_time",
        y=config.demand_supply_names,
    )
    config.format_legend(fig)

    return fig
