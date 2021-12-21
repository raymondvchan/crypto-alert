from cdp import cdp
from datetime import datetime
import pandas as pd
from pycoingecko import CoinGeckoAPI
from config import TERRA_WALLET_ADDRESS, COINS, MASSESTS


def rtn_summary(coin_data) -> str:
    """[summary]

    Returns:
        str: Summary format
    """

    summary = """<b><u>Summary:</u></b>"""
    for x in coin_data:
        if x == "fantom":
            summary += f"""
        <b>{x}</b>:
            <u>Liquidation Price: <b>0.5827 - 3.518</b></u>
            Avg 2 Week: {coin_data[x]["avg_2_week"]}
            Avg Hourly: {coin_data[x]["avg_hourly"]}
            <b><u>Curr Price: {coin_data[x]["current_price"]}</u></b>"""
        else:
            summary += f"""
        <b>{x}</b>:
            Avg 2 Week: {coin_data[x]["avg_2_week"]}
            Avg Hourly: {coin_data[x]["avg_hourly"]}
            Curr Price: {coin_data[x]["current_price"]}"""

    return summary


def recommendations(coin_data) -> str:
    """Returns any recommended actions based on coin data

    Args:
        coin_data ([type]): [description]

    Returns:
        str: [description]
    """
    rtn_text = ""
    for coin in coin_data:
        if coin_data[coin]["current_price"] >= coin_data[coin]["avg_2_week"]:
            rtn_text += f"""[<b>{coin}] <u>Should be sold!</u></b>
Avg 2 Week [ <b>{coin_data[coin]["avg_2_week"]}</b> ]
Current [ <b>{coin_data[coin]["current_price"]}</b> ]

"""
    return rtn_text


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


def get_collaterized_debt_positions() -> dict:
    """Retrieves collateralized debt positions. Utilizing mirror protocol graphql

    Returns:
        dict: class cdp
    """
    from gql import gql, Client
    from gql.transport.aiohttp import AIOHTTPTransport

    transport = AIOHTTPTransport(url="https://graph.mirror.finance/graphql")
    client = Client(transport=transport, fetch_schema_from_transport=True)
    query = gql(
        f"""
        {{
            cdps (address: "{TERRA_WALLET_ADDRESS}" maxRatio: 350) {{
                id
                address
                token
                mintAmount
                mintValue
                collateralToken
                collateralAmount
                collateralValue
                collateralRatio
                minCollateralRatio
            }}
        }}
        """
    )
    result = client.execute(query)
    return result


if __name__ == "__main__":
    # result = get_collaterized_debt_positions()
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
        if x == "fantom":
            print("Liquidation Price: 0.5827 - 3.518")
        else:
            print(
                x,
                f"""
            Avg 2 Week: {coin_data[x]["avg_2_week"]}
            Avg Hourly: {coin_data[x]["avg_hourly"]}
            Curr Price: {coin_data[x]["current_price"]}""",
            )
    print("End of script")
