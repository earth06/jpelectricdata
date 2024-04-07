import matplotlib.pyplot as plt
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os

plt.style.use("ggplot")

ROOTDIR = f"{os.path.dirname(__file__)}/.."


class ElectricAnalysis:
    def __init__(self):
        self.labels = [
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
        self.colors = [
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

    def load_demand_supply(
        self, begin: str = None, end: str = None, ignore_pump_up=True
    ):
        if begin is None:
            begin = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
        if end is None:
            end = datetime.today().strftime("%Y-%m-%d 23:59:59")
        conn = sqlite3.connect(f"{ROOTDIR}/data/data.db")
        sql = f"""
            SELECT * FROM detail_demand_supply 
            WHERE date_time BETWEEN '{begin}' AND '{end}'
        """
        self.df_demand = pd.read_sql(sql, conn, parse_dates=["date_time"])
        if ignore_pump_up:
            self.df_demand["pumping_up"] = self.df_demand["pumping_up"].where(
                self.df_demand["pumping_up"] >= 0, 0
            )
        conn.close()
        return

    def plot_demand_supply(self, area_name="chubu", figsize=(16, 5)):
        fig, ax = plt.subplots(figsize=figsize)
        tmp = self.df_demand.query(f"area_name=='{area_name}'").copy()
        tmp.index = pd.to_datetime(tmp["date_time"])
        tmp[self.labels].plot(kind="area", color=self.colors, ax=ax)
        tmp["area_demand"].plot(c="k", ax=ax)
        # 右上
        ax.legend(loc="upper left", bbox_to_anchor=(1.01, 0.9, 0.2, 0.1))
        return fig, ax
