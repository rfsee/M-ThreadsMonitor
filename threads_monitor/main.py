#!/usr/bin/env python
"""
Threads 每週熱門貼文監測工具

Usage:
    python main.py run         # 執行爬取與分析
    python main.py dashboard   # 啟動互動儀表板
    python main.py setup-scheduler  # 設定每天早上9點自動更新
    python main.py remove-scheduler # 移除排程
    python main.py status      # 查看排程狀態
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

from threads_monitor.config import Config
from threads_monitor.scraper import ThreadsScraper
from threads_monitor.analyzer import PostAnalyzer
from threads_monitor.scheduler import (
    setup_scheduler,
    remove_scheduler,
    get_scheduler_status,
)

WARN = "[WARN]"


def safe_print(text: str):
    try:
        print(text)
    except UnicodeEncodeError:
        cleaned = text.encode("ascii", "replace").decode("ascii")
        print(cleaned)


def cmd_run():
    config = Config()
    os.makedirs(config.data_dir_path, exist_ok=True)

    safe_print("=" * 55)
    safe_print("  [愛心] Threads 戀愛話題熱門貼文監測")
    safe_print(f"  [日曆] 執行時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    safe_print(f"  [搜尋] 關鍵字：{', '.join(config.keywords[:5])}...")
    safe_print(f"  [圖表] 門檻：讚數 >= {config.min_likes}")
    safe_print("=" * 55)

    scraper = ThreadsScraper(config)
    posts = scraper.scrape()

    safe_print(f"\n[筆記] 共取得 {len(posts)} 則貼文")

    analyzer = PostAnalyzer(config)
    result = analyzer.analyze_posts(posts)

    with open(config.output_path, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    safe_print(f"[儲存] 貼文資料已儲存：{config.output_path}")

    with open(config.analysis_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    safe_print(f"[儲存] 分析結果已儲存：{config.analysis_path}")

    safe_print("\n" + "=" * 55)
    safe_print("  [圖表] 分析摘要")
    safe_print("=" * 55)
    safe_print(f"  總貼文數：{result['total_posts']}")
    safe_print(f"  總讚數：{result['total_likes']:,}")
    safe_print(f"  平均讚數：{result['avg_likes']:,}")
    safe_print(f"  主題分佈：")
    for topic, count in sorted(result["topic_distribution"].items()):
        safe_print(f"    - {topic}: {count} 則")
    safe_print(f"\n  主題摘要：")
    for summary in result.get("topic_summaries", []):
        safe_print(f"\n  [標記] {summary['topic']}（{summary['post_count']} 則）")
        safe_print(f"    {summary['summary']}")
    safe_print("\n[完成] 執行以下指令開啟儀表板：")
    safe_print("   python main.py dashboard\n")


def cmd_dashboard():
    import subprocess
    import webbrowser
    import threading
    import time

    config = Config()
    dashboard_path = os.path.join(
        os.path.dirname(__file__), "dashboard.py"
    )

    safe_print("[啟動] 啟動互動式儀表板...")
    safe_print(f"   路徑：{dashboard_path}")
    safe_print(f"   預覽: 請開啟瀏覽器前往 http://localhost:8501")
    safe_print("")

    def open_browser():
        time.sleep(4)
        try:
            webbrowser.open("http://localhost:8501")
        except Exception:
            pass

    threading.Thread(target=open_browser, daemon=True).start()

    env = os.environ.copy()
    env["STREAMLIT_EMAIL"] = ""
    env["STREAMLIT_CONSOLE_LOG_LEVEL"] = "error"
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

    cmd = [
        sys.executable, "-m", "streamlit", "run", dashboard_path,
        "--server.headless=false",
        "--server.port=8501",
        "--global.developmentMode=false",
    ]
    subprocess.run(cmd, env=env)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    commands = {
        "run": cmd_run,
        "dashboard": cmd_dashboard,
        "setup-scheduler": lambda: safe_print(setup_scheduler()),
        "remove-scheduler": lambda: safe_print(remove_scheduler()),
        "status": lambda: safe_print(get_scheduler_status()),
    }

    if cmd in commands:
        commands[cmd]()
    else:
        safe_print(f"未知指令：{cmd}\n")
        print(__doc__)


if __name__ == "__main__":
    main()
