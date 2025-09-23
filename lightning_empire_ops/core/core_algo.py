# -*- coding: utf-8 -*-
# File: core/core_algo.py

import json
import logging
from cryptography.fernet import Fernet
from typing import List, Dict, Optional

# --- Logging Setup ---
# Logging is configured in main.py
from datetime import datetime

def load_key(key_path: str = "secret.key") -> Optional[bytes]:
    """從檔案載入密鑰"""
    import os
    abs_path = os.path.abspath(key_path)
    logging.info(f"Attempting to open key at: {abs_path}")
    print(f"Attempting to open key at: {abs_path}")
    try:
        with open(key_path, "rb") as key_file:
            key = key_file.read()
        return key
    except FileNotFoundError:
        logging.error(f"密鑰檔案找不到: {key_path}")
        return None

class EncryptedAlgorithm:
    """
    一個加密的演算法執行器。
    它需要一個密鑰來初始化，沒有密鑰就無法執行核心邏輯。
    """
    def __init__(self, key: bytes):
        self.fernet = Fernet(key)

    def _three_distance_algorithm(self, orders: List[Dict], region_heat: float) -> Dict:
        """
        這就是您機密的「三距離派單算法」的實際邏輯。
        在我們的設計中，這個函式被保護起來，外部無法直接調用。
        """
        # --- 這是演算法的模擬實現 ---
        # 實際邏輯會比這複雜得多
        prices = [o.get("price", 0) for o in orders]
        if not prices:
            return {"predicted_threshold": 2300.0, "reason": "No prices found, default threshold"}

        avg_price = sum(prices) / len(prices)
        # 模擬基於熱度和尖峰時段的動態閾值
        base_threshold = max(avg_price * 1.05, 2300.0)
        final_threshold = base_threshold * (1 + region_heat) # 假設總是尖峰

        return {
            "predicted_threshold": round(final_threshold, 2),
            "algorithm_version": "3.0-encrypted",
            "base_avg_price": round(avg_price, 2)
        }
        # --- 演算法模擬結束 ---

    def run_encrypted_prediction(self, orders: List[Dict], region_heat: float) -> Optional[Dict]:
        """
        執行加密的預測流程。
        它在內部調用核心算法，然後加密結果。
        在真實場景中，它會解密並執行一個預編譯的 .pyc 或 C 模組。
        為了模擬，我們只加密/解密輸出。
        """
        try:
            # 1. 執行核心算法
            result_data = self._three_distance_algorithm(orders, region_heat)
            result_json = json.dumps(result_data).encode('utf-8')

            # 2. 加密輸出 (模擬保護)
            encrypted_result = self.fernet.encrypt(result_json)

            # 3. 解密輸出 (模擬執行時的解鎖)
            decrypted_json = self.fernet.decrypt(encrypted_result)
            final_result = json.loads(decrypted_json.decode('utf-8'))

            logging.info(f"成功執行加密演算法，預測閾值為: {final_result['predicted_threshold']}")
            return final_result

        except Exception as e:
            logging.error(f"加密演算法執行失敗: {e}")
            return None

# --- Factory Function ---
def get_algorithm_executor() -> Optional[EncryptedAlgorithm]:
    """
    工廠函式：載入密鑰並返回一個可用的演算法執行器實例。
    這是給外部模組 (如 dispatch.py) 使用的主要入口。
    """
    key = load_key("core/secret.key") # Adjusted path for main.py
    if key:
        return EncryptedAlgorithm(key)
    return None

if __name__ == "__main__":
    # 用於獨立測試
    import os
    print(f"日誌將寫入到: {log_file}")

    # 測試時，我們假設 key 在當前目錄
    if not os.path.exists("secret.key"):
        print("未找到 secret.key，正在生成一個用於測試...")
        test_key = Fernet.generate_key()
        with open("secret.key", "wb") as f:
            f.write(test_key)

    key = load_key()
    if key:
        executor = EncryptedAlgorithm(key)

        # 模擬訂單數據
        mock_orders = [{"price": 300}, {"price": 500}]
        mock_heat = 0.2

        print("\n正在執行加密預測...")
        result = executor.run_encrypted_prediction(mock_orders, mock_heat)

        if result:
            print("✅ 成功執行並解密結果:")
            print(json.dumps(result, indent=4))
        else:
            print("❌ 執行失敗。")

        # 清理測試密鑰
        if os.path.exists("secret.key"):
            os.remove("secret.key")
    else:
        print("❌ 無法載入密鑰，測試中止。")
