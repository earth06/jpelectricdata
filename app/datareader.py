import sqlite3
import pandas as pd
from pages.common import Config


class DataReader:
    def __init__(self):
        self.DBPATH = f"../data/data.db"
        self.cfg = Config()

    def read_sql(self, sql):
        conn = sqlite3.connect(self.DBPATH)

        df = pd.read_sql(sql, conn)
        conn.close()
        return df

    def read_demand_supply(self, begin, end, ignore_negative_value=False):
        sql = f"""
            SELECT * FROM detail_demand_supply WHERE 1=1
            AND date_time BETWEEN '{begin}' AND '{end}'
        """
        df = self.read_sql(sql)
        if ignore_negative_value:
            df[self.cfg.demand_supply_names] = df[self.cfg.demand_supply_names].where(
                df[self.cfg.demand_supply_names] >= 0, 0
            )

        return df[["date_time", "area_name"] + self.cfg.demand_supply_names]

    def read_spot_price(self, begin, end):
        sql = f"""
            SELECT * FROM spot_price WHERE 1=1
            AND date_time BETWEEN '{begin}' AND '{end}'
        """
        df = self.read_sql(sql)
        return df
