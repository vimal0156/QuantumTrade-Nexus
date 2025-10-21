"""
Stan Weinstein's Market Stage Detection
"""

from typing import Optional, Dict, List, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
from matplotlib import patches

from .indicators import calculate_slope
from .consecutive_integers import find_consecutive_integers


class Stage(Enum):
    """Market stage enumeration"""
    STAGE_I = "stage_1"
    STAGE_II = "stage_2"
    STAGE_III = "stage_3"
    STAGE_IV = "stage_4"

    def integer_value(self, sep: str = "_") -> int:
        """Return the integer value of the stage"""
        return int(self.value.split(sep)[-1])

    def __str__(self):
        return self.value


# Define a custom type for the detected stage ranges
DetectedStages = Dict[Stage, List[Tuple[int, int]]]


@dataclass(frozen=True)
class StageDetectorResult:
    """Result from stage detection"""
    df: pd.DataFrame
    stages: DetectedStages


class StageDetector:
    """
    Detect Stan Weinstein's market stages using moving averages
    """

    def __init__(
            self,
            df: pd.DataFrame,
            fast_ma_size: int = 10,
            slow_ma_size: int = 40,
            min_consec: int = 4,
            slope_window: int = 4,
            rising_threshold: float = 0.0005,
            falling_threshold: float = -0.0005,
            flat_range: float = 0.0002
    ) -> None:
        """
        Initialize the stage detector
        
        Args:
            df: DataFrame with OHLCV data
            fast_ma_size: Fast moving average period
            slow_ma_size: Slow moving average period
            min_consec: Minimum consecutive periods for stage detection
            slope_window: Window size for slope calculation
            rising_threshold: Threshold for rising trend
            falling_threshold: Threshold for falling trend
            flat_range: Range for flat trend detection
        """
        self.df = df
        self.fast_ma_size = fast_ma_size
        self.slow_ma_size = slow_ma_size
        self.min_consec = min_consec
        self.slope_window = slope_window
        self.rising_threshold = rising_threshold
        self.falling_threshold = falling_threshold
        self.flat_range = flat_range

        # Determine the fast and slow MA column names
        self.col_fast_ma = f"{self.fast_ma_size}MA"
        self.col_slow_ma = f"{self.slow_ma_size}MA"

        # Determine the slope column names
        self.col_fast_ma_slope = f"{self.col_fast_ma}_slope"
        self.col_slow_ma_slope = f"{self.col_slow_ma}_slope"

        # Initialize a dictionary to store the detected stages
        self.stages: DetectedStages = {}

    def detect(self) -> StageDetectorResult:
        """
        Detect market stages
        
        Returns:
            StageDetectorResult with processed DataFrame and detected stages
        """
        # Preprocess the dataframe by computing MAs and slope values
        self._compute_indicators()

        # Detect each of the four stages
        self._detect_stage_i()
        self._detect_stage_ii()
        self._detect_stage_iii()
        self._detect_stage_iv()

        # Construct and return the stage detector result
        return StageDetectorResult(
            df=self.df,
            stages=self.stages
        )

    def _compute_indicators(self) -> None:
        """Compute moving averages and slopes"""
        # Compute the fast and slow MAs, then drop any NaN rows
        self.df[self.col_fast_ma] = self.df["Close"].rolling(
            window=self.fast_ma_size
        ).mean()
        self.df[self.col_slow_ma] = self.df["Close"].rolling(
            window=self.slow_ma_size
        ).mean()
        self.df = self.df.dropna().copy()

        # Calculate slope for both the fast and slow MAs
        self.df[self.col_fast_ma_slope] = self.df[self.col_fast_ma].rolling(
            window=self.slope_window
        ).apply(calculate_slope)
        self.df[self.col_slow_ma_slope] = self.df[self.col_slow_ma].rolling(
            window=self.slope_window
        ).apply(calculate_slope)
        self.df = self.df.dropna().copy()

    def _detect_stage_i(self) -> None:
        """Detect Stage I (Accumulation)"""
        idxs = np.where(
            (self.df[self.col_fast_ma] < self.df[self.col_slow_ma]) &
            (self.df[self.col_fast_ma_slope] > self.rising_threshold) &
            (np.abs(self.df[self.col_slow_ma]) > self.flat_range)
        )[0]

        self.stages[Stage.STAGE_I] = find_consecutive_integers(
            idxs,
            min_consec=self.min_consec
        )

    def _detect_stage_ii(self) -> None:
        """Detect Stage II (Advancing)"""
        idxs = np.where(
            (self.df[self.col_fast_ma] > self.df[self.col_slow_ma]) &
            (self.df[self.col_fast_ma_slope] > self.rising_threshold) &
            (self.df[self.col_slow_ma_slope] > self.rising_threshold)
        )[0]

        self.stages[Stage.STAGE_II] = find_consecutive_integers(
            idxs,
            min_consec=self.min_consec
        )

    def _detect_stage_iii(self) -> None:
        """Detect Stage III (Distribution)"""
        idxs = np.where(
            (self.df[self.col_fast_ma] > self.df[self.col_slow_ma]) &
            (self.df[self.col_fast_ma_slope] < self.falling_threshold) &
            (np.abs(self.df[self.col_slow_ma]) > self.flat_range)
        )[0]

        self.stages[Stage.STAGE_III] = find_consecutive_integers(
            idxs,
            min_consec=self.min_consec
        )

    def _detect_stage_iv(self) -> None:
        """Detect Stage IV (Declining)"""
        idxs = np.where(
            (self.df[self.col_fast_ma] < self.df[self.col_slow_ma]) &
            (self.df[self.col_fast_ma_slope] < self.falling_threshold) &
            (self.df[self.col_slow_ma_slope] < self.falling_threshold)
        )[0]

        self.stages[Stage.STAGE_IV] = find_consecutive_integers(
            idxs,
            min_consec=self.min_consec
        )

    def what_stage(self, input_date: datetime) -> Optional[Stage]:
        """
        Determine the stage at a specific date
        
        Args:
            input_date: Date to check
        
        Returns:
            Stage at the given date, or None if no stage detected
        """
        # Grab the row index of the input date
        row_idx = self.df.index.get_loc(input_date)

        # Loop over the computed stage indexes
        for (stage_name, periods) in self.stages.items():
            # Loop over the starting and ending indexes for the period
            for (start, end) in periods:
                # Check to see if the input date index falls within this range
                if start <= row_idx <= end:
                    return stage_name

        return None


