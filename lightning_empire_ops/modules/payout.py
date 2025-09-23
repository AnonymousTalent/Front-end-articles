# -*- coding: utf-8 -*-
# File: modules/payout.py
import json
import logging
from datetime import datetime
import os

# --- Configuration ---
# In a real system, this would be more dynamic
PAYOUT_CONFIG = {
    "report_dir": "reports/",
    "bank_details": {
        "bank_code": "822", # 中國信託
        "account_number": "484540302460"
    },
    "tax_rate": 0.1, # 假設稅率
}

# --- Logging Setup ---
# Logging is configured in main.py

def create_payout_record(order_id: str, amount: float, description: str = ""):
    """
    生成金流工單 (Payout Record) 並存為 JSON 檔案。
    這只生成記錄，不執行實際轉帳，以策安全。
    """
    try:
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("無效的金額")

        timestamp = datetime.now()
        record_id = f"PAYOUT-{timestamp.strftime('%Y%m%d-%H%M%S')}-{order_id}"

        tax = amount * PAYOUT_CONFIG["tax_rate"]
        net_amount = amount - tax

        payout_record = {
            "record_id": record_id,
            "order_id": order_id,
            "gross_amount": amount,
            "tax": round(tax, 2),
            "net_amount": round(net_amount, 2),
            "payout_account_code": PAYOUT_CONFIG["bank_details"]["bank_code"],
            "payout_account_number": PAYOUT_CONFIG["bank_details"]["account_number"],
            "status": "PENDING_TRANSFER", # 狀態：等待手動轉帳
            "description": description,
            "created_at": timestamp.isoformat()
        }

        # 確保報告目錄存在
        report_dir = PAYOUT_CONFIG['report_dir']
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)

        # 保存工單
        record_filepath = os.path.join(report_dir, f"{record_id}.json")
        with open(record_filepath, 'w', encoding='utf-8') as f:
            json.dump(payout_record, f, indent=4, ensure_ascii=False)

        logging.info(f"成功創建金流工單: {record_id} for order {order_id}")
        return payout_record

    except Exception as e:
        logging.error(f"創建金流工單失敗 for order {order_id}: {e}")
        return None

if __name__ == "__main__":
    # 用於獨立測試
    print(f"日誌將寫入到: {log_file}")
    print("正在測試創建金流工單...")

    # 模擬一筆訂單資訊
    test_order_id = "UBER-ABC-123"
    test_amount = 5678.0

    record = create_payout_record(test_order_id, test_amount, "測試訂單")

    if record:
        print("✅ 成功創建工單:")
        print(json.dumps(record, indent=4, ensure_ascii=False))
    else:
        print("❌ 創建工單失敗，請檢查日誌。")
