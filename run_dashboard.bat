@echo off
echo Installing required packages...
python -m pip install streamlit pandas plotly numpy altair scikit-learn

echo.
echo Starting the dashboard...
python -m streamlit run src\dashboard.py

pause
