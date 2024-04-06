import traceback
import zipfile
import pandas as pd
import requests
import os
from time import sleep
from datetime import datetime
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from pathlib import Path
import yaml
import yaml.scanner
import glob
import argparse

ROOTDIR = f"{os.path.dirname(__file__)}/.."


class ElectricData:
    """電力需給実績を取得するクラス
    """

    def __init__(self, target_date=None):
        self.LIMIT = 10
        self.OUTDIR = f"{ROOTDIR}/data"
        if target_date is None:
            self.target_date = datetime.today()
        else:
            self.target_date = pd.to_datetime(target_date)
        self.yyyymm_s = [t.strftime("%Y%m") for t in pd.date_range(
            self.target_date-pd.offsets.MonthBegin(10), self.target_date, freq="MS")[::-1]]
        self.area2code = {"hokkaido": "01", "tohoku": "02", "tokyo": "03", "chubu": "04",
                          "hokuriku": "05", "kannsai": "06", "chugoku": "07", "shikoku": "08", "kyusyu": "09"}
        with open(f"{ROOTDIR}/src/detail_demand_supply_master.yml", "tr") as f:
            self.config = yaml.safe_load(f)

    def get_data(self, url_list, encoding="utf-8"):
        for no, url in enumerate(url_list):
            print(f"No {no} try getting {url}")
            res = requests.get(url)
            if res.ok:
                data = res.content.decode(encoding=encoding)
                filename = os.path.basename(url)
                filepath = f"{self.OUTDIR}/{filename}"
                with open(filepath, "wt", encoding=encoding) as f:
                    f.write(data)
                print("success")
                return filepath
            sleep(1)
        return None

    def get_chuden(self):
        base_url = "https://powergrid.chuden.co.jp/denki_yoho_content_data"
        url_list = [
            f"{base_url}/eria_jukyu_{yyyymm}_04.csv" for yyyymm in self.yyyymm_s]
        filepath = self.get_data(url_list, encoding="shift-jis")
        return filepath

    def get_touden(self):
        base_url = "https://www.tepco.co.jp/forecast/html/images"
        url_list = [
            f"{base_url}/eria_jukyu_{yyyymm}_03.csv" for yyyymm in self.yyyymm_s]
        filepath = self.get_data(url_list, encoding="utf-8")
        return filepath

    def get_kanden(self):
        base_url = "https://www.kansai-td.co.jp/interchange/denkiyoho/area-performance"
        url_list = [
            f"{base_url}/eria_jukyu_{yyyymm}_06.csv" for yyyymm in self.yyyymm_s]
        filepath = self.get_data(url_list, encoding="shift-jis")
        return filepath

    def get_kyuden(self):
        base_url = "https://www.kyuden.co.jp/td_area_jukyu/csv/"
        url_list = [
            f"{base_url}/eria_jukyu_{yyyymm}_09.csv" for yyyymm in self.yyyymm_s]
        filepath = self.get_data(url_list, encoding="shift-jis")
        return filepath

    def get_yonden(self):
        base_url = "https://www.yonden.co.jp/nw/supply_demand/csv"
        url_list = [
            f"{base_url}/eria_jukyu_{yyyymm}_08.csv" for yyyymm in self.yyyymm_s]
        filepath = self.get_data(url_list, encoding="shift-jis")
        return filepath

    def get_chugokuden(self):
        base_url = "https://www.energia.co.jp/nw/jukyuu/sys"
        url_list = [
            f"{base_url}/eria_jukyu_{yyyymm}_07.csv" for yyyymm in self.yyyymm_s]
        filepath = self.get_data(url_list, encoding="shift-jis")
        return filepath

    def get_rikuden(self):
        base_url = "https://www.rikuden.co.jp/nw/denki-yoho/csv"
        url_list = [
            f"{base_url}/eria_jukyu_{yyyymm}_05.csv" for yyyymm in self.yyyymm_s]
        filepath = self.get_data(url_list, encoding="shift-jis")
        return filepath

    def get_tohokuden(self):
        options = webdriver.ChromeOptions()
        downloadpath = str(Path(f"{ROOTDIR}/data").resolve())
        print(downloadpath)
        # 相対パスは使えないっぽい
        options.add_experimental_option("prefs", {"download.default_directory": downloadpath,
                                        "download.directory_upgrade": True, "download.prompt_for_download": False, })

        base_url = "https://setsuden.nw.tohoku-epco.co.jp/realtime_jukyu.html"
        driver = webdriver.Chrome(
            f"{ROOTDIR}/src/bin/chromedriver", options=options)
        driver.get(base_url)
        sleep(2)
        for text in ["今月分実績ダウンロード", "先月分実績ダウンロード"]:
            element = driver.find_element_by_partial_link_text(text)
            sleep(2)
            element.click()
        driver.quit()
        filepath = sorted(glob.glob(f"{ROOTDIR}/data/**02.zip*"))[0]
        return filepath

    def load_with_check(self, filepath, area_name, encoding):
        df = pd.read_csv(filepath, encoding=encoding, skiprows=1)
        org_cols = self.config[area_name]
        # check process
        col_check = (df.columns == org_cols).sum()
        if col_check == 20:
            df.columns = self.config["common_columns"]
            return df
        else:
            print("original:", org_cols, "current:", df.columns)
            raise
        return None
    # 03

    def load_tokyo(self, filepath):
        df = self.load_with_check(filepath, "tokyo", encoding="utf-8")
        df["date_time"] = pd.to_datetime(df["DATE"] + " " + df["TIME"])
        df["area_name"] = "tokyo"
        return df
    # 04

    def load_chubu(self, filepath):
        df = self.load_with_check(filepath, "tokyo", encoding="shift-jis")
        df["date_time"] = pd.to_datetime(df["DATE"] + " " + df["TIME"])
        df["area_name"] = "chubu"
        return df
    # 05

    def load_hokuriku(self, filepath):
        df = self.load_with_check(filepath, "tokyo", encoding="shift-jis")
        df["date_time"] = pd.to_datetime(df["DATE"] + " " + df["TIME"])
        df["area_name"] = "hokuriku"
        return df

    def load_kansai(self, filepath):
        df = self.load_with_check(filepath, "tokyo", encoding="shift-jis")
        df["date_time"] = pd.to_datetime(df["DATE"] + " " + df["TIME"])
        df["area_name"] = "kansai"
        return df

    def load_chugoku(self, filepath):
        df = self.load_with_check(filepath, "tokyo", encoding="shift-jis")
        df["date_time"] = pd.to_datetime(df["DATE"] + " " + df["TIME"])
        df["area_name"] = "chugoku"
        return df

    def load_shikoku(self, filepath):
        df = self.load_with_check(filepath, "tokyo", encoding="utf-8")
        df["date_time"] = pd.to_datetime(df["DATE"] + " " + df["TIME"])
        df["area_name"] = "shikoku"
        return df

    def load_kyusyu(self, filepath):
        df = self.load_with_check(filepath, "tokyo", encoding="utf-8")
        df["date"] = pd.to_datetime(df["DATE"].astype("str"), format="%Y%m%d")
        # 24:00はTimestampに変換できないので00:00にして日付を１日進める
        idx_24h = df["TIME"] == "24:00"
        df.loc[idx_24h, "date"] = df.loc[idx_24h, "date"] + pd.offsets.Day(1)
        df.loc[idx_24h, "TIME"] = "00:00"
        df["date_time"] = pd.to_datetime(
            df["date"].dt.strftime("%Y-%m-%d") + " " + df["TIME"])
        # おそらく九州電力だけ前30分を見ているので、他と合わせるために30分戻す
        df["date_time"] = df["date_time"] - pd.offsets.Minute(30)
        df["area_name"] = "kyusyu"
        return df

    def load_tohoku(self, filepath):
        ext = os.path.splitext(filepath)
        if ext == ".zip":
            with zipfile.ZipFile("../data/realtime_jukyu_202404_02.zip") as zf:
                filelist = zf.namelist()
                df_list = []
                for filename in filelist:
                    with zf.open(filename) as f:
                        df_list.append(self.load_with_check(
                            f, encoding="shift-jis"))
            df = pd.concat(df_list)
        else:
            df = self.load_with_check(filepath, encoding="shift-jis")
        df["area_name"] = "tohoku"
        df["date_time"] = pd.to_datetime(df["DATE"] + " " + df["TIME"])
        return df

    def execute(self):
        get_methods = [self.get_tohokuden, self.get_touden, self.get_chuden, self.get_rikuden,
                       self.get_kanden, self.get_chugokuden, self.get_yonden, self.get_kyuden]

        load_methods = [self.load_tohoku, self.load_tokyo, self.load_chubu, self.load_hokuriku,
                        self.load_kansai, self.load_chugoku, self.load_shikoku, self.load_kyusyu]

        for i, (get_method, load_method) in enumerate(zip(get_methods, load_methods)):
            try:
                print(i)
                filepath = get_method()
                df = load_method(filepath)
                # DB登録の処理
            except Exception as e:
                print(traceback.format_exc())
                continue
    def load_manually(self, filepath, area_name):
        if area_name=="tohoku":
            df =self.load_tohoku(filepath)
        elif area_name=="tokyo":
            df = self.load_tokyo(filepath)
        elif area_name=="chubu":
            df = self.load_chubu(filepath)
        elif area_name=="hokuriku":
            df = self.load_hokuriku(filepath)
        elif area_name=="kansai":
            df = self.load_kansai(filepath)
        elif area_name=="chugoku":
            df = self.load_chugoku(filepath)
        elif area_name=="shikoku":
            df =self.load_shikoku(filepath)
        elif area_name=="kyusyu":
            df = self.load_kyusyu(filepath)
        else:
            raise 
        return df



if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--date", help="取得する月,指定がなければ当月を設定する")
    args.add_argument("--file", default=None,
                      help="手動でダウンロードしたファイルを指定する,またエリア名を指定する必要がある")
    args.add_argument("--area_name", help="手動で登録する際の対象エリア名")

    if args.file is None:
        elec = ElectricData(args.date)
        elec.execute()
    else:
        elec = ElectricData
        df = elec.load_manually(args.area_name)
        # upsert処理