document.addEventListener("DOMContentLoaded", function () {
    // Connect to the Socket.IO server
    const socket = io.connect('//' + document.domain + ':' + location.port);

    // DOM Elements
    const statusBadge = document.getElementById("connection-status");
    const currentIpEl = document.getElementById("current-ip");
    const currentCityEl = document.getElementById("current-city");
    const currentPortEl = document.getElementById("current-port");
    const latencyDisplay = document.getElementById("latency-display");
    const historyTableBody = document.getElementById("history-table-body");

    // State
    const history = [];
    const cityCache = {};

    // Helper: Get City from IP (Client-side)
    async function getCity(ip_address) {
        if (cityCache[ip_address]) return cityCache[ip_address];
        try {
            const response = await fetch(`https://ipinfo.io/${ip_address}/json`);
            if (!response.ok) throw new Error("Network response was not ok");
            const data = await response.json();
            const city = data.city || 'Unknown';
            cityCache[ip_address] = city;
            return city;
        } catch (error) {
            console.error('Error fetching city information:', error);
            return 'Unknown';
        }
    }

    // Helper: Update Status Badge
    function updateStatus(connected) {
        if (connected) {
            statusBadge.textContent = "Connected";
            statusBadge.classList.replace("bg-secondary", "bg-success");
            statusBadge.classList.replace("bg-danger", "bg-success");
        } else {
            statusBadge.textContent = "Disconnected";
            statusBadge.classList.replace("bg-success", "bg-danger");
        }
    }

    // Helper: Calculate Median
    function calculateMedian(values) {
        if (values.length === 0) return 0;
        const sorted = [...values].sort((a, b) => a - b);
        const mid = Math.floor(sorted.length / 2);
        return sorted.length % 2 !== 0 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
    }

    // Helper: Render History Table
    function renderHistory() {
        historyTableBody.innerHTML = history.map((item, index) => {
            const timeString = item.timestamp.toLocaleTimeString();
            return `
                <tr>
                    <td>${index + 1}</td>
                    <td>${timeString}</td>
                    <td>${item.ip_address}</td>
                    <td>${item.city}</td>
                    <td>${item.port}</td>
                    <td>${item.medianLatency}</td>
                </tr>
            `;
        }).join("");
    }

    // --- Socket Events ---

    socket.on('connect', () => {
        console.log("Connected to server");
        updateStatus(true);
        // Reset latency display on new connection
        latencyDisplay.innerText = "-- ms";

        // Notify server
        socket.emit('client_connected', { data: 'Client connected!' });
    });

    socket.on('disconnect', () => {
        console.log("Disconnected from server");
        updateStatus(false);
    });

    socket.on('client_info', async (data) => {
        const { ip_address, port } = data;

        // Fetch city (or use cache)
        const city = await getCity(ip_address);

        // Update Current Info Card
        currentIpEl.innerText = ip_address;
        currentCityEl.innerText = city;
        currentPortEl.innerText = port;

        // Add to History
        const timestamp = new Date();
        history.push({
            ip_address,
            port,
            city,
            timestamp,
            // Track latency samples for this session
            latencies: [],
            medianLatency: '-- ms'
        });

        // Keep history manageable (last 10 entries)
        if (history.length > 10) {
            history.shift();
        }
        renderHistory();
    });

    socket.on('pong_event', (payload) => {
        if (payload && payload.timestamp) {
            const client_receive_time = new Date().getTime();
            const latency = client_receive_time - payload.timestamp;
            latencyDisplay.innerText = `${latency} ms`;

            // Update median latency for the active session (latest in history)
            if (history.length > 0) {
                const activeSession = history[history.length - 1];

                activeSession.latencies.push(latency);
                const median = Math.round(calculateMedian(activeSession.latencies));
                activeSession.medianLatency = `${median} ms`;

                renderHistory();
            }
        }
    });

    // --- Ping Loop ---

    function sendPing() {
        if (socket.connected) {
            const timestamp = new Date().getTime();
            // Send timestamp as payload
            socket.emit('ping_event', { timestamp: timestamp });
        }
    }

    // Ping every 1 second
    setInterval(sendPing, 1000);
});
