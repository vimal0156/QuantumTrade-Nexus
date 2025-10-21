# Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies

Open a terminal/command prompt in this directory and run:

```bash
pip install -r requirements.txt
```

This will install:
- streamlit
- pandas
- numpy
- yfinance
- matplotlib
- mplfinance
- scipy
- seaborn

### Step 2: Run the Application

**Option A: Using the batch file (Windows)**
```bash
run_app.bat
```

**Option B: Using command line**
```bash
streamlit run streamlit_app.py
```

**Option C: Using Python**
```bash
python -m streamlit run streamlit_app.py
```

### Step 3: Access the App

The app will automatically open in your browser at:
```
http://localhost:8501
```

## 📱 Using the App

1. **Select a tool** from the sidebar navigation
2. **Enter parameters** (ticker symbols, dates, etc.)
3. **Click the action button** (e.g., "Fetch Data", "Calculate", etc.)
4. **View results** - charts, tables, and metrics will appear

## 🎯 Example Workflows

### Analyze a Stock
1. Go to "Stock Charts"
2. Enter ticker: AAPL
3. Select days: 90
4. Click "Generate Chart"

### Calculate Risk/Reward
1. Go to "Risk/Reward Calculator"
2. Enter account value: $25,000
3. Enter entry point: $100
4. Enter stop loss: $95
5. Click "Calculate"

### Detect Market Stages
1. Go to "Market Stage Detection"
2. Enter ticker: SPY
3. Select years: 4
4. Click "Detect Stages"

## ⚡ Tips

- **Multiple tickers**: Separate with commas (e.g., AAPL,NVDA,META)
- **Data availability**: Some tickers may have limited historical data
- **Performance**: Larger date ranges take longer to process
- **Refresh**: Use the browser refresh button to reset the app

## 🐛 Common Issues

**"Module not found" error**
```bash
pip install -r requirements.txt
```

**"streamlit: command not found"**
```bash
python -m pip install streamlit
```

**Port already in use**
```bash
streamlit run streamlit_app.py --server.port 8502
```

## 📚 Learn More

- See `README_STREAMLIT.md` for detailed documentation
- Check the original Jupyter notebooks for methodology details
- Visit https://docs.streamlit.io for Streamlit documentation

## 🎉 Enjoy!

You now have a complete financial analysis toolkit at your fingertips!
