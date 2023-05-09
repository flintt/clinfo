document.addEventListener("DOMContentLoaded", function () {
    const socket = io.connect('//'+ document.domain + ':' + location.port);
  
    const clientInfoDiv = document.getElementById("client-info");
    const history = [];

    socket.on('connect', () => {
        socket.emit('client_connected', {data: 'Client connected!'});
    });
    socket.on("client_info", (data) => {
      const { ip_address, port } = data;
  
      // 将新的客户端信息添加到历史记录数组中
      history.push({ ip_address, port });
  
      // 保持历史记录数组的长度为10
      if (history.length > 10) {
        history.shift();
      }
  
      // 更新客户端信息的显示
      clientInfoDiv.innerHTML = history
        .map((item, index) => {
          return `<p>${index + 1}. IP Address: ${item.ip_address}, Port: ${
            item.port
          }</p>`;
        })
        .join("");
    });
  });
