@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo   Threads 熱門貼文資料更新
echo ========================================
python -m threads_monitor.main run
echo.
echo 完成！按任意鍵關閉...
pause >nul
