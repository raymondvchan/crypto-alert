class cdp:
    """Asset class to have attributes of price, collateral, qty, thresholds etc.."""

    def __init__(self, asset_id: str):
        """Initialize asset

        Args:
            asset_id (str): asset_id should match coingecko symobl ID
        """
        self.asset_id = asset_id
