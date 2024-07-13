import pandas as pd
import sqlite3
import os
import yaml
import argparse

ROOTDIR = f"{os.path.dirname(__file__)}/.." # noqa


class JEPXData():
    def __init__(self):
        with open(f"{ROOTDIR}/src/detail_demand_supply_master.yml", "tr") as f:
            self.config = yaml.safe_load(f)
        self.org_columns = self.config["original_columns"]["spot_columns"]

    def upsert(self, df: pd.DataFrame):
        conn = sqlite3.connect(f"{ROOTDIR}/data/data.db")
        col_names = ",".join(self.config["spot_columns"])
        values = ",".join(["?"] * len(self.config["spot_columns"]))
        sql = f"""
            INSERT OR REPLACE INTO spot_price({col_names})
            VALUES ({values})
        """
        df["date_time"] = df["date_time"].dt.strftime("%Y-%m-%d %H:%M")
        data_list = [tuple(row) for row in df[self.config["db_columns"]].values]
        conn.executemany(sql, data_list)
        conn.commit()
        conn.close()
        return 0

    def format_columns(self, df):
        if df.columns == self.org_columns:
            raise
        else:
            # date_time列を定義

            # カラムをrename
            
            # 整形したdfを返す
            df_fmt = df
            return df_fmt

    def get_jepx_spot_price(self, filepath):
        pass