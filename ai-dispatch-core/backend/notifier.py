import os

# 雖然我們 अभी तक 'python-telegram-bot' 安裝 नहीं किया है,
# 但我們可以先定義好函式結構。
# from telegram import Bot

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_dispatch_notification(order, rider):
    """
    向騎手或頻道發送派單通知。
    """
    message = f"【新的派單任務】\n訂單ID: {order['id']}\n已指派給: {rider['name']} (ID: {rider['id']})"

    # 實際的 bot.send_message 會在這裡調用
    # bot = Bot(token=TELEGRAM_TOKEN)
    # bot.send_message(chat_id=CHAT_ID, text=message)

    print("--- 通知中心 ---")
    print(f"正在向頻道 {CHAT_ID} 發送通知...")
    print(message)
    print("-----------------")
    # 為了模擬，我們只在控制台打印
    return True

if __name__ == '__main__':
    # 模擬數據
    mock_order = {'id': 'B456'}
    mock_rider = {'id': 'R07', 'name': '火箭人'}

    print("測試通知功能：")
    send_dispatch_notification(mock_order, mock_rider)
