import pandas as pd

def find_best_rider(order, riders_df):
    """
    根據訂單和騎手列表，找到最適合的騎手。
    演算法：(100 - 距離) + (評分 * 10)

    Args:
        order (pd.Series): 一筆訂單的資料。
        riders_df (pd.DataFrame): 所有可用的騎手。

    Returns:
        pd.Series: 最適合的騎手的資料，如果沒有可用的騎手則返回 None。
    """
    if riders_df.empty:
        return None

    # 複製一份以避免 SettingWithCopyWarning
    riders = riders_df.copy()

    # 這裡的 'distance_km' 是相對於訂單的，在真實系統中需要即時計算。
    # 在此模擬中，我們假設 'distance_km' 已經是相對於某個中心點的距離。
    # 為了模擬，我們即時計算一個分數。
    riders["score"] = riders.apply(
        lambda rider: (100 - rider["distance_km"]) + (rider["rating"] * 10),
        axis=1
    )

    # 按分數降序排序，選取最高分的騎手
    best_rider = riders.sort_values("score", ascending=False).iloc[0]

    return best_rider

if __name__ == '__main__':
    # 創建一些假數據來測試
    orders_data = {'id': ['A123'], 'store_lat': [25.047], 'store_lon': [121.531]}
    riders_data = {
        'id': ['R01', 'R02', 'R03'],
        'name': ['貓騎士', '閃電俠', '快遞員'],
        'distance_km': [2.5, 1.2, 3.8],
        'rating': [4.8, 4.9, 4.5]
    }
    order_df = pd.DataFrame(orders_data)
    riders_df = pd.DataFrame(riders_data)

    # 假設我們正在處理第一筆訂單
    current_order = order_df.iloc[0]

    best_rider = find_best_rider(current_order, riders_df)

    print(f"訂單 {current_order['id']} 的最佳騎手是：")
    print(best_rider)
