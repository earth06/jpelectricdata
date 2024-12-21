import sqlite3
import pandas as pd


class DataReader:
    def __init__(self):
        self.DBPATH = f"../data/data.db"

    def read_sql(self, sql):
        conn = sqlite3.connect(self.DBPATH)
        df = pd.read_sql(sql, conn)
        conn.close()
        return df

    def read_demand_supply(self, begin, end):
        sql = f"""
            SELECT * FROM detail_demand_supply WHERE 1=1
            AND date_time BETWEEN '{begin}' AND '{end}'
        """
        df = self.read_sql(sql)
        return df

    def read_spot_price(self, begin, end):
        sql = f"""
            SELECT * FROM spot_price WHERE 1=1
            AND date_time BETWEEN '{begin}' AND '{end}'
        """
        df = self.read_sql(sql)
        return df
