import dash_bootstrap_components as dbc
from dash import dcc, html


class Config:
    def __init__(self):
        self.target_areas = ["chubu", "kyusyu", "kansai", "tokyo"]
        self.supply_names = [
            "nuclear",
            "geothermal",
            "hydropower",
            "thermal_lng",
            "thermal_coal",
            "thermal_oil",
            "thermal_others",
            "biomass",
            "windpower",
            "solarpower",
            "pumping_up",
            "battery",
            "connector",
            "others",
        ]

        self.supply_colors = [
            "#7030a0",
            "#a00000",
            "#0170c0",
            "#ff7f81",
            "#dbdbdb",
            "#fff2cd",
            "#698fd0",
            "#92d051",
            "#00af50",
            "#ffff01",
            "#01b0f1",
            "#f29659",
            "#7f7f7f",
            "#c86480",
        ]

        self.demand_supply2_jpnames = {
            "area_demand": "需要",
            "nuclear": "原子力",
            "thermal_lng": "LNG",
            "thermal_coal": "石炭",
            "thermal_oil": "石油",
            "thermal_others": "その他",
            "hydropower": "水力",
            "geothermal": "地熱",
            "biomass": "バイオマス",
            "solarpower": "太陽光",
            "windpower": "風力",
            "pumping_up": "揚水",
            "others": "その他",
            "battery": "蓄電池",
            "connector": "連系線",
        }
        self.jp2en_demand_supply = {val: key for key, val in self.demand_supply2_jpnames.items()}

        self.demand_supply_names = self.supply_names + ["area_demand"]
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
        # dashでは value:labelの扱い
        self.area2jparea = {
            "hokkaido": "北海道",
            "tohoku": "東北",
            "tokyo": "東京",
            "chubu": "中部",
            "hokuriku": "北陸",
            "kansai": "関西",
            "chugoku": "中国",
            "shikoku": "四国",
            "kyusyu": "九州",
        }

        self.page_paths = ["/", "/balance", "/download", "/publishapiurl"]
        self.page_names = ["ホーム", "需給バランス", "ダウンロード", "apiurl発行"]
        self.sidebar = html.Div(
            [html.H2(children="Index")]
            + [html.Div(dcc.Link(page, href=page_path)) for page, page_path in zip(self.page_names, self.page_paths)]
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
            legend={
                "orientation": "h",  # 凡例を横に並べる
                "entrywidth": 0.2,  # 凡例の幅(いまいちよくわからん)
                "yanchor": "bottom",
                "y": 1.02,
                "xanchor": "right",
                "x": 1,
                "entrywidthmode": "fraction",  # 0-1で凡例の幅を決める
            }
        )
