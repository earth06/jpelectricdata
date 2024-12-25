import dash
import dash_bootstrap_components as dbc
from datareader import DataReader
from pages.common import Config


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


if __name__ == "__main__":
    app.run(debug=True)
    # app.run_server(mode="inline") #jupyter
