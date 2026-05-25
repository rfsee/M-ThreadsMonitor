# Threads 戀愛話題熱門貼文監測工具

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://M-ThreadsMonitor.streamlit.app)

## 功能

- 自動爬取 Threads 上與戀愛相關的熱門貼文
- 篩選讚數 ≥ 1000 的貼文
- 主題分類（工具推薦、觀點爭論、案例分享、抱怨、幽默梗、求助請益）
- 每群自動生成摘要
- 互動式儀表板

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
