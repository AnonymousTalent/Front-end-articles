# -*- coding: utf-8 -*-
import asyncio
import logging
import json
import hmac
import hashlib
from datetime import datetime, time, timedelta
from typing import Dict, List
from aiohttp import ClientSession, ClientError
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from retry import retry
from cryptography.fernet import Fernet
import aiofiles
import os
import csv
import time as time_module
from pathlib import Path
import gzip

# Import the configuration from the dedicated config file
from config import CONFIG

# Ensure directories exist
for dir_path in [CONFIG["log_dir"], CONFIG["evidence_dir"], CONFIG["config_backup_dir"], CONFIG["report_dir"]]:
    Path(dir_path).mkdir(parents=True, exist_ok=True)

# Logging setup
logging.basicConfig(
    filename=f"{CONFIG['log_dir']}/log_{datetime.now().strftime('%Y%m%d')}.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Config backup and restore
async def backup_config():
    backup_path = f"{CONFIG['config_backup_dir']}/config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        current_config_str = json.dumps(CONFIG, indent=2, ensure_ascii=False)
        async with aiofiles.open(backup_path, "w", encoding="utf-8") as f:
            await f.write(current_config_str)
        logging.info(f"Configuration backed up to {backup_path}")
    except Exception as e:
        logging.error(f"Failed to backup config: {e}")


async def restore_config():
    # This function would be used to load a specific backup if needed.
    # For now, we load the main config.py on startup.
    logging.info("Configuration loaded from config.py")


# Log cleanup and compression
async def clean_old_logs():
    cutoff_date = datetime.now() - timedelta(days=CONFIG["log_retention_days"])
    log_dir = CONFIG["log_dir"]
    for filename in os.listdir(log_dir):
        if filename.startswith("log_") and not filename.endswith(".gz"):
            try:
                file_date_str = filename.split("_")[1].split(".")[0]
                file_date = datetime.strptime(file_date_str, "%Y%m%d")
                if file_date < cutoff_date:
                    file_path = os.path.join(log_dir, filename)
                    with open(file_path, "rb") as f_in:
                        with gzip.open(f"{file_path}.gz", "wb") as f_out:
                            f_out.writelines(f_in)
                    os.remove(file_path)
                    logging.info(f"Compressed and deleted old log: {filename}")
            except Exception as e:
                logging.error(f"Failed to process log {filename}: {e}")

# API Signature Verification
def generate_signature(payload: Dict) -> str:
    return hmac.new(CONFIG["api_secret"].encode(), json.dumps(payload, sort_keys=True).encode(), hashlib.sha256).hexdigest()

# Check for peak hours
def is_peak_hour():
    current_time = datetime.now().time()
    return time(11, 0) <= current_time <= time(14, 0) or time(17, 0) <= current_time <= time(20, 0)

# Module health check
async def health_check_task():
    while CONFIG["running"]:
        for module in CONFIG["active_modules"]:
            if CONFIG["health_status"][module] != "OK":
                logging.warning(f"Module {module} is unhealthy: {CONFIG['health_status'][module]}. Attempting recovery.")
                # In a real system, recovery logic would go here.
                CONFIG["health_status"][module] = "OK" # Simulate recovery
                await notify_multi_channel(f"Module {module} recovered.", priority="high")
        await asyncio.sleep(300)  # Check every 5 minutes

# --- MODULE IMPLEMENTATIONS ---

@retry(ClientError, tries=CONFIG["retry_attempts"], delay=2)
async def dispatch_module(session: ClientSession) -> None:
    start_time = time_module.time()
    try:
        orders = []
        for platform, config in CONFIG["platforms"].items():
            # This is a mock API call. In reality, you'd call the real platform API.
            logging.info(f"Fetching orders from {platform}...")
            # MOCK DATA
            platform_orders = [{"id": f"{platform[:2]}{i}", "price": 50 + i*5, "user_rating": 4.5, "distance": 2.5} for i in range(3)]
            for order in platform_orders:
                order["platform"] = platform
                order["platform_weight"] = config.get("weight", 1.0)
            orders.extend(platform_orders)

        order_density = len(orders) / max(1, len(CONFIG["platforms"]))

        async def predict_order_value(orders: List[Dict]) -> float:
            prices = [o["price"] for o in orders if "price" in o]
            base_threshold = (sum(prices) / len(prices) * 1.1) if prices else CONFIG["order_threshold"]
            return base_threshold * 1.2 if is_peak_hour() else base_threshold * 0.9

        threshold = await predict_order_value(orders)

        prioritized_orders = []
        for order in orders:
            price = order.get("price", 0)
            user_rating = order.get("user_rating", 4.0)
            distance = order.get("distance", 1.0)
            time_factor = 1.2 if is_peak_hour() else 0.8
            value_score = (price * (user_rating / 5.0) / (distance + 0.1) *
                           order["platform_weight"] * time_factor * (1 + order_density * 0.1))

            if value_score > 50: order["priority"] = "high"
            elif 40 <= value_score <= 50: order["priority"] = "medium"
            else: order["priority"] = "low"
            order["value_score"] = value_score
            prioritized_orders.append(order)

        prioritized_orders.sort(key=lambda o: o["value_score"], reverse=True)

        active_orders_count = 0
        for order in prioritized_orders:
            if active_orders_count >= CONFIG["max_concurrent_orders"]:
                logging.info("Max concurrent orders reached.")
                break
            if order["value_score"] >= threshold:
                logging.info(f"Dispatching order {order['id']} from {order['platform']} with score {order['value_score']:.2f}")
                # await accept_order(session, order) # This would be the real call
                active_orders_count += 1
                await notify_multi_channel(f"Accepted {order['priority']} priority order {order['id']}", priority=order["priority"])

        CONFIG["health_status"]["dispatch"] = "OK"
    except Exception as e:
        logging.error(f"Dispatch module failed: {e}", exc_info=True)
        CONFIG["health_status"]["dispatch"] = f"Error: {e}"
    finally:
        CONFIG["performance_metrics"]["dispatch"]["time"] = time_module.time() - start_time

# Other modules would be implemented similarly...

async def payout_module(session: ClientSession):
    logging.info("Payout module running...")
    await asyncio.sleep(5) # Simulate work
    logging.info("Payout module finished.")

async def collection_module(session: ClientSession):
    logging.info("Collection module running...")
    await asyncio.sleep(5) # Simulate work
    logging.info("Collection module finished.")

async def marketing_module(session: ClientSession):
    logging.info("Marketing module running...")
    await asyncio.sleep(5) # Simulate work
    logging.info("Marketing module finished.")

# --- NOTIFICATION AND TELEGRAM ---

async def notify_multi_channel(message: str, chat_id: str = None, priority: str = "normal"):
    if not chat_id:
        chat_id = "YOUR_ADMIN_CHAT_ID" # Default admin chat

    bot = Bot(token=CONFIG["telegram_token"])
    prefix = "🚨 [URGENT] " if priority == "high" else ""

    try:
        await bot.send_message(chat_id=chat_id, text=f"{prefix}{message}")
    except Exception as e:
        logging.error(f"Failed to send Telegram message: {e}")

    # LINE Notify integration would go here
    # async with ClientSession() as session:
    # ...

async def status_command(update, context):
    keyboard = [
        [InlineKeyboardButton("📊 Metrics", callback_data="metrics"), InlineKeyboardButton("📈 Chart", callback_data="chart")],
        [InlineKeyboardButton("⏸️ Pause System", callback_data="pause"), InlineKeyboardButton("▶️ Resume System", callback_data="resume")],
        [InlineKeyboardButton("⚙️ Config", callback_data="config_template"), InlineKeyboardButton("📋 Perf Report", callback_data="performance")]
    ]
    await update.message.reply_text("Commander, what is your bidding?", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_callback(update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "metrics":
        # In a real system, these would be live metrics
        metrics = {"orders_today": 150, "revenue_today": 7500, "system_status": "Running" if CONFIG['running'] else 'Paused'}
        await query.edit_message_text(text=f"Live Metrics:\n{json.dumps(metrics, indent=2)}")
    elif query.data == 'pause':
        CONFIG['running'] = False
        await query.edit_message_text(text="System operations have been paused. Main loop will exit after the current cycle.")
        await notify_multi_channel("System paused by user.", priority="high")
    elif query.data == 'resume':
        if not CONFIG['running']:
            CONFIG['running'] = True
            await query.edit_message_text(text="System resumed. Main loop will restart on the next cycle.")
            # This doesn't auto-restart the main loop, it just sets the flag for the next run.
            # A more robust system would use a process manager.
            await notify_multi_channel("System resumed by user.", priority="high")
        else:
            await query.edit_message_text(text="System is already running.")
    else:
        await query.edit_message_text(text=f"Action '{query.data}' is not fully implemented in this prototype.")

# Other command handlers would go here...

async def main():
    """The main entry point for the application."""
    app = Application.builder().token(CONFIG["telegram_token"]).build()
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    # Add other handlers...

    await app.initialize()
    await app.start()

    logging.info("Flash Dispatch Engine Started.")
    await notify_multi_channel("Flash Dispatch Engine Online.", priority="high")

    # Start background tasks
    asyncio.create_task(health_check_task())
    asyncio.create_task(clean_old_logs())

    while CONFIG["running"]:
        await backup_config()
        async with ClientSession() as session:
            active_tasks = []
            module_map = {
                "dispatch": dispatch_module,
                "payout": payout_module,
                "collection": collection_module,
                "marketing": marketing_module,
            }
            for module_name in CONFIG["active_modules"]:
                if module_name in module_map:
                    active_tasks.append(module_map[module_name](session))

            await asyncio.gather(*active_tasks, return_exceptions=True)

        logging.info(f"Automation cycle completed. Waiting for 1 hour.")
        await asyncio.sleep(3600)

    logging.info("Main loop exited.")
    await notify_multi_channel("Flash Dispatch Engine Offline.", priority="high")
    await app.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Shutdown requested by user.")
