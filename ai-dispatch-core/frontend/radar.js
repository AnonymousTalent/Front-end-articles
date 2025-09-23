document.addEventListener('DOMContentLoaded', function() {
    const map = document.getElementById('map');
    const statusDiv = document.getElementById('status');
    const dispatchLog = document.getElementById('dispatch-log');
    const API_URL = '/api/simulation-data'; // This endpoint will be served by our Flask app

    // 為了模擬，我們假設地圖是一個 1000x1000 的虛擬空間
    const MAP_WIDTH = 1000;
    const MAP_HEIGHT = 1000;

    function updateMap(data) {
        if (!map) return;
        map.innerHTML = ''; // 清空地圖

        // 更新訂單位置
        data.orders.forEach(order => {
            const orderEl = createMapElement('order', `O${order.id}`, order.x, order.y);
            orderEl.title = `Order ID: ${order.id}`;
            map.appendChild(orderEl);
        });

        // 更新騎手位置
        data.riders.forEach(rider => {
            const riderEl = createMapElement('rider', `R${rider.id}`, rider.x, rider.y, rider.name);
            riderEl.title = `Rider: ${rider.name} (${rider.rating}★)`;
            map.appendChild(riderEl);
        });
    }

    function createMapElement(type, id, x, y, label = '') {
        const el = document.createElement('div');
        el.className = type;

        const mapRect = map.getBoundingClientRect();
        // 將 0-100 的坐標轉換為地圖上的百分比位置
        el.style.left = `${(x / 100) * mapRect.width - 10}px`; // 減去一半寬度來置中
        el.style.top = `${(y / 100) * mapRect.height - 10}px`; // 減去一半高度來置中

        const symbol = document.createElement('span');
        symbol.textContent = type === 'order' ? 'O' : 'R';
        el.appendChild(symbol);

        if(label) {
            const nameLabel = document.createElement('div');
            nameLabel.className = 'item-label';
            nameLabel.textContent = label;
            el.appendChild(nameLabel);
        }

        return el;
    }

    function logDispatchEvent(log) {
        if (!dispatchLog) return;
        const newLogEntry = document.createElement('p');
        newLogEntry.textContent = `[${new Date().toLocaleTimeString()}] ${log}`;
        // 將新日誌添加到頂部
        if (dispatchLog.firstChild && dispatchLog.firstChild.textContent === '等待派單活動...') {
            dispatchLog.innerHTML = '';
        }
        dispatchLog.prepend(newLogEntry);
    }

    async function fetchData() {
        try {
            const response = await fetch(API_URL);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();

            statusDiv.textContent = `系統運行中 | ${data.orders.length} 筆訂單 | ${data.riders.length} 位騎手在線`;
            updateMap(data);
            if (data.latest_dispatch) {
                logDispatchEvent(data.latest_dispatch);
            }

        } catch (error) {
            console.error("無法獲取雷達數據:", error);
            statusDiv.textContent = "系統離線或發生錯誤";
        }
    }

    // 每 3 秒獲取一次新數據
    setInterval(fetchData, 3000);
    // 立即執行一次以快速載入
    fetchData();
});
