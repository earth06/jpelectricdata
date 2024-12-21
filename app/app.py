from datetime import date
from datetime import datetime, timedelta
import dash
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
from datareader import DataReader


reader = DataReader()
target_areas = ["chubu", "kyusyu", "kansai", "tokyo"]
demand_supply_names = [
    "area_demand",
    "nuclear",
    "thermal_lng",
    "thermal_coal",
    "thermal_oil",
    "thermal_others",
    "hydropower",
    "geothermal",
    "biomass",
    "solarpower",
    "windpower",
    "pumping_up",
]
areas = [
    "hokkaido",
    "tohoku",
    "tokyo",
    "chubu",
    "hokuriku",
    "kansai",
    "chugoku",
    "shikoku",
    "kyusyu",
]


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.DataFrame(
    {
        "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
        "Amount": [4, 1, 2, 2, 4, 5],
        "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"],
    }
)

fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

app.layout = html.Div(
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
                    date=date.today(),  # callbackで参照させるときはここの引数の名前になる
                ),
            ]
        ),
        # 予測対象エリアの設定
        html.Div(
            children=[
                "予測対象エリア:",
                dcc.Checklist(target_areas, ["chubu"], inline=True),
            ]
        ),
        # 需給の対象エリア
        html.Div(
            children=[
                "需給実績対象エリア:",
                dcc.Checklist(areas, ["chubu"], inline=True),
                "需給項目:",
                dcc.Dropdown(
                    demand_supply_names, "area_demand", id="demand_supply_selector"
                ),
            ]
        ),
        dcc.Graph(id="demand-graph", figure=fig),
        dcc.Graph(id="price-graph", figure=fig),
    ]
)


# date singlepickerのdate属性をとる
@app.callback(
    Output("demand-graph", "figure"),
    Input("plot_base_date", "date"),
    Input("demand_supply_selector", "value"),
)
def update_price_graph(base_date, dem_sup_col):
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
    return fig


@app.callback(
    Output("price-graph", "figure"),
    Input("plot_base_date", "date"),
)
def update_demand_graph(base_date):
    print(base_date)
    py_base_date = datetime.strptime(base_date, "%Y-%m-%d")
    begin = (py_base_date - timedelta(days=7)).strftime("%Y-%m-%d")
    end = py_base_date.strftime("%Y-%m-%d")
    df = reader.read_spot_price(begin, end)
    fig = px.line(df, x="date_time", y=[f"area_price_{area}" for area in target_areas])
    return fig


if __name__ == "__main__":
    app.run(debug=True)
    # app.run_server(mode="inline") #jupyter
