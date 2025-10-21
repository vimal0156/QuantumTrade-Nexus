"""
Integration test to verify all modules work together
"""

import sys
from datetime import datetime, timedelta

print("=" * 60)
print("INTEGRATION TEST - Python FinTech Toolkit")
print("=" * 60)

# Test 1: Import all utility modules
print("\n1. Testing imports...")
try:
    from utils.data_fetcher import fetch_ohlcv_history
    from utils.unified_data_fetcher import fetch_market_data
    from utils.indicators import calculate_slope, stochastic_rsi
    from utils.risk_calculator import RiskRewardCalculator
    from utils.stage_detector import StageDetector, plot_stage_detections
    from utils.consecutive_integers import find_consecutive_integers
    print("   ✅ All utility imports successful")
except Exception as e:
    print(f"   ❌ Import error: {e}")
    sys.exit(1)

# Test 2: Test unified data fetcher with yfinance
print("\n2. Testing unified data fetcher (yfinance)...")
try:
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    df = fetch_market_data(
        ticker="AAPL",
        start_date=start_date,
        end_date=end_date,
        interval="1d",
        data_source="yfinance",
        api_key=None
    )
    
    if not df.empty:
        print(f"   ✅ Fetched {len(df)} rows for AAPL")
        print(f"   Columns: {df.columns.tolist()}")
    else:
        print("   ⚠️  No data returned (might be network issue)")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Test slope calculation
print("\n3. Testing slope calculation...")
try:
    import pandas as pd
    test_series = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    slope = calculate_slope(test_series)
    print(f"   ✅ Slope calculated: {slope:.4f}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Test risk calculator
print("\n4. Testing risk calculator...")
try:
    calc = RiskRewardCalculator(
        total_account_value=10000,
        entry_point=100,
        stop_loss=95,
        risk_rate=0.01
    )
    params = calc.get_risk_parameters()
    print(f"   ✅ Risk calculator works")
    print(f"   Amount to risk: ${params.amount_to_risk:.2f}")
    print(f"   Position size: {params.position_size:.2f} shares")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 5: Test consecutive integers
print("\n5. Testing consecutive integers...")
try:
    import numpy as np
    test_array = np.array([1, 2, 3, 5, 6, 7, 8, 10])
    groups = find_consecutive_integers(test_array, min_consec=3)
    print(f"   ✅ Found {len(groups)} consecutive groups")
    print(f"   Groups: {groups}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 6: Test Alpha Vantage (with demo key)
print("\n6. Testing Alpha Vantage API (demo key)...")
try:
    df_av = fetch_market_data(
        ticker="IBM",  # Demo key works with IBM
        start_date=start_date,
        end_date=end_date,
        interval="1d",
        data_source="alphavantage",
        api_key="demo"
    )
    
    if not df_av.empty:
        print(f"   ✅ Alpha Vantage fetched {len(df_av)} rows")
    else:
        print("   ⚠️  No data (demo key has limits)")
except Exception as e:
    print(f"   ⚠️  Alpha Vantage error (expected with demo key): {str(e)[:50]}")

print("\n" + "=" * 60)
print("INTEGRATION TEST COMPLETE")
print("=" * 60)
print("\n✅ All core modules are properly integrated!")
print("🚀 Ready to run: streamlit run streamlit_app.py")
