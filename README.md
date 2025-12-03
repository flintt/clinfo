# Network Diagnostic Tool

A real-time network monitoring application built with Flask, Socket.IO, and Bootstrap 5. This tool provides instant feedback on client connection details including IP address, city (geolocation), port, and latency.

![Network Diagnostic Tool UI](https://via.placeholder.com/800x400?text=Network+Diagnostic+Tool+Screenshot)

## Features

*   **Real-time Monitoring**: Instantly detects client IP, remote port, and connection status.
*   **Latency Tracking**: continuously measures round-trip time (ping) between the client and server.
*   **Median Latency**: Calculates and displays the median latency for the current session (robust to outliers).
*   **Geolocation**: Automatically resolves the client's city based on their IP address (using ipinfo.io).
*   **Modern UI**: Clean, responsive interface built with Bootstrap 5.
*   **Connection History**: Keeps a log of recent connections with their statistics.

## Installation

1.  **Clone the repository** (if applicable) or download the source code.

2.  **Install dependencies**:
    Ensure you have Python installed, then run:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

You can configure the application using environment variables.

*   `SECRET_KEY`: (Optional) A secret key for Flask sessions. Defaults to a secure fallback if not provided.

To set it locally:
```bash
# Linux/macOS
export SECRET_KEY='your-super-secret-key'

# Windows (PowerShell)
$env:SECRET_KEY="your-super-secret-key"
```

## Running the Application

### Development
For local development and testing, you can run the Flask app directly:

```bash
python app.py
```
The application will be available at `http://localhost:12345`.

### Production (Gunicorn)
For production environments, it is recommended to use Gunicorn with an asynchronous worker class like `gevent` to support WebSocket concurrency.

1.  **Install Gevent**:
    ```bash
    pip install gevent gevent-websocket
    ```

2.  **Run with Gunicorn**:
    ```bash
    gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 -b 0.0.0.0:12345 app:app
    ```
    *   `-k geventwebsocket.gunicorn.workers.GeventWebSocketWorker`: Uses the dedicated Gevent WebSocket worker for full compatibility.
    *   `-w 1`: Uses 1 worker (recommended for Flask-SocketIO unless using a message queue).
    *   `-b 0.0.0.0:12345`: Binds to port 12345 on all interfaces.

## Project Structure

*   `app.py`: Main Flask application entry point and Socket.IO event handlers.
*   `templates/index.html`: The HTML template for the user interface.
*   `static/client.js`: Frontend logic for Socket.IO communication and DOM manipulation.
*   `requirements.txt`: Python dependencies.
