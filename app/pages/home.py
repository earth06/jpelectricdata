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

dash.register_page(__name__, path="/")


def layout(**kwargs):
    # layout変数を定義しておくとマルチページ読み込みのときにapp.layoutに設定してくれるらしい
    fig = px.line(x=[1, 2, 3], y=[1, 2, 3])
    home_page = html.Div(
        children=[
            html.H2(children="市場価格と全エリアの需給"),
            # 期間の設定
            html.Div(
                children=[
                    "推論実行日:",
                    dcc.DatePickerSingle(
                        id="plot_base_date",
                        min_date_allowed=date(2024, 4, 1),
                        max_date_allowed=date.today() + timedelta(days=2),
                        date=date.today(),  # callbackで参照させるときはここの引数の名前になる
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
                    # "需給実績対象エリア:",
                    # dcc.Checklist(config.areas, ["chubu"], inline=True),
                    "需給項目:",
                    dcc.Dropdown(
                        options=config.demand_supply2_jpnames,
                        value="area_demand",
                        id="demand_supply_selector",
                    ),
                ]
            ),
            dcc.Graph(id="price-graph", figure=fig),
            dcc.Graph(id="demand-graph", figure=fig),
        ]
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
    fig = px.line(
        df, x="date_time", y=[f"area_price_{area}" for area in config.target_areas]
    )
    config.format_legend(fig)
    return fig
