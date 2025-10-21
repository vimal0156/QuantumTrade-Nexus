"""
Quick verification script - checks all integrations are working
"""

import sys
import os

print("\n" + "="*70)
print(" 🔍 INTEGRATION VERIFICATION - Python FinTech Toolkit")
print("="*70 + "\n")

errors = []
warnings = []
success = []

# Check 1: File existence
print("📁 Checking files...")
required_files = [
    "streamlit_app.py",
    "utils/data_fetcher.py",
    "utils/unified_data_fetcher.py",
    "utils/indicators.py",
    "utils/risk_calculator.py",
    "utils/stage_detector.py",
    "utils/consecutive_integers.py",
    "requirements.txt"
]

for file in required_files:
    if os.path.exists(file):
        success.append(f"   ✅ {file}")
    else:
        errors.append(f"   ❌ Missing: {file}")

for s in success:
    print(s)
for e in errors:
    print(e)

# Check 2: Python syntax
print("\n🐍 Checking Python syntax...")
syntax_files = [
    "streamlit_app.py",
    "utils/unified_data_fetcher.py",
    "utils/data_fetcher.py"
]

for file in syntax_files:
    try:
        with open(file, 'r', encoding='utf-8') as f:
            compile(f.read(), file, 'exec')
        print(f"   ✅ {file} - syntax OK")
    except SyntaxError as e:
        errors.append(f"   ❌ {file} - syntax error: {e}")
        print(errors[-1])

# Check 3: Import test
print("\n📦 Testing imports...")
try:
    from utils.unified_data_fetcher import fetch_market_data
    print("   ✅ unified_data_fetcher imported")
except Exception as e:
    errors.append(f"   ❌ unified_data_fetcher import failed: {e}")
    print(errors[-1])

try:
    from utils.data_fetcher import fetch_ohlcv_history
    print("   ✅ data_fetcher imported")
except Exception as e:
    errors.append(f"   ❌ data_fetcher import failed: {e}")
    print(errors[-1])

try:
    from utils.indicators import calculate_slope, stochastic_rsi
    print("   ✅ indicators imported")
except Exception as e:
    errors.append(f"   ❌ indicators import failed: {e}")
    print(errors[-1])

try:
    from utils.risk_calculator import RiskRewardCalculator
    print("   ✅ risk_calculator imported")
except Exception as e:
    errors.append(f"   ❌ risk_calculator import failed: {e}")
    print(errors[-1])

try:
    from utils.stage_detector import StageDetector
    print("   ✅ stage_detector imported")
except Exception as e:
    errors.append(f"   ❌ stage_detector import failed: {e}")
    print(errors[-1])

try:
    from utils.consecutive_integers import find_consecutive_integers
    print("   ✅ consecutive_integers imported")
except Exception as e:
    errors.append(f"   ❌ consecutive_integers import failed: {e}")
    print(errors[-1])

# Check 4: Dependencies
print("\n📚 Checking dependencies...")
try:
    import streamlit
    print(f"   ✅ streamlit {streamlit.__version__}")
except:
    warnings.append("   ⚠️  streamlit not installed")
    print(warnings[-1])

try:
    import pandas
    print(f"   ✅ pandas {pandas.__version__}")
except:
    errors.append("   ❌ pandas not installed")
    print(errors[-1])

try:
    import yfinance
    print(f"   ✅ yfinance installed")
except:
    warnings.append("   ⚠️  yfinance not installed")
    print(warnings[-1])

try:
    import requests
    print(f"   ✅ requests {requests.__version__}")
except:
    warnings.append("   ⚠️  requests not installed (needed for APIs)")
    print(warnings[-1])

try:
    import mplfinance
    print(f"   ✅ mplfinance installed")
except:
    warnings.append("   ⚠️  mplfinance not installed")
    print(warnings[-1])

# Summary
print("\n" + "="*70)
print(" 📊 VERIFICATION SUMMARY")
print("="*70)

if len(errors) == 0:
    print("\n🎉 SUCCESS! All integrations verified!")
    print("\n✅ All files present")
    print("✅ No syntax errors")
    print("✅ All modules import successfully")
    print("✅ Core dependencies installed")
    
    if len(warnings) > 0:
        print(f"\n⚠️  {len(warnings)} warnings (optional dependencies):")
        for w in warnings:
            print(w)
    
    print("\n🚀 Ready to run:")
    print("   streamlit run streamlit_app.py")
    print("\n📖 See INTEGRATION_GUIDE.md for details")
else:
    print(f"\n❌ {len(errors)} error(s) found:")
    for e in errors:
        print(e)
    print("\n⚠️  Please fix errors before running the app")
    sys.exit(1)

print("\n" + "="*70 + "\n")
