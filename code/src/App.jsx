import React, { useEffect, useState } from "react";
import RadarChart from "./RadarChart";
import ControlPanel from "./ControlPanel";
import StatusTable from "./StatusTable";

const App = () => {
  const [aiStatus, setAiStatus] = useState([]);
  const [taskStats, setTaskStats] = useState([]);

  useEffect(() => {
    // WebSocket 模擬即時資料
    const ws = new WebSocket("ws://localhost:4000");
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setAiStatus(data.aiStatus);
      setTaskStats(data.taskStats);
    };
    return () => ws.close();
  }, []);

  return (
    <div className="flex flex-col h-screen bg-gray-900">
      {/* 頂部導航 */}
      <header className="bg-gray-800 text-white p-4 flex justify-between">
        <h1 className="font-bold text-xl">太空站 AI 指揮台</h1>
        <div className="text-lg">系統狀態監控</div>
      </header>

      <div className="flex flex-1 p-4 gap-4">
        {/* 左側雷達 */}
        <div className="w-2/3 bg-gray-800 p-4 rounded-lg shadow-lg flex flex-col items-center">
          <RadarChart data={aiStatus} />
          <StatusTable data={taskStats} />
        </div>

        {/* 右側控制面板 */}
        <div className="w-1/3 bg-gray-700 p-4 rounded-lg shadow-lg text-white">
          <ControlPanel />
        </div>
      </div>
    </div>
  );
};

export default App;
