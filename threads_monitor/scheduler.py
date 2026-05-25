import os
import sys
import subprocess
from datetime import datetime
from typing import Optional

TASK_NAME = "ThreadsMonitorDailyUpdate"
SCRIPT_NAME = "main.py"


def get_project_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def get_python_path() -> str:
    return sys.executable or "python"


def get_script_path() -> str:
    return os.path.join(get_project_dir(), SCRIPT_NAME)


def setup_scheduler() -> str:
    python_path = get_python_path()
    script_path = get_script_path()

    task_cmd = (
        f'schtasks /Create /SC DAILY /TN "{TASK_NAME}" '
        f'/TR "\'{python_path}\' \'{script_path}\' run" '
        f'/ST 09:00 /F'
    )

    try:
        result = subprocess.run(
            task_cmd, shell=True, capture_output=True, text=True,
        )
        if result.returncode == 0:
            return f"✅ 排程任務已建立！每天 09:00 自動執行。\n{result.stdout}"
        else:
            return (
                f"⚠ 建立排程失敗（可能需要管理員權限）:\n"
                f"{result.stderr}\n\n"
                f"請以系統管理員身分執行以下命令手動建立：\n\n"
                f"  {task_cmd}"
            )
    except Exception as e:
        return f"❌ 發生錯誤：{e}"


def remove_scheduler() -> str:
    cmd = f'schtasks /Delete /TN "{TASK_NAME}" /F'
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return "✅ 排程任務已刪除"
        else:
            return f"⚠ 刪除排程失敗：{result.stderr}"
    except Exception as e:
        return f"❌ 發生錯誤：{e}"


def get_scheduler_status() -> str:
    cmd = f'schtasks /Query /TN "{TASK_NAME}" /FO LIST'
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return f"✅ 排程狀態：\n{result.stdout}"
        else:
            return "❌ 尚未建立排程任務"
    except Exception as e:
        return f"⚠ 查詢失敗：{e}"
