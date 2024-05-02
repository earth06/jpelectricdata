from electric_analysis import ElectricAnalysis
from atproto import Client
import os
import matplotlib
from datetime import datetime, timedelta


begin = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
end = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

matplotlib.use("Agg")
BSKY_ID = os.environ.get("BSKY_ID")
BSKY_PASS = os.environ.get("BSKY_PASSWD")

anal = ElectricAnalysis()
anal.load_demand_supply(begin=begin, end=end)
anal.plot_all_demand_supply(save=True)

client = Client()
client.login(BSKY_ID, BSKY_PASS)

with open("../example/all_area_demand_supply.jpg", "br") as f:
    img = f.read()
client.send_image("電力需給", img, "demand_supply")
