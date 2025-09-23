# -*- coding: utf-8 -*-
# File: modules/dispatch.py
import asyncio
import logging
import json
from datetime import datetime, time
from typing import Dict, List
from aiohttp import ClientSession, ClientError
from retry import retry
import time as perf_time

# 配置（給工程師的公開部分）
CONFIG = {
    "platforms": {
        "uber": {"api_url": "https://api.uber.com/v1/orders", "token": "ENGINEER_UBER_TOKEN", "weight": 1.2},
        "foodpanda": {"api_url": "https://api.foodpanda.com/v1/orders", "token": "ENGINEER_FOODPANDA_TOKEN", "weight": 1.0}
    },
    "log_dir": "logs/", # Corrected path
    "order_threshold": 2300.0, # 最低2300元
    "retry_attempts": 3,
    "max_concurrent_orders": 200, # 兩小時200單
}

# 日誌設置
# Logging is configured in main.py

# 檢查高峰時段
def is_peak_hour():
    current_time = datetime.now().time()
    return time(11, 0) <= current_time <= time(14, 0) or time(17, 0) <= current_time <= time(20, 0)

# 模擬你的核心算法（加密封裝，工程師無法查看）
# In the final structure, this will be imported from core_algo.py
async def predict_order_value(orders: List[Dict], region_heat: float) -> float:
    # 假設這是你的三距離算法，已加密
    prices = [o["price"] for o in orders if "price" in o]
    base_threshold = max(sum(prices) / len(prices) * 1.05, CONFIG["order_threshold"]) if prices else CONFIG["order_threshold"]
    return base_threshold * (1 + region_heat) if is_peak_hour() else base_threshold * 0.9

# 派單模組（含OpenVPN noref優化）
@retry(ClientError, tries=CONFIG["retry_attempts"], delay=2)
async def dispatch_module(session: ClientSession, notify_callback: callable) -> None:
    try:
        start_time = perf_time.perf_counter() # 開始計時（驗證OpenVPN 4%提升）
        region_heat = 0.1 # 模擬區域熱度（工程師需自行串接SerpApi）
        orders = []
        for platform, config in CONFIG["platforms"].items():
            async with session.get(config["api_url"], headers={"Authorization": f"Bearer {config['token']}"}) as resp:
                platform_orders = (await resp.json()).get("orders", [])
                for order in platform_orders:
                    order["platform"] = platform
                    order["platform_weight"] = config["weight"]
                orders.extend(platform_orders)

        threshold = await predict_order_value(orders, region_heat)
        prioritized_orders = []
        for order in orders:
            price = order.get("price", 0)
            platform = order.get("platform", "unknown")
            user_rating = order.get("user_rating", 5.0)
            distance = order.get("distance", 1.0)
            time_factor = 1.2 if is_peak_hour() else 0.8
            value_score = price * (user_rating / 5.0) / (distance + 0.1) * order["platform_weight"] * time_factor * (1 + region_heat)
            order["priority"] = "high" if value_score > 5000 else "medium" if value_score >= 2300 else "low"
            order["value_score"] = value_score
            prioritized_orders.append(order)

        prioritized_orders.sort(key=lambda o: ({"high": 3, "medium": 2, "low": 1}[o["priority"]], o["value_score"]), reverse=True)

        active_orders = 0
        for order in prioritized_orders:
            if active_orders >= CONFIG["max_concurrent_orders"]:
                logging.info("Max concurrent orders reached, skipping")
                break
            if order["value_score"] >= threshold:
                await accept_order(session, order)
                active_orders += 1
                logging.info(f"Accepted {order['priority']} priority order {order['id']} from {order['platform']} with value score {order['value_score']:.2f}")
                await notify_callback(f"{order['priority'].capitalize()} priority order {order['id']} from {order['platform']} accepted: {order['price']} TWD", priority=order["priority"])
            else:
                logging.info(f"Ignored {order['priority']} priority order {order['id']} from {order['platform']} with value score {order['value_score']:.2f}")

        end_time = perf_time.perf_counter()
        logging.info(f"Dispatch module took {end_time - start_time:.4f} seconds")
    except Exception as e:
        logging.error(f"Dispatch module failed: {str(e)}")
        await notify_callback(f"Dispatch failed: {str(e)}", priority="high")

async def accept_order(session: ClientSession, order: Dict):
    platform = order.get("platform", "unknown")
    payload = {"order_id": order["id"], "platform": platform}
    headers = {"Authorization": f"Bearer {CONFIG['platforms'][platform]['token']}"}
    async with session.post(f"{CONFIG['platforms'][platform]['api_url']}/{order['id']}/accept", json=payload, headers=headers) as resp:
        if resp.status != 200:
            raise ClientError(f"Failed to accept order {order['id']} from {platform}")

async def main_test():
    async with ClientSession() as session:
        async def notify_callback(message: str, priority: str = "normal"):
            print(f"Notification: {message}") # 工程師需自行實現Telegram/LINE通知
        await dispatch_module(session, notify_callback)

if __name__ == "__main__":
    # This block is for testing this module independently.
    print(f"日誌將寫入到: {log_file}")
    asyncio.run(main_test())
