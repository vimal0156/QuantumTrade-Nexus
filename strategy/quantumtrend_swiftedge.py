"""
QuantumTrend SwiftEdge - Adaptive Trend-Following Strategy
Combines Supertrend, Keltner Channels, and 100-period EMA for precise signals
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict


class QuantumTrendSwiftEdge:
    """
    QuantumTrend SwiftEdge Strategy
    
    Combines:
    - Supertrend: Trend direction using ATR
    - Keltner Channels: Volatility-based breakout detection
    - 100-period EMA: Long-term trend filter
    """
    
    def __init__(
        self,
        sensitivity: int = 3,
        use_manual_settings: bool = False,
        atr_period: int = 10,
        atr_multiplier: float = 3.0,
        keltner_length: int = 20,
        keltner_multiplier: float = 1.5,
        keltner_atr_length: int = 10,
        ema_length: int = 100,
        use_simple_atr: bool = False
    ):
        """
        Initialize QuantumTrend SwiftEdge strategy
        
        Args:
            sensitivity: Signal sensitivity (1=Low, 5=High). Default=3
            use_manual_settings: If True, use manual parameters instead of sensitivity
            atr_period: ATR calculation period (manual mode)
            atr_multiplier: Supertrend ATR multiplier (manual mode)
            keltner_length: Keltner Channel EMA length (manual mode)
            keltner_multiplier: Keltner Channel ATR multiplier (manual mode)
            keltner_atr_length: Keltner Channel ATR period (manual mode)
            ema_length: EMA trend filter length (manual mode)
            use_simple_atr: Use simple moving average for ATR calculation
        """
        self.sensitivity = max(1, min(5, sensitivity))
        self.use_manual_settings = use_manual_settings
        self.use_simple_atr = use_simple_atr
        
        if use_manual_settings:
            self.atr_period = atr_period
            self.atr_multiplier = atr_multiplier
            self.keltner_length = keltner_length
            self.keltner_multiplier = keltner_multiplier
            self.keltner_atr_length = keltner_atr_length
            self.ema_length = ema_length
        else:
            # Adaptive parameters based on sensitivity
            self._set_adaptive_parameters()
    
    def _set_adaptive_parameters(self):
        """Set parameters based on sensitivity level"""
        # Sensitivity mapping: 1=Conservative, 3=Balanced, 5=Aggressive
        sensitivity_map = {
            1: {'atr': 14, 'mult': 4.0, 'kelt_len': 30, 'kelt_mult': 2.0, 'kelt_atr': 14, 'ema': 150},
            2: {'atr': 12, 'mult': 3.5, 'kelt_len': 25, 'kelt_mult': 1.75, 'kelt_atr': 12, 'ema': 125},
            3: {'atr': 10, 'mult': 3.0, 'kelt_len': 20, 'kelt_mult': 1.5, 'kelt_atr': 10, 'ema': 100},
            4: {'atr': 8, 'mult': 2.5, 'kelt_len': 15, 'kelt_mult': 1.25, 'kelt_atr': 8, 'ema': 75},
            5: {'atr': 6, 'mult': 2.0, 'kelt_len': 10, 'kelt_mult': 1.0, 'kelt_atr': 6, 'ema': 50}
        }
        
        params = sensitivity_map[self.sensitivity]
        self.atr_period = params['atr']
        self.atr_multiplier = params['mult']
        self.keltner_length = params['kelt_len']
        self.keltner_multiplier = params['kelt_mult']
        self.keltner_atr_length = params['kelt_atr']
        self.ema_length = params['ema']
    
    def calculate_atr(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Average True Range"""
        high = df['High']
        low = df['Low']
        close = df['Close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        if self.use_simple_atr:
            atr = tr.rolling(window=period).mean()
        else:
            atr = tr.ewm(span=period, adjust=False).mean()
        
        return atr
    
    def calculate_supertrend(self, df: pd.DataFrame) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Supertrend indicator
        
        Returns:
            supertrend: Supertrend line values
            direction: 1 for uptrend, -1 for downtrend
            visible: Boolean series indicating when line should be visible
        """
        atr = self.calculate_atr(df, self.atr_period)
        hl_avg = (df['High'] + df['Low']) / 2
        
        # Calculate basic bands
        upper_band = hl_avg + (self.atr_multiplier * atr)
        lower_band = hl_avg - (self.atr_multiplier * atr)
        
        # Initialize
        supertrend = pd.Series(index=df.index, dtype=float)
        direction = pd.Series(index=df.index, dtype=int)
        
        supertrend.iloc[0] = lower_band.iloc[0]
        direction.iloc[0] = 1
        
        # Calculate Supertrend
        for i in range(1, len(df)):
            # Update bands
            if df['Close'].iloc[i] > upper_band.iloc[i-1]:
                direction.iloc[i] = 1
            elif df['Close'].iloc[i] < lower_band.iloc[i-1]:
                direction.iloc[i] = -1
            else:
                direction.iloc[i] = direction.iloc[i-1]
                
                # Adjust bands
                if direction.iloc[i] == 1 and lower_band.iloc[i] < lower_band.iloc[i-1]:
                    lower_band.iloc[i] = lower_band.iloc[i-1]
                if direction.iloc[i] == -1 and upper_band.iloc[i] > upper_band.iloc[i-1]:
                    upper_band.iloc[i] = upper_band.iloc[i-1]
            
            # Set Supertrend value
            if direction.iloc[i] == 1:
                supertrend.iloc[i] = lower_band.iloc[i]
            else:
                supertrend.iloc[i] = upper_band.iloc[i]
        
        # Calculate visibility (price within ATR threshold)
        threshold_multiplier = 0.5 + (self.sensitivity - 1) * 0.375  # 0.5 to 2.0
        threshold = atr * threshold_multiplier
        
        visible = abs(df['Close'] - supertrend) <= threshold
        
        return supertrend, direction, visible
    
    def calculate_keltner_channels(self, df: pd.DataFrame) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Keltner Channels
        
        Returns:
            basis: Middle line (EMA)
            upper: Upper band
            lower: Lower band
        """
        # Calculate basis (EMA)
        basis = df['Close'].ewm(span=self.keltner_length, adjust=False).mean()
        
        # Calculate ATR for bands
        atr = self.calculate_atr(df, self.keltner_atr_length)
        
        # Calculate bands
        upper = basis + (self.keltner_multiplier * atr)
        lower = basis - (self.keltner_multiplier * atr)
        
        return basis, upper, lower
    
    def calculate_ema(self, df: pd.DataFrame) -> pd.Series:
        """Calculate long-term EMA for trend filter"""
        return df['Close'].ewm(span=self.ema_length, adjust=False).mean()
    
    def calculate_gradient_color(self, direction: pd.Series) -> pd.Series:
        """Calculate smoothed gradient value for visualization (0 to 1)"""
        # Smooth direction changes with 5-period EMA
        smoothed = direction.ewm(span=5, adjust=False).mean()
        
        # Normalize to 0-1 range (from -1 to 1)
        gradient = (smoothed + 1) / 2
        
        return gradient
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate buy/sell signals based on strategy logic
        
        Args:
            df: DataFrame with OHLC data (Open, High, Low, Close)
        
        Returns:
            DataFrame with additional columns:
            - supertrend: Supertrend line
            - st_direction: Supertrend direction (1=up, -1=down)
            - st_visible: Supertrend visibility
            - kelt_basis: Keltner Channel middle line
            - kelt_upper: Keltner Channel upper band
            - kelt_lower: Keltner Channel lower band
            - ema_100: Long-term EMA
            - gradient: Gradient color value (0-1)
            - signal: 1=Buy, -1=Sell, 0=No signal
            - position: Current position (1=Long, -1=Short, 0=Flat)
        """
        df = df.copy()
        
        # Calculate indicators
        supertrend, st_direction, st_visible = self.calculate_supertrend(df)
        kelt_basis, kelt_upper, kelt_lower = self.calculate_keltner_channels(df)
        ema_100 = self.calculate_ema(df)
        gradient = self.calculate_gradient_color(st_direction)
        
        # Add to dataframe
        df['supertrend'] = supertrend
        df['st_direction'] = st_direction
        df['st_visible'] = st_visible
        df['kelt_basis'] = kelt_basis
        df['kelt_upper'] = kelt_upper
        df['kelt_lower'] = kelt_lower
        df['ema_100'] = ema_100
        df['gradient'] = gradient
        
        # Detect trend changes
        df['st_change'] = st_direction.diff()
        
        # Initialize signal column
        df['signal'] = 0
        
        # BUY SIGNAL CONDITIONS:
        # 1. Price above 100-EMA (bullish market)
        # 2. Price breaks above Keltner upper band
        # 3. Supertrend switches to uptrend
        buy_condition = (
            (df['Close'] > df['ema_100']) &  # Price above EMA
            (df['Close'] > df['kelt_upper']) &  # Breakout above Keltner
            (df['Close'].shift(1) <= df['kelt_upper'].shift(1)) &  # Previous bar was below
            (df['st_change'] > 0)  # Supertrend changed to uptrend
        )
        
        # SELL SIGNAL CONDITIONS:
        # 1. Price below 100-EMA (bearish market)
        # 2. Price breaks below Keltner lower band
        # 3. Supertrend switches to downtrend
        sell_condition = (
            (df['Close'] < df['ema_100']) &  # Price below EMA
            (df['Close'] < df['kelt_lower']) &  # Breakout below Keltner
            (df['Close'].shift(1) >= df['kelt_lower'].shift(1)) &  # Previous bar was above
            (df['st_change'] < 0)  # Supertrend changed to downtrend
        )
        
        df.loc[buy_condition, 'signal'] = 1
        df.loc[sell_condition, 'signal'] = -1
        
        # Calculate position (for backtesting)
        df['position'] = 0
        position = 0
        
        for i in range(len(df)):
            if df['signal'].iloc[i] == 1:
                position = 1  # Enter long
            elif df['signal'].iloc[i] == -1:
                position = -1  # Enter short
            # Hold position until opposite signal
            df.loc[df.index[i], 'position'] = position
        
        return df
    
    def backtest(self, df: pd.DataFrame, initial_capital: float = 10000) -> Dict:
        """
        Backtest the strategy
        
        Args:
            df: DataFrame with OHLC data
            initial_capital: Starting capital
        
        Returns:
            Dictionary with backtest results
        """
        df = self.generate_signals(df)
        
        # Calculate returns
        df['returns'] = df['Close'].pct_change()
        df['strategy_returns'] = df['position'].shift(1) * df['returns']
        
        # Calculate cumulative returns
        df['cumulative_returns'] = (1 + df['returns']).cumprod()
        df['cumulative_strategy_returns'] = (1 + df['strategy_returns']).cumprod()
        
        # Calculate equity curve
        df['equity'] = initial_capital * df['cumulative_strategy_returns']
        
        # Calculate metrics
        total_return = (df['cumulative_strategy_returns'].iloc[-1] - 1) * 100
        buy_hold_return = (df['cumulative_returns'].iloc[-1] - 1) * 100
        
        # Calculate number of trades
        trades = df[df['signal'] != 0]
        num_trades = len(trades)
        num_buys = len(trades[trades['signal'] == 1])
        num_sells = len(trades[trades['signal'] == -1])
        
        # Calculate win rate
        trade_returns = []
        entry_price = None
        entry_type = None
        
        for i in range(len(df)):
            if df['signal'].iloc[i] != 0:
                if entry_price is not None:
                    # Close previous trade
                    if entry_type == 1:  # Long
                        ret = (df['Close'].iloc[i] - entry_price) / entry_price
                    else:  # Short
                        ret = (entry_price - df['Close'].iloc[i]) / entry_price
                    trade_returns.append(ret)
                
                # Open new trade
                entry_price = df['Close'].iloc[i]
                entry_type = df['signal'].iloc[i]
        
        # Close final trade if open
        if entry_price is not None:
            if entry_type == 1:
                ret = (df['Close'].iloc[-1] - entry_price) / entry_price
            else:
                ret = (entry_price - df['Close'].iloc[-1]) / entry_price
            trade_returns.append(ret)
        
        winning_trades = [r for r in trade_returns if r > 0]
        losing_trades = [r for r in trade_returns if r <= 0]
        
        win_rate = len(winning_trades) / len(trade_returns) * 100 if trade_returns else 0
        avg_win = np.mean(winning_trades) * 100 if winning_trades else 0
        avg_loss = np.mean(losing_trades) * 100 if losing_trades else 0
        
        # Calculate Sharpe ratio (annualized, assuming daily data)
        if df['strategy_returns'].std() != 0:
            sharpe_ratio = (df['strategy_returns'].mean() / df['strategy_returns'].std()) * np.sqrt(252)
        else:
            sharpe_ratio = 0
        
        # Calculate maximum drawdown
        cumulative = df['cumulative_strategy_returns']
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        
        results = {
            'total_return': total_return,
            'buy_hold_return': buy_hold_return,
            'num_trades': num_trades,
            'num_buys': num_buys,
            'num_sells': num_sells,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'final_equity': df['equity'].iloc[-1],
            'data': df
        }
        
        return results
    
    def get_current_signal(self, df: pd.DataFrame) -> Dict:
        """
        Get current signal and indicator values
        
        Args:
            df: DataFrame with OHLC data
        
        Returns:
            Dictionary with current values
        """
        df = self.generate_signals(df)
        
        last_row = df.iloc[-1]
        
        return {
            'price': last_row['Close'],
            'supertrend': last_row['supertrend'],
            'st_direction': 'Uptrend' if last_row['st_direction'] == 1 else 'Downtrend',
            'st_visible': last_row['st_visible'],
            'kelt_upper': last_row['kelt_upper'],
            'kelt_lower': last_row['kelt_lower'],
            'kelt_basis': last_row['kelt_basis'],
            'ema_100': last_row['ema_100'],
            'gradient': last_row['gradient'],
            'signal': 'BUY' if last_row['signal'] == 1 else ('SELL' if last_row['signal'] == -1 else 'HOLD'),
            'position': 'Long' if last_row['position'] == 1 else ('Short' if last_row['position'] == -1 else 'Flat')
        }
