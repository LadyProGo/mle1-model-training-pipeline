import logging
import os
from pathlib import Path

from airflow.providers.telegram.hooks.telegram import TelegramHook
from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR / ".env")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def _send(message: str) -> None:
    if not TOKEN or not CHAT_ID:
        logging.warning("Telegram notification skipped: credentials are not configured.")
        return

    try:
        hook = TelegramHook(token=TOKEN, chat_id=CHAT_ID)
        hook.send_message({"chat_id": CHAT_ID, "text": message})
    except Exception as error:
        logging.warning(f"Telegram notification failed and was ignored: {error}")


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
