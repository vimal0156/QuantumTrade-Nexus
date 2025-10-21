# Python FinTech Toolkit - Streamlit App

A comprehensive financial analysis toolkit that consolidates multiple technical analysis tools into an interactive web application.

## 🚀 Features

This Streamlit application combines all the functionality from the Jupyter notebooks into a single, easy-to-use interface:

1. **📊 Market Data Explorer** - Download and explore market data using yfinance
2. **📉 Stock Charts** - Interactive candlestick charts with volume
3. **📈 Moving Averages** - Calculate and visualize SMAs across different timeframes
4. **📐 Slope Analysis** - Compute trend slopes using linear regression
5. **🎯 Market Stage Detection** - Identify Stan Weinstein's market stages
6. **💰 Risk/Reward Calculator** - Calculate position sizing and R-multiples
7. **📊 Stochastic RSI** - TradingView-compatible Stochastic RSI indicator
8. **🔢 Consecutive Integers** - Utility for finding consecutive integer groups

## 📦 Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Access the app:**
   - The app will automatically open in your default browser
   - Default URL: http://localhost:8501

## 🎯 Usage

### Market Data Explorer
- Enter ticker symbols (comma-separated)
- Select interval (daily, weekly, monthly)
- Download and visualize market data
- Compare multiple stocks

### Stock Charts
- Generate candlestick, OHLC, or line charts
- Toggle volume display
- View summary statistics

### Moving Averages
- Calculate SMAs for different timeframes
- Customize MA periods
- Visualize trends

### Slope Analysis
- Calculate trend slopes using linear regression
- Identify uptrends and downtrends
- Visualize slope lines on charts

### Market Stage Detection
- Detect Stan Weinstein's 4 market stages
- Customize detection parameters
- Identify current market stage

### Risk/Reward Calculator
- Calculate position sizing
- Determine R-multiples
- Plan entry and exit points
- Support for both long and short positions

### Stochastic RSI
- TradingView-compatible implementation
- Customizable parameters
- Identify overbought/oversold conditions

### Consecutive Integers
- Find groups of consecutive integers
- Useful for pattern detection
- Visualize results

## 🏗️ Project Structure

```
pythonfintech-main/
├── streamlit_app.py          # Main Streamlit application
├── requirements.txt           # Python dependencies
├── utils/                     # Utility modules
│   ├── __init__.py
│   ├── data_fetcher.py       # Market data fetching
│   ├── indicators.py         # Technical indicators
│   ├── risk_calculator.py    # Risk/reward calculations
│   ├── stage_detector.py     # Market stage detection
│   └── consecutive_integers.py # Integer grouping utility
└── [notebook directories]     # Original Jupyter notebooks
```

## 🔧 Configuration

The app uses default parameters that can be adjusted through the UI:
- Moving average periods
- Stage detection thresholds
- Risk percentages
- Indicator parameters

## 📊 Data Source

All market data is fetched from Yahoo Finance using the `yfinance` library. Data is real-time and free to use.

## 🛠️ Technical Stack

- **Streamlit** - Web application framework
- **yfinance** - Market data provider
- **pandas** - Data manipulation
- **numpy** - Numerical computing
- **matplotlib** - Plotting library
- **mplfinance** - Financial charts
- **scipy** - Scientific computing
- **seaborn** - Statistical visualization

## 📝 Notes

- The app requires an internet connection to fetch market data
- Some indicators require minimum data points to calculate
- Historical data availability depends on the ticker and Yahoo Finance

## 🐛 Troubleshooting

**Issue: Module not found errors**
- Solution: Ensure all dependencies are installed: `pip install -r requirements.txt`

**Issue: No data available for ticker**
- Solution: Verify the ticker symbol is correct and available on Yahoo Finance

**Issue: Charts not displaying**
- Solution: Check that matplotlib backend is properly configured

## 📄 License

This project consolidates educational materials for financial analysis and trading.

## 🤝 Contributing

Feel free to extend the functionality by:
1. Adding new technical indicators
2. Implementing additional chart types
3. Enhancing the UI/UX
4. Adding export functionality

## 📧 Support

For issues or questions, please refer to the original Jupyter notebooks for detailed explanations of each tool's methodology.
