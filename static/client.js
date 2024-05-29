// 当文档加载完毕时执行此函数
document.addEventListener("DOMContentLoaded", function () {
    // 连接到当前域名和端口上的 Socket.IO 服务器
    const socket = io.connect('//'+ document.domain + ':' + location.port);
  
    // 获取显示客户端信息的 HTML 元素
    const clientInfoDiv = document.getElementById("client-info");
    // 历史记录数组，用于存储客户端信息
    const history = [];
  
    // 更新页面显示的函数
    function updateDisplay() {
      // 更新clientInfoDiv的HTML内容
      clientInfoDiv.innerHTML = history
        .map((item, index) => {
          const timeString = item.timestamp.toLocaleString();
          return `<p>${index + 1}. (${timeString}) IP Address: ${item.ip_address}, City: ${item.city}, Port: ${item.port}, Delay: ${item.delay}ms</p>`;
        })
        .join("");
    }
  
    // 异步函数，根据IP地址获取城市信息
    async function getCity(ip_address) {
      try {
        const response = await fetch(`https://ipinfo.io/${ip_address}/json`);
        const data = await response.json();
        return data.city || 'Unknown';
      } catch (error) {
        console.error('Error fetching city information:', error);
        return 'Unknown';
      }
    }
  
    // 发送ping事件的函数
    function sendPing() {
      const client_send_time = new Date().getTime();
      socket.sendTimestamp = client_send_time;
      socket.emit('ping_event');
    }
  
    // 当与服务器连接成功时执行
    socket.on('connect', () => {
      sendPing();
      socket.emit('client_connected', {data: 'Client connected!'});
    });
  
    // 处理从服务器收到的客户端信息
    socket.on("client_info", async (data) => {
      const { ip_address, port } = data;
      const timestamp = new Date();
      const city = await getCity(ip_address);
  
      // 添加新的客户端信息到历史记录数组
      history.push({ ip_address, port, city, timestamp, delay: 0 });
  
      // 如果历史记录超过10条，移除最旧的一条
      if (history.length > 10) {
        history.shift();
      }
  
      updateDisplay();
    });
  
    // 当收到pong事件时，计算往返延迟
    socket.on('pong_event', (data) => {
      const client_receive_time = new Date().getTime();
      const round_trip_time = client_receive_time - socket.sendTimestamp;
  
      // 更新最新的历史记录条目的延迟信息
      if (history.length > 0) {
        history[history.length - 1].delay = round_trip_time;
        updateDisplay();
      }
    });
  
    // 每隔1秒发送一次ping事件以获取时延
    setInterval(sendPing, 1000);
  });
  