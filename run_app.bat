@echo off
echo ========================================
echo Python FinTech Toolkit - Streamlit App
echo ========================================
echo.
echo Installing dependencies...
python -m pip install -r requirements.txt
echo.
echo Starting Streamlit app...
python -m streamlit run streamlit_app.py
pause
