from dash import html, dcc
import dash_bootstrap_components as dbc


class Config:
    def __init__(self):

        self.target_areas = ["chubu", "kyusyu", "kansai", "tokyo"]
        self.demand_supply_names = [
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
        self.areas = [
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

        self.page_paths = ["/", "/balance", "/download"]
        self.page_names = ["ホーム", "需給バランス", "ダウンロード"]
        self.sidebar = html.Div(
            [
                html.Div(dcc.Link(page, href=page_path))
                for page, page_path in zip(self.page_names, self.page_paths)
            ]
        )

    def generate_side_main_layout(self, layout):
        container = dbc.Container(
            [
                dbc.Row(
                    [dbc.Col(self.sidebar, width=2), dbc.Col(layout, width=10)],
                    style={"hegith": "100vh"},
                )
            ],
            fluid=True,
        )
        return container

    def format_legend(self, fig):
        fig.update_layout(
            legend=dict(
                orientation="h",  # 凡例を横に並べる
                entrywidth=0.2,  # 凡例の幅(いまいちよくわからん)
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                entrywidthmode="fraction",  # 0-1で凡例の幅を決める
            )
        )
