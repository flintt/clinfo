import os
import logging
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Use environment variable for secret key with a default fallback
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key!ChangeMe')

# Explicitly set async_mode to 'gevent' to ensure compatibility with Gunicorn gevent worker
# even if eventlet is installed in the environment.
socketio = SocketIO(app, async_mode='gevent')

# Store connected clients (In-memory storage)
connected_clients = {}

def get_client_ip():
    """
    Helper to get the real client IP address, handling proxies.
    """
    if request.headers.get('CF-Connecting-IP'):
        return request.headers.get('CF-Connecting-IP')
    if request.headers.get('X-Forwarded-For'):
        # X-Forwarded-For can be a comma-separated list
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('client_connected')
def handle_client_connected(data):
    client_ip = get_client_ip()
    client_port = request.environ.get('REMOTE_PORT')
    client_sid = request.sid
    connect_time = datetime.now()
    
    connected_clients[client_sid] = {
        'ip_address': client_ip,
        'port': client_port,
        'connect_time': connect_time
    }

    logger.info(f'Client connected: IP {client_ip}, Port {client_port}, SID {client_sid}')

    # Send client info back to the connecting client
    emit('client_info', {'ip_address': client_ip, 'port': client_port})

@socketio.on('disconnect')
def handle_disconnect():
    client_sid = request.sid
    client_info = connected_clients.pop(client_sid, None)

    if client_info:
        duration = datetime.now() - client_info['connect_time']
        logger.info(f"Client disconnected: IP {client_info['ip_address']}, Duration {duration}")
    else:
        logger.warning(f"Unknown client disconnected: SID {client_sid}")

@socketio.on('ping_event')
def handle_ping_event(data=None):
    """
    Handle ping event.
    Echoes back the data (timestamp) to allow client to calculate latency.
    """
    emit('pong_event', data)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=12345, allow_unsafe_werkzeug=True)
