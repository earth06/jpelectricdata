import pandas as pd
import dash
import dash_bootstrap_components as dbc
from datareader import DataReader
from pages.common import Config
from flask import request, jsonify


reader = DataReader()
config = Config()

# bootstrapを適用するにはstylesheetを指定する必要がある
external_stylesheets = [dbc.themes.FLATLY]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, use_pages=True)


app.layout = dbc.Container(
    [
        dbc.Row(
            [dbc.Col(config.sidebar, width=2), dbc.Col(dash.page_container, width=10)],
            style={"hegith": "100vh"},
        )
    ],
    fluid=True,
)


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
    app.run(debug=True)
    # app.run_server(mode="inline") #jupyter
