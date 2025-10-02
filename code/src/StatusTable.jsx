import React from "react";

const StatusTable = ({ data }) => {
  if (!data || data.length === 0) {
    return <div className="text-white mt-4">等待任務數據...</div>;
  }

  return (
    <div className="mt-6 w-full max-w-2xl">
      <h2 className="text-white font-bold mb-2 text-lg text-center">派單 & 任務狀態</h2>
      <table className="table-auto w-full text-white text-center">
        <thead className="bg-gray-700">
          <tr>
            <th className="px-4 py-2">模組</th>
            <th className="px-4 py-2">派單量</th>
            <th className="px-4 py-2">成功率</th>
            <th className="px-4 py-2">異常單</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr key={idx} className="bg-gray-800 border-b border-gray-700">
              <td className="px-4 py-2">{row.name}</td>
              <td className="px-4 py-2">{row.orders}</td>
              <td className="px-4 py-2 text-green-400">{row.success}%</td>
              <td className="px-4 py-2 text-red-400">{row.failed}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default StatusTable;
