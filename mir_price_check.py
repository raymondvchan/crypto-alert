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


def get_asset(asset) -> dict:
    from gql import gql, Client
    from gql.transport.aiohttp import AIOHTTPTransport

    transport = AIOHTTPTransport(url="https://graph.mirror.finance/graphql")
    client = Client(transport=transport, fetch_schema_from_transport=True)
    query = gql(
        f"""
        {{
            asset (token: "{asset}") {{
                symbol
                name
                token
                pair
                status
                prices {{
                oraclePrice
                price
                }}
            }}
        }}
        """
    )
    result = client.execute(query)
    return result


if __name__ == "__main__":
    import time
    import datetime

    buy_threshold = 35.6
    refresh_time = 60
    try:
        while True:
            mIAU = "terra10h7ry7apm55h4ez502dqdv9gr53juu85nkd4aq"
            data = get_asset(mIAU)
            if float(data["asset"]["prices"]["price"]) >= buy_threshold:
                print("")
                print("***************ALERT**************")
                print("          ***** BUY ******        ")
                print(" ", datetime.datetime.now())
                print(" ", data["asset"]["symbol"])
                print("   Price:", data["asset"]["prices"]["price"])
                print(" O_Price:", data["asset"]["prices"]["oraclePrice"])
                print("          ***** BUY ******        ")
                print("***************ALERT**************")
                print("")
            else:
                print("")
                print(datetime.datetime.now())
                print(" ", data["asset"]["symbol"])
                print("   Price:", data["asset"]["prices"]["price"])
                print(" O_Price:", data["asset"]["prices"]["oraclePrice"])
            time.sleep(refresh_time)

    except KeyboardInterrupt:
        pass
