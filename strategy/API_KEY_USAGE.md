# 🔑 Using API Keys with QuantumTrend SwiftEdge

## Overview

The QuantumTrend SwiftEdge strategy now uses the **unified data fetcher** which supports multiple data sources with API keys, just like the rest of the app!

---

## ✅ What Changed

### Before:
- Used yfinance directly
- No API key support
- Could fail with yfinance errors

### After:
- Uses unified_data_fetcher
- Supports 3 data sources:
  - **Yahoo Finance** (free, no API key)
  - **Alpha Vantage** (free tier with API key)
  - **Polygon.io** (free tier with API key)
- Same data source as rest of app
- More reliable data fetching

---

## 🚀 How to Use

### Method 1: Streamlit App (Automatic)

The Streamlit integration automatically uses the **global data source** from the sidebar!

1. Run the app:
   ```bash
   python -m streamlit run streamlit_app.py
   ```

2. Select data source in sidebar:
   - Yahoo Finance (default)
   - Alpha Vantage API (enter key)
   - Polygon.io API (enter key)

3. Navigate to "🌊 QuantumTrend SwiftEdge"

4. Run backtest - it will use your selected data source!

**No code changes needed!** ✅

---

### Method 2: Test Script

The test script now supports data sources:

#### Option A: Use Yahoo Finance (Default)
```bash
cd strategy
python test_quantumtrend.py
```

No changes needed - uses yfinance by default.

#### Option B: Use Alpha Vantage

Edit `test_quantumtrend.py` line 218-219:

```python
# Change from:
data_source = "yfinance"
api_key = None

# To:
data_source = "alphavantage"
api_key = "YOUR_ALPHA_VANTAGE_KEY"
```

Then run:
```bash
python test_quantumtrend.py
```

#### Option C: Use Polygon.io

Edit `test_quantumtrend.py` line 218-219:

```python
data_source = "polygon"
api_key = "YOUR_POLYGON_KEY"
```

---

### Method 3: Python API

```python
from strategy import QuantumTrendSwiftEdge
from utils.unified_data_fetcher import fetch_market_data
from datetime import datetime, timedelta

# Fetch data with API key
end_date = datetime.now()
start_date = end_date - timedelta(days=365)

# Option 1: Yahoo Finance (no API key)
df = fetch_market_data("SPY", start_date, end_date, "1d", "yfinance", None)

# Option 2: Alpha Vantage
df = fetch_market_data("SPY", start_date, end_date, "1d", "alphavantage", "YOUR_KEY")

# Option 3: Polygon
df = fetch_market_data("SPY", start_date, end_date, "1d", "polygon", "YOUR_KEY")

# Run strategy
strategy = QuantumTrendSwiftEdge(sensitivity=3)
results = strategy.backtest(df)

print(f"Return: {results['total_return']:.2f}%")
```

---

## 🔑 Getting API Keys

### Alpha Vantage (Free Tier)
1. Go to: https://www.alphavantage.co/support/#api-key
2. Enter your email
3. Get instant free API key
4. **Limits:** 25 calls/day, 5 calls/minute

### Polygon.io (Free Tier)
1. Go to: https://polygon.io/
2. Sign up for free account
3. Get API key from dashboard
4. **Limits:** 5 calls/minute

---

## 💡 Which Data Source to Use?

### Yahoo Finance (yfinance)
**Pros:**
- ✅ Free, no API key needed
- ✅ Works immediately
- ✅ Good for testing

**Cons:**
- ⚠️ Can be unreliable
- ⚠️ Rate limiting
- ⚠️ Occasional errors

**Best for:** Quick tests, learning

---

### Alpha Vantage
**Pros:**
- ✅ Reliable API
- ✅ Free tier available
- ✅ Good data quality
- ✅ 25 calls/day

**Cons:**
- ⚠️ Requires API key
- ⚠️ Daily limit
- ⚠️ Slower for multiple tickers

**Best for:** Daily backtesting, production use

---

### Polygon.io
**Pros:**
- ✅ Very reliable
- ✅ High quality data
- ✅ Good free tier
- ✅ Fast API

**Cons:**
- ⚠️ Requires API key
- ⚠️ 5 calls/minute limit

**Best for:** Production use, frequent backtesting

---

## 📊 Streamlit Integration

The Streamlit page automatically uses the global data source!

### How It Works:

1. **Global Settings** (in sidebar):
   ```
   🌐 Data Source
   Select Data Provider: [Yahoo Finance ▼]
   
   Alpha Vantage API Key: [_________]
   Polygon.io API Key: [_________]
   ```

2. **Strategy Page** uses these settings:
   ```python
   # Automatically gets data source and API key
   source, api_key = get_data_source_params()
   
   # Fetches data using your settings
   df = fetch_market_data(ticker, start, end, "1d", source, api_key)
   ```

3. **No manual configuration needed!**

---

## 🔧 Troubleshooting

### Error: "No data available"

**Solution:**
1. Check ticker symbol is correct
2. Try different data source
3. Verify API key is valid
4. Check API rate limits

### Error: "API key required"

**Solution:**
1. Get free API key (see above)
2. Enter in sidebar (Streamlit)
3. Or edit test script (standalone)

### Error: "Rate limit exceeded"

**Solution:**
1. Wait a few minutes
2. Switch to different data source
3. Use Yahoo Finance for unlimited calls

### yfinance Errors

**Solution:**
1. Switch to Alpha Vantage or Polygon
2. They're more reliable
3. Free tiers available

---

## 📝 Example Configurations

### Configuration 1: Free & Easy
```python
data_source = "yfinance"
api_key = None
```
**Use case:** Testing, learning, quick backtests

### Configuration 2: Reliable Daily Use
```python
data_source = "alphavantage"
api_key = "YOUR_ALPHA_VANTAGE_KEY"
```
**Use case:** Daily strategy testing, production

### Configuration 3: High-Frequency Testing
```python
data_source = "polygon"
api_key = "YOUR_POLYGON_KEY"
```
**Use case:** Multiple backtests, production systems

---

## ✅ Summary

**QuantumTrend SwiftEdge now supports API keys!**

### What You Get:
- ✅ 3 data source options
- ✅ More reliable data fetching
- ✅ Same as rest of app
- ✅ Automatic in Streamlit
- ✅ Easy to configure

### How to Use:
1. **Streamlit:** Just select data source in sidebar
2. **Test Script:** Edit lines 218-219
3. **Python API:** Pass data_source and api_key

### Recommended:
- **Testing:** Use yfinance (free, easy)
- **Production:** Use Alpha Vantage or Polygon (reliable)

---

**No more yfinance errors!** 🎉

Get your free API keys and enjoy reliable data fetching!
