

## 快速啟動（本機）

```bash
pip install -r requirements.txt
python -m threads_monitor.main run
python -m threads_monitor.main dashboard
```

或雙擊 `start_dashboard.bat`

## 雲端部署

一鍵部署到 Streamlit Community Cloud：

[![Deploy to Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/new?template=https://github.com/rfsee/M-ThreadsMonitor)

或手動步驟：
1. 前往 https://share.streamlit.io
2. 用 GitHub 登入
3. 點 "Create app" → 選 `rfsee/M-ThreadsMonitor`
4. Main file path 填入 `threads_monitor/dashboard.py`
5. 點 Deploy

部署完成後即可在任何裝置開啟瀏覽器使用。