# Default stage color mapping for visualization
DEFAULT_STAGE_COLORS = {
    Stage.STAGE_I: "yellowgreen",
    Stage.STAGE_II: "seagreen",
    Stage.STAGE_III: "indigo",
    Stage.STAGE_IV: "red",
}


def plot_stage_detections(
        stage_result: StageDetectorResult,
        title: str,
        stage_colors: Optional[Dict[str, str]] = None
) -> plt.Figure:
    """
    Plot market stages on a candlestick chart
    
    Args:
        stage_result: StageDetectorResult from stage detection
        title: Chart title
        stage_colors: Optional custom color mapping for stages
    
    Returns:
        Matplotlib figure
    """
    # Check if the stage colors has not been supplied
    if stage_colors is None:
        stage_colors = DEFAULT_STAGE_COLORS

    # Initialize a new figure, then create a subplot for the stages
    fig = mpf.figure(figsize=(14, 7), style="yahoo")
    ax = plt.subplot(1, 1, 1)

    # Take the rectangle height to be the highest high in the dataframe
    rect_height = stage_result.df["High"].max()

    # Loop over the stages and periods
    for (stage, periods) in stage_result.stages.items():
        # Loop over the periods in each stage
        for (start, end) in periods:
            # Create a rectangle to visualize the stage
            rect = patches.Rectangle(
                xy=(start, 0),
                width=end - start,
                height=rect_height,
                color=stage_colors[stage],
                alpha=0.25
            )

            # Compute the center x-coordinate of the rectangle
            cx = start + ((end - start) / 2.0)
            ax.annotate(
                str(stage.integer_value()),
                xy=(cx, rect_height * 0.95),
                color="black",
                weight="bold",
                fontsize=8,
                ha="center"
            )

            # Add the rectangle and text to the axis
            ax.add_patch(rect)
            ax.autoscale_view()

    # Create additional plots for the moving averages
    addt_plots = [
        mpf.make_addplot(
            stage_result.df["10MA"],
            color="royalblue",
            ax=ax
        ),
        mpf.make_addplot(
            stage_result.df["40MA"],
            color="maroon",
            ax=ax
        ),
    ]

    # Plot the candlesticks with the MAs
    mpf.plot(
        stage_result.df,
        ax=ax,
        addplot=addt_plots,
        type="candle"
    )

    # Set the figure title and convert to a tight layout
    fig.suptitle(title, fontsize=12)
    plt.tight_layout()

    return fig
