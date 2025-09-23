# -*- coding: utf-8 -*-
# File: main.py
import asyncio
import argparse
import logging
from datetime import datetime
from aiohttp import ClientSession

# 導入帝國的各大模組
from modules import dispatch, payout, monitor
from core.core_algo import get_algorithm_executor

import os
from cryptography.fernet import Fernet

def ensure_secret_key_exists(path="core/secret.key"):
    """Ensures the secret key file exists, creating it if necessary."""
    if not os.path.exists(path):
        print(f"Secret key not found at {path}. Generating a new one.")
        logging.warning(f"Secret key not found at {path}. Generating a new one.")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        key = Fernet.generate_key()
        with open(path, "wb") as key_file:
            key_file.write(key)

# --- 全局日誌設定 ---
# 確保日誌目錄存在
os.makedirs('logs', exist_ok=True)
log_file = f"logs/main_log_{datetime.now().strftime('%Y%m%d')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(module)s] - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler() # 同時輸出到控制台
    ]
)

class LightningEmpire:
    """
    閃電帝國總控制器
    """
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        logging.info("Initializing Bot Manager...")
        self.bot_manager = monitor.BotManager(config_path="data/bot_config.csv")
        logging.info("Bot Manager initialized.")

        logging.info("Initializing Algorithm Executor...")
        self.algorithm_executor = get_algorithm_executor()
        logging.info("Algorithm Executor initialized.")

        if self.dry_run:
            logging.warning("🔥 系統處於【試運行 Dry Run】模式，將不會執行真實交易或派單。🔥")

    async def notify_callback(self, message: str, priority: str = "normal"):
        """
        通知回調函式，用於將訊息透過指定的機器人發送出去。
        """
        # 根據優先級選擇不同的機器人
        role = "派單" # 預設
        if priority == "high":
            role = "安全總管"
        elif priority == "low":
            role = "偵察"

        # chat_id 應從設定檔或動態取得，此處為範例
        target_chat_id = "GENERAL_CHANNEL_ID"

        if not self.dry_run:
            await self.bot_manager.send_notification(role, message, target_chat_id)
        else:
            logging.info(f"[Dry Run] 模擬通知 -> Role: {role}, Message: {message}")

    async def order_accepted_callback(self, order: dict):
        """
        訂單成功接受後的回調函式，用於觸發金流模組。
        """
        logging.info(f"訂單 {order.get('id')} 已成功派發，準備生成金流工單...")
        if not self.dry_run:
            payout.create_payout_record(
                order_id=order.get('id', 'UNKNOWN'),
                amount=order.get('price', 0.0),
                description=f"Payout for {order.get('platform')} order."
            )
        else:
            logging.info(f"[Dry Run] 模擬生成金流工單 -> Order ID: {order.get('id')}, Amount: {order.get('price')}")

    async def run_empire(self):
        """
        帝國主循環
        """
        if not self.algorithm_executor:
            logging.error("❌ 無法初始化核心演算法，系統中止。")
            return

        # Monkey-patch the dispatch module to use our callbacks and protected algorithm
        # This is a way to inject dependencies without changing the engineer's code
        dispatch.predict_order_value = self.algorithm_executor.run_encrypted_prediction

        original_accept_order = dispatch.accept_order
        async def patched_accept_order(session, order):
            if not self.dry_run:
                await original_accept_order(session, order)
            else:
                logging.info(f"[Dry Run] 模擬接受訂單 -> Order ID: {order.get('id')}")
            # No matter dry_run or not, we trigger the payout logic
            await self.order_accepted_callback(order)

        dispatch.accept_order = patched_accept_order


        async with ClientSession() as session:
            while True:
                logging.info("--- 帝國開始新一輪派單循環 ---")
                try:
                    await dispatch.dispatch_module(session, self.notify_callback)
                except Exception as e:
                    logging.error(f"派單循環出錯: {e}")
                    await self.notify_callback(f"派單主循環發生嚴重錯誤: {e}", priority="high")

                logging.info("--- 本輪循環結束，休眠 2 小時 ---")
                await asyncio.sleep(7200) # 2 hours

if __name__ == "__main__":
    # Ensure all necessary files and directories are in place before running
    ensure_secret_key_exists()

    parser = argparse.ArgumentParser(description="閃電帝國行動總控制器")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="啟用試運行模式，不會執行真實交易。"
    )
    args = parser.parse_args()

    # 建立帝國實例
    empire = LightningEmpire(dry_run=args.dry_run)

    # 啟動帝國
    try:
        asyncio.run(empire.run_empire())
    except KeyboardInterrupt:
        logging.info("皇帝已下令，系統正在關閉...")
    except Exception as e:
        logging.critical(f"帝國系統發生致命錯誤: {e}")
