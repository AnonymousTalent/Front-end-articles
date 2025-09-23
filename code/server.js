import { WebSocketServer } from 'ws';

const wss = new WebSocketServer({ port: 4000 });

console.log("Mock WebSocket server started on ws://localhost:4000");

const aiModules = ["雷達站", "防禦", "攻擊", "派單", "防釣魚", "核心"];
const statuses = ["ok", "warn", "error"];

const generateMockData = () => {
  const aiStatus = aiModules.map(name => ({
    name,
    status: statuses[Math.floor(Math.random() * statuses.length)],
    log: `Log entry at ${new Date().toLocaleTimeString()}`
  }));

  const taskStats = aiModules.map(name => ({
    name,
    orders: Math.floor(Math.random() * 1000),
    success: (90 + Math.random() * 10).toFixed(1),
    failed: Math.floor(Math.random() * 20),
  }));

  return { aiStatus, taskStats };
};

wss.on('connection', ws => {
  console.log('Client connected');

  const interval = setInterval(() => {
    ws.send(JSON.stringify(generateMockData()));
  }, 2000);

  ws.on('close', () => {
    console.log('Client disconnected');
    clearInterval(interval);
  });
});
