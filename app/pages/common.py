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

        self.navigation = [
            {"label": "ホーム", "path": "/", "icon": "fa-house", "id": "nav-home"},
            {"label": "需給バランス", "path": "/balance", "icon": "fa-scale-balanced", "id": "nav-balance"},
            {"label": "ダウンロード", "path": "/download", "icon": "fa-download", "id": "nav-download"},
            {"label": "API URL発行", "path": "/publishapiurl", "icon": "fa-paper-plane", "id": "nav-publishapiurl"},
            {"label": "1か月トレンド", "path": "/trend", "icon": "fa-chart-line", "id": "nav-trend"},
        ]

    def format_legend(self, fig):
        fig.update_layout(
            legend={
                "orientation": "h",  # 凡例を横並び
                "entrywidth": 0.2,
                "yanchor": "bottom",
                "y": 1.02,
                "xanchor": "right",
                "x": 1,
                "entrywidthmode": "fraction",
                "bgcolor": "rgba(255, 255, 255, 0.9)",
                "bordercolor": "#e5e7eb",
                "borderwidth": 1,
            }
        )

    def apply_chart_theme(self, fig):
        fig.update_layout(
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font={"color": "#111827"},
            hovermode=False,
            hoverlabel={"bgcolor": "#ffffff", "bordercolor": "#facc15", "font_color": "#1f2937"},
            margin={"l": 50, "r": 30, "t": 50, "b": 40},
            autosize=True,
            width=None,
        )
        fig.update_traces(hoverinfo="skip", hovertemplate=None)
        fig.update_xaxes(
            showgrid=True,
            gridcolor="#e5e7eb",
            zeroline=False,
            linecolor="#d1d5db",
            tickfont={"color": "#4b5563"},
            titlefont={"color": "#4b5563"},
            automargin=True,
        )
        fig.update_yaxes(
            showgrid=True,
            gridcolor="#e5e7eb",
            zeroline=False,
            linecolor="#d1d5db",
            tickfont={"color": "#4b5563"},
            titlefont={"color": "#4b5563"},
            automargin=True,
        )
