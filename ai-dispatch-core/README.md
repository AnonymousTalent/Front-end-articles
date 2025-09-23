# AI Dispatch Core 😼⚡

**AI 派單核心系統** 是一個完整的後端自動化 + 前端雷達模擬的 AI 派單系統。此系統專為內部使用而設計，確保所有操作和數據都在完全掌控之下。

## 系統架構

本專案採用前後端分離的模擬架構：

-   **後端 (`main.py` + `backend/`)**: 一個基於 Python 的模擬器，它會：
    1.  從 CSV 檔案讀取訂單和騎手數據。
    2.  根據派單演算法 (`dispatch_logic.py`) 將訂單分配給最佳騎手。
    3.  透過控制台模擬發送通知 (`notifier.py`) 和記錄結果 (`storage.py`)。
    4.  運行一個無限循環的線程來持續處理訂單。

-   **前端 (`frontend/`)**: 一個基於 HTML/JS/CSS 的雷達介面，它會：
    1.  從後端的 API 端點 (`/api/simulation-data`) 定期獲取數據。
    2.  在一個模擬地圖上即時視覺化訂單和騎手的位置。
    3.  顯示最新的派單日誌。

-   **設定 (`config/`)**: 存放環境變數，例如 API Token。

## 目錄結構

```
ai-dispatch-core/
│── backend/
│   ├── orders_api.py        # 拉取訂單
│   ├── riders_api.py        # 拉取騎手位置
│   ├── dispatch_logic.py    # 派單演算法
│   ├── notifier.py          # 發送通知
│   └── storage.py           # 記錄結果
│
│── frontend/
│   ├── radar_map.html       # 前端雷達視覺化
│   ├── radar.js             # 前端邏輯
│   └── style.css            # 樣式表
│
│── config/
│   ├── settings.env         # API Key, Token 等設定
│
│── data/
│   ├── orders_today.csv     # 模擬訂單數據
│   └── riders_location.csv  # 模擬騎手數據
│
│── main.py                  # 核心應用程式：整合後端與啟動伺服器
│── requirements.txt         # Python 相依套件
└── README.md                # 本說明檔案
```

## 系統設定與運行

**1. 安裝相依套件**

首先，請確保您已安裝 Python 3.8+。然後在終端機中運行以下指令來安裝所有必要的套件：

```bash
pip install -r requirements.txt
```

**2. 設定環境變數**

複製或重命名 `config/settings.env` 檔案。根據您的需求填寫裡面的值，例如 Telegram Bot 的 Token。

```env
# config/settings.env

TELEGRAM_TOKEN="你的BotToken"
CHAT_ID="騎手群ID"
```

**3. 運行系統**

一切準備就緒後，在專案根目錄 (`ai-dispatch-core/`) 下運行 `main.py`：

```bash
python main.py
```

您應該會看到類似以下的輸出：

```
🚀 AI 派單模擬器啟動...
🌍 啟動前端 Web 伺服器於 http://127.0.0.1:5000
```

**4. 打開雷達介面**

打開您的瀏覽器，訪問 [http://127.0.0.1:5000](http://127.0.0.1:5000)。您將會看到即時的雷達地圖，後端模擬器會自動在背景進行派單，並將結果顯示在前端介面上。

## 私人庫防禦工事 (Security Best Practices)

此專案設計為私人庫，為確保程式碼與數據安全，請遵循以下最佳實踐：

1.  **保持儲存庫私有**: 確保此 GitHub 儲存庫設定為 `Private`。
2.  **禁止 Forking**: 在儲存庫的設定中，取消勾選 `Allow forking`，防止程式碼被複製到外部。
3.  **保護主分支**: 設定分支保護規則 (Branch Protection Rules) 來保護 `main` 或 `master` 分支，例如要求 Code Review 才能合併。
4.  **管理存取權限**: 僅將權限授予絕對需要的開發人員，並使用最小權限原則。
5.  **使用 `.gitignore`**: 確保敏感檔案（如 `config/settings.env`，`*.pyc`，以及其他本地設定檔）被添加到 `.gitignore` 中，避免它們被意外提交。
6.  **(可選) Commit 簽章**: 啟用 GPG Commit 簽章驗證，確保所有提交都來自可信的來源。
7.  **(可選) Webhook 監控**: 設定 Webhook 來監控儲存庫的異常活動，並將通知發送到指定的監控頻道。
