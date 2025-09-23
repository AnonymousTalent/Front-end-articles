#!/bin/bash
#
# 一鍵安裝腳本 for 閃電帝國行動
# This script sets up the environment for the project.

echo "🚀 開始設定「閃電帝國行動」的執行環境..."

# 確保我們在腳本所在的目錄下執行
cd "$(dirname "$0")"

# 步驟 1: 建立 Python 虛擬環境 (推薦)
if [ ! -d "venv" ]; then
    echo "🐍 正在建立 Python 虛擬環境..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ 建立虛擬環境失敗。請確認您已安裝 python3 和 venv 套件。"
        exit 1
    fi
fi

# 啟用虛擬環境
source venv/bin/activate

# 步驟 2: 建立 requirements.txt
echo "📝 正在建立相依套件列表 (aiohttp, retry, cryptography)..."
cat > requirements.txt << EOL
aiohttp
retry
cryptography
EOL

# 步驟 3: 安裝相依套件
echo "📦 正在使用 pip 安裝相依套件..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ 安裝相依套件失敗。請檢查您的網路連線和 pip 設定。"
    exit 1
fi

echo "✅ 環境設定完成！您現在可以啟用虛擬環境 (source venv/bin/activate) 並執行主程式。"
exit 0
