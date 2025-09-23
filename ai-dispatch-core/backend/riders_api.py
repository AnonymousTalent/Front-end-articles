import pandas as pd
import os

def get_riders(data_path="data/riders_location.csv"):
    """
    從數據源拉取騎手位置和狀態。
    在此模擬實現中，我們從 CSV 檔案讀取。
    """
    full_path = os.path.join(os.getcwd(), data_path)
    print(f"從 {full_path} 讀取騎手資料...")
    if not os.path.exists(full_path):
        print(f"錯誤：找不到騎手檔案 {full_path}")
        return pd.DataFrame()

    return pd.read_csv(full_path)

if __name__ == '__main__':
    # 用於單獨測試此模組
    riders = get_riders("../data/riders_location.csv")
    print("成功讀取騎手資料：")
    print(riders)
