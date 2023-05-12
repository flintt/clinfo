from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask import request
from datetime import datetime
app = Flask(__name__)

app.secret_key = 'your_secret_key'  # 请替换为您自己的密钥
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
# 用于存储客户端信息的字典
connected_clients = {}

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=12345)

@socketio.on('client_connected')
def handle_client_connected(data):
    client_ip = request.headers.get('CF-Connecting-IP', request.remote_addr)
    client_port = request.environ.get('REMOTE_PORT')
    client_sid = request.sid
    # 记录连接时间
    connect_time = datetime.now()
    
    # 将客户端信息与会话 ID 关联
    connected_clients[client_sid] = {'ip_address': client_ip, 'port': client_port, 'connect_time': connect_time}
    print(f'{datetime.now()}: Client connected: IP {client_ip}, Port {client_port}')
    # 发送客户端信息
    emit('client_info', {'ip_address': client_ip, 'port': client_port})
@socketio.on('disconnect')
def handle_disconnect():
    client_sid = request.sid
    # 通过会话 ID 获取客户端信息
    client_info = connected_clients.get(client_sid, None)
    if client_info:
        client_ip = client_info['ip_address']
        client_port = client_info['port']
        connect_time = client_info['connect_time']

        # 计算连接时长
        disconnect_time = datetime.now()
        duration = disconnect_time - connect_time
        print(f'{datetime.now()}: Client disconnected: IP {client_ip}, Port {client_port}, Connected Duration {duration}')
        # 从字典中移除断开连接的客户端
        del connected_clients[client_sid]
    else:
        print(f'{datetime.now()}: Unknown client disconnected')

@socketio.on('ping_event')
def handle_ping_event():
    emit('pong_event')
    