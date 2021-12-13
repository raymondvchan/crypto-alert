from datetime import datetime
import pandas as pd
from pycoingecko import CoinGeckoAPI
from config import COINS

cg = CoinGeckoAPI()

coin_data = {}
current_prices = cg.get_price(ids=COINS, vs_currencies="usd")
for coin in COINS:
    coin_data[coin] = {}

    # Gather coin history
    price_daily = cg.get_coin_market_chart_by_id(coin, "usd", 14, interval="daily")
    df = pd.DataFrame(price_daily["prices"])
    coin_data[coin]["avg_2_week"] = df[1].mean()

    price_hourly = cg.get_coin_market_chart_by_id(coin, "usd", 1, interval="hourly")
    df = pd.DataFrame(price_hourly["prices"])
    coin_data[coin]["avg_hourly"] = df[1].mean()

    coin_data[coin]["current_price"] = current_prices[coin]["usd"]

    # Check if trade should happen
    if coin_data[coin]["current_price"] >= coin_data[coin]["avg_2_week"]:
        print(
            f"""[{coin}] Should be sold. Avg 2 Week [{coin_data[coin]["avg_2_week"]}]  |  Current [{coin_data[coin]["current_price"]}]"""
        )
print("End of script")
