@echo off
chcp 65001 >nul
cd /d "%~dp0"
set STREAMLIT_EMAIL=
set STREAMLIT_CONSOLE_LOG_LEVEL=error
set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
echo ========================================
echo   Threads 戀愛話題監測儀表板
echo ========================================
echo.
echo 1. 開啟儀表板... (約 5 秒)
echo 2. 如果瀏覽器未自動開啟，請手動前往：
echo    http://localhost:8501
echo.
echo 按 Ctrl+C 可停止儀表板
echo ========================================
python -m streamlit run threads_monitor/dashboard.py --server.headless=false --server.port=8501 --global.developmentMode=false
pause
