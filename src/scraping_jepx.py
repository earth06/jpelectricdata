import argparse
import os
import sqlite3
from datetime import datetime

import pandas as pd
import yaml

ROOTDIR = f"{os.path.dirname(__file__)}/.."  # noqa


class JEPXData:
    def __init__(self):
        with open(f"{ROOTDIR}/src/detail_demand_supply_master.yml", "tr") as f:
            self.config = yaml.safe_load(f)
        self.org_columns = self.config["original_columns"]["spot_columns"]

    def upsert(self, df_input: pd.DataFrame):
        df = df_input.copy()
        conn = sqlite3.connect(f"{ROOTDIR}/data/data.db")
        col_names = ",".join(self.config["spot_columns"])
        values = ",".join(["?"] * len(self.config["spot_columns"]))
        sql = f"""
            INSERT OR REPLACE INTO spot_price({col_names})
            VALUES ({values})
        """
        df["date_time"] = df["date_time"].dt.strftime("%Y-%m-%d %H:%M")
        data_list = [tuple(row) for row in df[self.config["spot_columns"]].values]
        conn.executemany(sql, data_list)
        conn.commit()
        conn.close()
        return 0

    def format_columns(self, df_raw):
        df = df_raw.copy()
        diff = df.columns.difference(self.org_columns)
        if len(diff) > 0:
            raise
        else:
            # date_time列を定義
            timecode2time = {i + 1: f"{i // 2:02d}:{(i % 2) * 30:02d}" for i in range(48)}
            df["time"] = df["時刻コード"].apply(lambda x: timecode2time[x])
            df["年月日"] = pd.to_datetime(df["年月日"] + " " + df["time"])
            # カラムをrename
            jp2en = {
                jp: en
                for jp, en in zip(
                    self.config["original_columns"]["spot_columns"],
                    self.config["spot_columns"],
                )
            }
            # 整形したdfを返す
            df_fmt = df.rename(columns=jp2en).drop(columns="time")
            return df_fmt

    def get_jepx_spot_price(self, year=None):
        if year is None:
            today = datetime.now()
            if today.month <= 3:
                year = today.year - 1
            else:
                year = today.year
        df = pd.read_csv(f"http://www.jepx.jp/market/excel/spot_{year}.csv", encoding="shift-jis")
        df = df[self.org_columns].copy()
        return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", default=None, help="data year")
    args = parser.parse_args()
    jepx = JEPXData()
    df = jepx.get_jepx_spot_price(year=args.year)
    df_fmt = jepx.format_columns(df)
    jepx.upsert(df_fmt)
    print("end correctly")
