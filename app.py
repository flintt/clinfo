from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask import request
from datetime import datetime
app = Flask(__name__)

app.secret_key = 'your_secret_key'  # 请替换为您自己的密钥
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=12345)

@socketio.on('client_connected')
def handle_client_connected(data):
    client_ip = request.headers.get('CF-Connecting-IP', request.remote_addr)
    client_port = request.environ.get('REMOTE_PORT')
    emit('client_info', {'ip_address': client_ip, 'port': client_port})
    print(f'time: {datetime.now()}, ip_address: {client_ip}, port: {client_port}')
