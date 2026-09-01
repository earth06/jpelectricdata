TARGET_AREAS = ["chubu", "kyusyu", "kansai", "tokyo"]

SUPPLY_NAMES = [
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

SUPPLY_COLORS = [
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

DEMAND_SUPPLY_JP_NAMES = {
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

DEMAND_SUPPLY_NAMES = [*SUPPLY_NAMES, "area_demand"]

AREAS = [
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

AREA_JP_NAMES = {
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

TREND_AREA_JP_NAMES = {**AREA_JP_NAMES, "all": "全国"}

NAVIGATION = [
    {"label": "ホーム", "path": "/", "icon": "home"},
    {"label": "需給バランス", "path": "/balance", "icon": "balance"},
    {"label": "ダウンロード", "path": "/download", "icon": "download"},
    {"label": "API URL発行", "path": "/publishapiurl", "icon": "api"},
    {"label": "1か月トレンド", "path": "/trend", "icon": "trend"},
    {"label": "送電線マップ", "path": "/powermap", "icon": "map"},
]

SPOT_BLOCK_COLUMNS = [
    "sell_block_amount",
    "sell_block_contract_amount",
    "buy_block_amount",
    "buy_block_contract_amount",
]


def spot_price_columns(areas: list[str] | None = None) -> list[str]:
    """Return spot price column names for selected areas."""
    return [f"area_price_{area}" for area in (areas or TARGET_AREAS)]


def apply_chart_theme(fig) -> None:
    """Apply the dashboard's shared Plotly visual style."""
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
        automargin=True,
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#e5e7eb",
        zeroline=False,
        linecolor="#d1d5db",
        tickfont={"color": "#4b5563"},
        automargin=True,
    )


def format_legend(fig) -> None:
    """Place Plotly legends above the chart."""
    fig.update_layout(
        legend={
            "orientation": "h",
            "entrywidth": 0.2,
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
            "entrywidthmode": "fraction",
            "bgcolor": "rgba(255, 255, 255, 0.9)",
            "bordercolor": "#e5e7eb",
            "borderwidth": 1,
        },
    )
