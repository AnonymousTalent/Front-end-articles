import os
import time
import threading
import pandas as pd
from flask import Flask, jsonify, send_from_directory
from dotenv import load_dotenv

# 導入後端模組
from backend import orders_api, riders_api, dispatch_logic, notifier, storage

# --- 全局設定與狀態管理 ---

# 載入 .env 檔案
load_dotenv(dotenv_path='config/settings.env')

# 建立 Flask App
app = Flask(__name__, static_folder='frontend')

# 模擬的共享狀態
# 在真實應用中，這會由資料庫或快取系統管理
simulation_state = {
    "orders": pd.DataFrame(),
    "riders": pd.DataFrame(),
    "latest_dispatch": None,
}
state_lock = threading.Lock()

# --- 派單模擬核心邏輯 ---

def run_dispatch_simulation():
    """在背景執行緒中運行的派單模擬器"""
    print("🚀 AI 派單模擬器啟動...")

    # 初始載入數據
    initial_orders = orders_api.get_orders('data/orders_today.csv')
    initial_riders = riders_api.get_riders('data/riders_location.csv')

    with state_lock:
        simulation_state["orders"] = initial_orders
        simulation_state["riders"] = initial_riders

    while True:
        time.sleep(5) # 每 5 秒嘗試派一次單

        with state_lock:
            # 如果沒有訂單，就重置訂單列表以持續模擬
            if simulation_state["orders"].empty:
                print("所有訂單已派發完畢，重新載入訂單以繼續模擬...")
                simulation_state["orders"] = orders_api.get_orders('data/orders_today.csv')
                simulation_state["latest_dispatch"] = "所有訂單已派發完畢，循環重新開始。"

            # 取得佇列中的第一筆訂單
            order_to_dispatch = simulation_state["orders"].iloc[0]
            riders_available = simulation_state["riders"]

        print(f"\nProcessing order: {order_to_dispatch['id']}")

        # 尋找最佳騎手
        best_rider = dispatch_logic.find_best_rider(order_to_dispatch, riders_available)

        if best_rider is not None:
            print(f"找到最佳騎手: {best_rider['name']}")
            # 模擬通知與儲存
            notifier.send_dispatch_notification(order_to_dispatch, best_rider)
            storage.record_dispatch(order_to_dispatch, best_rider)

            # 更新狀態
            with state_lock:
                # 從訂單列表中移除已派發的訂單
                simulation_state["orders"] = simulation_state["orders"].iloc[1:]
                # 更新前端顯示的最新派單訊息
                dispatch_message = f"訂單 {order_to_dispatch['id']} 已成功指派給 {best_rider['name']}"
                simulation_state["latest_dispatch"] = dispatch_message
        else:
            print("目前沒有可用的騎手。")
            with state_lock:
                simulation_state["latest_dispatch"] = f"訂單 {order_to_dispatch['id']} 無法找到合適的騎手。"


# --- Flask Web 伺服器 ---

@app.route('/')
def serve_radar_map():
    """提供前端雷達地圖頁面"""
    return send_from_directory('frontend', 'radar_map.html')

@app.route('/<path:path>')
def serve_static_files(path):
    """提供 CSS 和 JS 等靜態檔案"""
    return send_from_directory('frontend', path)

@app.route('/api/simulation-data')
def get_simulation_data():
    """提供給前端的 API，返回當前模擬狀態"""
    with state_lock:
        # 轉換為可序列化的 JSON 格式
        orders_json = simulation_state["orders"].to_dict(orient='records')
        riders_json = simulation_state["riders"].to_dict(orient='records')

        response = {
            "orders": orders_json,
            "riders": riders_json,
            "latest_dispatch": simulation_state["latest_dispatch"]
        }
    return jsonify(response)

if __name__ == '__main__':
    # 在背景啟動模擬器
    simulation_thread = threading.Thread(target=run_dispatch_simulation, daemon=True)
    simulation_thread.start()

    # 啟動 Web 伺服器
    # host='0.0.0.0' 讓它可以從外部訪問
    print("🌍 啟動前端 Web 伺服器於 http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
