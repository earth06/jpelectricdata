import matplotlib.pyplot as plt
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os
import numpy as np
import matplotlib.patches as mpatches
import argparse
import japanize_matplotlib

plt.style.use("ggplot")

ROOTDIR = f"{os.path.dirname(__file__)}/.."


class ElectricAnalysis:
    def __init__(self):
        self.jplabels = [
            "原子力",
            "地熱",
            "水力",
            "火力(LNG)",
            "火力(石炭)",
            "火力(石油)",
            "火力(その他)",
            "バイオマス",
            "風力",
            "太陽光",
            "揚水",
            "蓄電池",
            "連系線",
            "その他",
        ]
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
        self.areas = [
            "hokkaido",
            "tohoku",
            "tokyo",
            "hokuriku",
            "chubu",
            "kansai",
            "chugoku",
            "shikoku",
            "kyusyu",
        ]
        self.jpareas = [
            "北海道",
            "東北",
            "東京",
            "北陸",
            "中部",
            "関西",
            "中国",
            "四国",
            "九州",
        ]

    def load_demand_supply(
        self, begin: str = None, end: str = None, ignore_negative_value=True
    ):
        if begin is None:
            begin = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
        if end is None:
            end = datetime.today().strftime("%Y-%m-%d 23:59:59")
        self.begin = begin
        self.end = end
        conn = sqlite3.connect(f"{ROOTDIR}/data/data.db")
        sql = f"""
            SELECT * FROM detail_demand_supply 
            WHERE date_time BETWEEN '{self.begin}' AND '{self.end}'
        """
        self.df_demand = pd.read_sql(sql, conn, parse_dates=["date_time"])
        if ignore_negative_value:
            self.df_demand[self.labels] = self.df_demand[self.labels].where(
                self.df_demand[self.labels] >= 0, 0
            )
        conn.close()
        return

    def load_spot_price(self, begin: str = None, end: str = None):
        if begin is None:
            begin = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
        if end is None:
            end = datetime.today().strftime("%Y-%m-%d 23:59:59")
        self.begin = begin
        self.end = end
        conn = sqlite3.connect(f"{ROOTDIR}/data/data.db")
        sql = f"""
            SELECT * FROM spot_price 
            WHERE date_time BETWEEN '{self.begin}' AND '{self.end}'
        """
        self.df_jepx = pd.read_sql(sql, conn, parse_dates=["date_time"])
        conn.close()
        return 

    def plot_demand_supply(self, area_name="chubu", figsize=(18, 8), legend=True, alpha=1):
        fig, ax = plt.subplots(figsize=figsize)
        tmp = self.df_demand.query(f"area_name=='{area_name}'").copy()
        tmp.index = pd.to_datetime(tmp["date_time"])
        tmp.rename(
            columns={
                label: jplabel for label, jplabel in zip(self.labels, self.jplabels)
            },
            inplace=True,
        )
        tmp[self.jplabels].plot(kind="area", color=self.colors, ax=ax,legend=False, alpha=alpha)
        tmp["area_demand"].plot(c="r", ax=ax, legend=False, marker=".")
        # 右上
        if legend:
            ax.legend(loc="upper left", bbox_to_anchor=(1.01, 0.9, 0.2, 0.1))
        return fig, ax

    def plot_all_demand_supply(self, figsize=(16, 13), save=True):
        fig = plt.figure(figsize=figsize)
        ax = np.zeros(9, dtype=np.object_)
        area_names = self.df_demand["area_name"].unique()
        for i, (area_name, jp_area_name) in enumerate(zip(self.areas, self.jpareas)):
            if area_name not in area_names:
                continue
            ax[i] = fig.add_subplot(3, 3, i + 1)
            tmp = self.df_demand.query(f"area_name=='{area_name}'").copy()
            tmp.index = pd.to_datetime(tmp["date_time"])
            tmp.rename(
                columns={
                    label: jplabel for label, jplabel in zip(self.labels, self.jplabels)
                },
                inplace=True,
            )
            tmp[self.jplabels].plot(
                kind="area", color=self.colors, ax=ax[i], legend=False, alpha=0.8
            )
            tmp["area_demand"].plot(c="k", ax=ax[i], legend=False)
            ax[i].set_xlabel("")
            ax[i].set_title(jp_area_name)
            ax[i].grid(axis="x", which="minor", zorder=-1)
            ax[i].set_ylabel("[MW]")
            ax[i].set_xlim(self.begin, self.end)
            if i < 6:
                ax[i].tick_params(labelbottom=False)
            if i % 3 != 0:
                ax[i].set_ylabel("")

        # 凡例
        patches = [
            mpatches.Patch(color=color, label=label)
            for color, label in zip(self.colors, self.labels)
        ]
        fig.legend(
            handles=patches, loc="upper left", bbox_to_anchor=(0.9, 0.8, 0.2, 0.1)
        )
        fig.suptitle("エリア需給実績速報値")
        fig.subplots_adjust(hspace=0.25)
        if save:
            fig.savefig(
                f"{ROOTDIR}/example/all_area_demand_supply.jpg", bbox_inches="tight"
            )
        return fig, ax


if __name__ == "__main__":
    import matplotlib

    matplotlib.use("Agg")
    parser = argparse.ArgumentParser()
    parser.add_argument("--begin", default=None, help="plot begin YYYY-MM-DD")
    parser.add_argument("--end", default=None, help="plot end YYYY-MM-DD")
    args = parser.parse_args()
    elec = ElectricAnalysis()
    elec.load_demand_supply(begin=args.begin, end=args.end)
    elec.plot_all_demand_supply()
