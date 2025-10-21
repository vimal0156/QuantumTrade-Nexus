"""
Risk/Reward calculator for trading position sizing
"""

from typing import Optional, Union, List
from dataclasses import dataclass


@dataclass(frozen=True)
class TradeRiskParams:
    """Data schema for risk/reward parameters for a given trade"""
    amount_to_risk: float
    percent_risk: float
    shares_to_trade: float
    total_investment: float


@dataclass(frozen=True)
class RLevelOutput:
    """Data schema for R-level outputs"""
    r_level: int
    potential_pl: float
    price: float


class RiskRewardCalculator:
    """
    Calculator for position sizing and R-multiples in trading
    """

    # Define the list of default R-values to compute
    DEFAULT_R_VALUES = [1, 2, 3, 4, 5]

    def __init__(
            self,
            total_account_value: float,
            entry_point: float,
            stop_loss: float,
            risk_rate: float = 0.01,
            is_short: bool = False
    ) -> None:
        """
        Initialize the risk/reward calculator
        
        Args:
            total_account_value: Total account value in dollars
            entry_point: Entry price for the trade
            stop_loss: Stop loss price
            risk_rate: Percentage of account to risk (default 1%)
            is_short: True if this is a short trade, False for long
        """
        # For short trades, the entry point must be *below* the stop loss
        if is_short and entry_point >= stop_loss:
            raise ValueError(
                "For short trades, `entry_point` must be less than `stop_loss`"
            )

        # For long trades, the entry point but be *above* the stop loss
        if not is_short and entry_point <= stop_loss:
            raise ValueError(
                "For long trades, `entry_point` must be greater than `stop_loss`"
            )
        
        # Store the total account value, entry point, stop loss, risk rate, and
        # trade direction
        self.total_account_value = total_account_value
        self.entry_point = entry_point
        self.stop_loss = stop_loss
        self.risk_rate = risk_rate
        self.is_short = is_short

        # Calculate the amount to risk on each trade
        self.amount_to_risk = self.total_account_value * self.risk_rate

        # Determine the price difference between the entry point and stop loss,
        # then derive the number of shares to enter based on the amount to risk
        # and trade direction
        self.price_delta = abs(self.entry_point - self.stop_loss)
        self.shares_to_trade = self.amount_to_risk / self.price_delta

        # Calculate the total amount of money to be invested based on the
        # number of shares and the entry point
        self.total_investment = self.shares_to_trade * self.entry_point

        # Derive the overall risk percentage of the account
        amount_ratio = self.amount_to_risk / self.total_account_value
        self.risk_pct_of_account = amount_ratio * 100

    def get_risk_parameters(self) -> TradeRiskParams:
        """
        Get the calculated risk parameters
        
        Returns:
            TradeRiskParams object with risk calculations
        """
        return TradeRiskParams(
            amount_to_risk=self.amount_to_risk,
            percent_risk=self.risk_pct_of_account,
            shares_to_trade=self.shares_to_trade,
            total_investment=self.total_investment
        )

    def r_levels(
            self,
            r_levels: Optional[List[Union[int, float]]] = None
    ) -> List[RLevelOutput]:
        """
        Calculate R-levels and corresponding prices
        
        Args:
            r_levels: List of R-levels to calculate (default [1,2,3,4,5])
        
        Returns:
            List of RLevelOutput objects
        """
        # Check to see if risk/reward levels were not provided
        if not isinstance(r_levels, list):
            # Use the default risk/reward levels
            r_levels = self.DEFAULT_R_VALUES

        # Initialize the list of R-level outputs
        results = []

        # Loop over the levels
        for r in r_levels:
            # Calculate the potential profit/loss
            potential_pl = r * self.amount_to_risk

            # Determine the price based on trade direction (for shorts, price
            # *decreases* as R *rises*, while for longs price *increases* as
            # R *rises)
            direction = -1 if self.is_short else 1
            price = self.entry_point + (direction * r * self.price_delta)

            # Update the results list
            results.append(RLevelOutput(
                r_level=r,
                potential_pl=potential_pl,
                price=price
            ))

        return results

    def r_level_at_price(self, price: float) -> float:
        """
        Calculate the R-level for a given price
        
        Args:
            price: Target price
        
        Returns:
            R-level at the given price
        """
        # Compute the r-level for the input price based on trade direction
        direction = -1 if self.is_short else 1
        r_level = direction * (price - self.entry_point) / self.price_delta
        
        return r_level
