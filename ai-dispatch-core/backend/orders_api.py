import pandas as pd
import os

def get_orders(data_path="data/orders_today.csv"):
    """
    從數據源拉取訂單。
    在此模擬實現中，我們從 CSV 檔案讀取訂單。
    """
    full_path = os.path.join(os.getcwd(), data_path)
    print(f"從 {full_path} 讀取訂單...")
    if not os.path.exists(full_path):
        print(f"錯誤：找不到訂單檔案 {full_path}")
        return pd.DataFrame()

    return pd.read_csv(full_path)

if __name__ == '__main__':
    # 用於單獨測試此模組
    # 為了讓這個測試能獨立運作，我們需要調整一下路徑
    # 假設我們在 ai-dispatch-core 目錄下執行 python -m backend.orders_api
    orders = get_orders("../data/orders_today.csv")
    print("成功讀取訂單：")
    print(orders)
