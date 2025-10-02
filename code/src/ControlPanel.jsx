import React from "react";

const ControlPanel = () => {
  const buttonStyle = "w-full text-left p-3 m-1 rounded-lg transition duration-200 ease-in-out transform hover:scale-105";

  return (
    <div>
      <h2 className="font-bold text-xl mb-4 border-b border-gray-500 pb-2">控制面板</h2>
      <button className={`${buttonStyle} bg-green-600 hover:bg-green-500`}>
        啟動防禦模組
      </button>
      <button className={`${buttonStyle} bg-red-600 hover:bg-red-500`}>
        停止防禦模組
      </button>
      <button className={`${buttonStyle} bg-blue-600 hover:bg-blue-500`}>
        派單模組操作
      </button>
      <button className={`${buttonStyle} bg-yellow-500 hover:bg-yellow-400`}>
        金流檢查
      </button>
      <button className={`${buttonStyle} bg-gray-500 hover:bg-gray-400`}>
        日誌下載
      </button>
      <button className={`${buttonStyle} bg-purple-600 hover:bg-purple-500`}>
        一鍵清空
      </button>
    </div>
  );
};

export default ControlPanel;
