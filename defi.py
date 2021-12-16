from datetime import datetime
import pandas as pd
from pycoingecko import CoinGeckoAPI
from config import COINS


def rtn_summary() -> str:
    """[summary]

    Returns:
        str: Summary format
    """
    coin_data = get_coin_data()
    summary = """Summary:"""
    for x in coin_data:
        summary += f"""
        {x}:
            Avg 2 Week: {coin_data[x]["avg_2_week"]}
            Avg Hourly: {coin_data[x]["avg_hourly"]}
            Curr Price: {coin_data[x]["current_price"]}"""

    return summary


def get_coin_data() -> dict:
    """Retrieves coin prices

    Returns:
        dict: Dictionary of coin [averages and current price]
    """
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
    return coin_data


if __name__ == "__main__":
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

    print(datetime.now())
    print("""Summary:""")
    for x in coin_data:
        print(
            x,
            f"""
            Avg 2 Week: {coin_data[x]["avg_2_week"]}
            Avg Hourly: {coin_data[x]["avg_hourly"]}
            Curr Price: {coin_data[x]["current_price"]}""",
        )
    print("End of script")
