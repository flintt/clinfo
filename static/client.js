document.addEventListener("DOMContentLoaded", function () {
  const socket = io.connect('//'+ document.domain + ':' + location.port);

  const clientInfoDiv = document.getElementById("client-info");
  const history = [];

  function updateDisplay() {
      clientInfoDiv.innerHTML = history
          .map((item, index) => {
              const timeString = item.timestamp.toLocaleString();
              return `<p>${index + 1}. (${timeString}) IP Address: ${item.ip_address}, Port: ${item.port}, Delay: ${item.delay}ms</p>`;
          })
          .join("");
  }

  function sendPing() {
      const client_send_time = new Date().getTime();
      socket.sendTimestamp = client_send_time;
      socket.emit('ping_event');
  }

  socket.on('connect', () => {
      sendPing();
      socket.emit('client_connected', {data: 'Client connected!'});
  });

  socket.on("client_info", (data) => {
      const { ip_address, port } = data;
      const timestamp = new Date();

      // 将新的客户端信息和时间戳添加到历史记录数组中
      history.push({ ip_address, port, timestamp, delay: 0 });

      // 保持历史记录数组的长度为10
      if (history.length > 10) {
          history.shift();
      }

      updateDisplay();
  });

  socket.on('pong_event', (data) => {
      const client_receive_time = new Date().getTime();
      const round_trip_time = (client_receive_time - socket.sendTimestamp) ;
      // console.log("Round trip time:", round_trip_time, "seconds");

      // 更新历史记录数组中最后一项的时延
      if (history.length > 0) {
          history[history.length - 1].delay = round_trip_time;
          updateDisplay();
      }
  });

  // 每隔5秒发送一次 ping_event 以获取时延
  setInterval(sendPing, 5000);
});
