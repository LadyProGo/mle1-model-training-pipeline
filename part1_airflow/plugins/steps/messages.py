import logging
import os
from pathlib import Path

import requests
from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR / ".env")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

TELEGRAM_TIMEOUT_SECONDS = 60


def _send(message: str) -> None:
    if not TOKEN or not CHAT_ID:
        logging.warning("Telegram notification skipped: credentials are not configured.")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
    }

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=TELEGRAM_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        logging.info("Telegram notification sent successfully.")
    except requests.exceptions.RequestException as error:
        error_message = str(error).replace(TOKEN, "***") if TOKEN else str(error)
        logging.warning(f"Telegram notification failed and was ignored: {error_message}")
    except Exception as error:
        logging.warning(f"Telegram notification failed and was ignored: {type(error).__name__}")


def send_telegram_success_message(context) -> None:
    dag_id = context["dag"].dag_id
    run_id = context.get("run_id", "unknown_run")
    _send(f"DAG {dag_id} finished successfully. Run: {run_id}")


def send_telegram_failure_message(context) -> None:
    dag_id = context["dag"].dag_id
    task_instance = context.get("task_instance")
    task_id = task_instance.task_id if task_instance else "unknown_task"
    run_id = context.get("run_id", "unknown_run")
    _send(f"DAG {dag_id} failed. Task: {task_id}. Run: {run_id}")
