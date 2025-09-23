# -*- coding: utf-8 -*-
# File: modules/monitor.py
import pandas as pd
import logging
import os
from typing import Dict, Optional
from datetime import datetime

# --- Logging Setup ---
# Logging is configured in main.py

class BotManager:
    """
    武將調度中心
    負責管理和調度所有 Telegram Bots。
    """
    def __init__(self, config_path: str = "data/bot_config.csv"):
        self.config_path = config_path
        self.bots: Dict[str, Dict] = {}
        self.load_bots()

    def load_bots(self):
        """從設定檔載入所有機器人"""
        try:
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(f"找不到武將名冊: {self.config_path}")

            df = pd.read_csv(self.config_path)
            # 將 role 作為 key，方便查找
            for _, row in df.iterrows():
                role = row['role']
                self.bots[role] = {
                    "bot_name": row['bot_name'],
                    "token": row['token']
                }
            logging.info(f"成功載入 {len(self.bots)} 位武將 (Bots)。")
            print(f"成功載入 {len(self.bots)} 位武將 (Bots)。")

        except Exception as e:
            logging.error(f"載入武將名冊失敗: {e}")
            print(f"載入武將名冊失敗: {e}")

    def get_bot_by_role(self, role: str) -> Optional[Dict]:
        """根據角色名稱取得機器人資訊"""
        return self.bots.get(role)

    async def send_notification(self, role: str, message: str, chat_id: str):
        """
        透過指定角色的機器人發送通知。
        (此為模擬，實際發送需整合 aiohttp 和 Telegram API)
        """
        bot = self.get_bot_by_role(role)
        if not bot:
            logging.error(f"找不到角色為 '{role}' 的機器人。")
            return False

        bot_name = bot['bot_name']
        # token = bot['token'] # 用於實際 API 請求

        print(f"--- 武將調度中心 ---")
        print(f"指令: 透過 {bot_name} ({role})")
        print(f"發送訊息至 Chat ID {chat_id}:")
        print(f"'{message}'")
        print(f"--------------------")

        logging.info(f"透過 {bot_name} ({role}) 發送通知: {message}")

        # 實際的 aiohttp 請求會在這裡
        # url = f"https://api.telegram.org/bot{token}/sendMessage"
        # payload = {"chat_id": chat_id, "text": message}
        # async with aiohttp.ClientSession() as session:
        #     async with session.post(url, json=payload) as response:
        #         if response.status != 200:
        #             logging.error(f"透過 {bot_name} 發送通知失敗。")
        #             return False
        return True

if __name__ == "__main__":
    # 用於獨立測試
    import asyncio
    print(f"日誌將寫入到: {log_file}")

    # 建立調度中心實例
    manager = BotManager()

    # 模擬發送通知
    async def test_send():
        if manager.bots:
            print("\n--- 測試通知功能 ---")
            await manager.send_notification(
                role="派單",
                message="新的派單任務：訂單 #12345，金額 2500元。",
                chat_id="TARGET_CHAT_ID" # 這裡應填寫目標聊天室ID
            )
            await manager.send_notification(
                role="醫療",
                message="系統健康狀態：一切正常。",
                chat_id="ADMIN_CHAT_ID"
            )
            await manager.send_notification(
                role="不存在的角色",
                message="這則訊息不該被發送。",
                chat_id="ANY_ID"
            )
        else:
            print("❌ 未載入任何機器人，無法進行測試。")

    asyncio.run(test_send())
