from logging import warning


class tarot_market:
    """Tarot.to market attributes"""

    def __init__(
        self,
        asset_1: str,
        asset_2: str,
        lower_bound: float,
        upper_bound: float,
        warning_threshold: float = 0.2,
    ):
        """Initialize market with lower / upper liquidation values

        Args:
            asset_1 (str): CoinGecko Asset ID
            asset_2 (str): CoinGecko Asset ID
            lower_bound (float): lower bound of asset_1 / asset_2
            upper_bound (float): upper bound of asset_1 / asset_2
            warning_threshold (float, optional): Pads the liquidation boundaries by this percent. Defaults to 0.25.
        """
        self.asset_1 = asset_1
        self.asset_2 = asset_2
        self.warning_threshold = warning_threshold
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def get_asset_data(self) -> dict:
        """Retrieves assets summary from CoinGecko

        Returns:
            dict: Dictionary of asset prices
        """
        from pycoingecko import CoinGeckoAPI

        cg = CoinGeckoAPI()
        current_prices = cg.get_price(
            ids=[self.asset_1, self.asset_2], vs_currencies="usd"
        )
        return current_prices

    def check_liquidation_bounds(self) -> bool:
        """Gather asset data and checks if current prices are within safe liquidation bounds

        Returns:
            bool: True if within safe liquidation bounds
        """
        prices = self.get_asset_data()
        current_price = prices[self.asset_1]["usd"] / prices[self.asset_2]["usd"]
        self.current_price = current_price
        warning_threshold = self.warning_threshold * (
            self.upper_bound - self.lower_bound
        )
        self.lower_bound_warning = self.lower_bound + warning_threshold
        self.upper_bound_warning = self.upper_bound - warning_threshold

        if self.lower_bound_warning <= self.current_price <= self.upper_bound_warning:
            return True
        else:
            return False


if __name__ == "__main__":
    import time
    import datetime
    from tarot_config import markets

    refresh_time = 10

    try:
        while True:
            for market in markets:
                cur_market = tarot_market(
                    market["pairs"][0],
                    market["pairs"][1],
                    market["lower_bound"],
                    market["upper_bound"],
                )
                is_safe_zone = cur_market.check_liquidation_bounds()
                if not is_safe_zone:
                    print("")
                    print("***************ALERT**************")
                    print(datetime.datetime.now())
                    print(" ", "Pool", cur_market.asset_1, cur_market.asset_2)
                    print("  LIQUIDATION WARNING!!")
                    print(
                        " Warning Threshold hit:",
                        cur_market.lower_bound_warning,
                        "-",
                        cur_market.upper_bound_warning,
                    )
                    print(
                        " Liq Range:",
                        cur_market.lower_bound,
                        "-",
                        cur_market.upper_bound,
                    )
                    print(" ", "Current Price:", cur_market.current_price)
                else:
                    print(datetime.datetime.now(), "clear")

            time.sleep(refresh_time)

    except KeyboardInterrupt:
        pass
