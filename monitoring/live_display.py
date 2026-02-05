"""
Live Monitoring and WebSocket Display System
سیستم نظارت زنده و نمایش WebSocket

Real-time monitoring with:
- WebSocket-based live updates
- Chart.js integration for real-time graphs
- Persian language support
- Multi-session monitoring capability
"""

import os
import json
import time
import logging
import asyncio
import threading
from datetime import datetime
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum

# WebSocket and async support
import websockets
from websockets.server import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosed

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketMessageType(Enum):
    """Types of WebSocket messages"""
    METRICS_UPDATE = "metrics_update"
    SIMULATION_START = "simulation_start"
    SIMULATION_STOP = "simulation_stop"
    BOT_POWER_ADJUSTMENT = "bot_power_adjustment"
    ATTACK_EVENT = "attack_event"
    ERROR = "error"
    HEARTBEAT = "heartbeat"

@dataclass
class LiveMetrics:
    """Real-time metrics structure"""
    session_id: str
    timestamp: float
    bandwidth_gbps: float
    requests_per_second: int
    active_bots: int
    evasion_rate: float
    cpu_usage_percent: float
    memory_usage_mb: int
    attack_type: str
    ai_optimization_score: float
    persian_timestamp: str

class LiveDisplayServer:
    """
    WebSocket server for live monitoring displays
    سرور WebSocket برای نمایش‌های نظارت زنده
    """
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.connected_clients: Set[WebSocketServerProtocol] = set()
        self.active_sessions: Dict[str, LiveMetrics] = {}
        self.is_running = False
        self.server = None
        
        # Persian calendar support
        self.persian_months = [
            "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
            "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
        ]
        
        logger.info(f"سرور نمایش زنده روی {host}:{port} راه‌اندازی شد")
    
    def _convert_to_persian_date(self, timestamp: float) -> str:
        """Convert timestamp to Persian date format"""
        # Simplified Persian date conversion
        # In production, use proper Persian calendar library
        dt = datetime.fromtimestamp(timestamp)
        
        # Approximate Persian date (this is simplified)
        persian_year = dt.year - 621
        persian_month = (dt.month + 8) % 12 or 12
        persian_day = dt.day
        
        if persian_day > 30:
            persian_day = 30
            persian_month += 1
            if persian_month > 12:
                persian_month = 1
                persian_year += 1
        
        return f"{persian_year:04d}/{persian_month:02d}/{persian_day:02d} {dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"
    
    async def register_client(self, websocket: WebSocketServerProtocol, path: str):
        """Register a new WebSocket client"""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"کلاینت جدید ثبت شد: {client_id}")
        
        self.connected_clients.add(websocket)
        
        try:
            # Send initial connection message
            await self.send_to_client(websocket, {
                "type": WebSocketMessageType.HEARTBEAT.value,
                "data": {
                    "message": "اتصال به سرور نمایش زنده برقرار شد",
                    "timestamp": time.time(),
                    "persian_timestamp": self._convert_to_persian_date(time.time())
                }
            })
            
            # Keep connection alive and handle incoming messages
            async for message in websocket:
                await self.handle_client_message(websocket, message)
                
        except ConnectionClosed:
            logger.info(f"اتصال کلاینت بسته شد: {client_id}")
        except Exception as e:
            logger.error(f"خطا در مدیریت کلاینت: {e}")
        finally:
            self.connected_clients.discard(websocket)
            logger.info(f"کلاینت حذف شد: {client_id}")
    
    async def handle_client_message(self, websocket: WebSocketServerProtocol, message: str):
        """Handle incoming message from client"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "subscribe_session":
                session_id = data.get("session_id")
                if session_id and session_id in self.active_sessions:
                    # Send current session data
                    await self.send_session_data(websocket, session_id)
                    logger.info(f"کلاینت مشترک شد: {session_id}")
            
            elif message_type == "get_all_sessions":
                # Send all active sessions
                await self.send_all_sessions(websocket)
                
        except json.JSONDecodeError:
            logger.error("پیام کلاینت نامعتبر است")
        except Exception as e:
            logger.error(f"خطا در پردازش پیام کلاینت: {e}")
    
    async def send_to_client(self, websocket: WebSocketServerProtocol, data: Dict):
        """Send data to a specific client"""
        try:
            message = json.dumps(data, ensure_ascii=False, default=str)
            await websocket.send(message)
        except ConnectionClosed:
            self.connected_clients.discard(websocket)
        except Exception as e:
            logger.error(f"خطا در ارسال به کلاینت: {e}")
    
    async def broadcast_to_all_clients(self, data: Dict):
        """Broadcast data to all connected clients"""
        if not self.connected_clients:
            return
        
        # Create list of coroutines for concurrent sending
        send_tasks = []
        for websocket in list(self.connected_clients):
            send_tasks.append(self.send_to_client(websocket, data))
        
        # Send to all clients concurrently
        if send_tasks:
            await asyncio.gather(*send_tasks, return_exceptions=True)
    
    def update_session_metrics(self, session_id: str, metrics: Dict):
        """Update metrics for a session and broadcast to clients"""
        try:
            # Create LiveMetrics object
            live_metrics = LiveMetrics(
                session_id=session_id,
                timestamp=metrics.get("timestamp", time.time()),
                bandwidth_gbps=metrics.get("bandwidth_gbps", 0.0),
                requests_per_second=metrics.get("requests_per_second", 0),
                active_bots=metrics.get("active_bots", 0),
                evasion_rate=metrics.get("evasion_rate", 0.0),
                cpu_usage_percent=metrics.get("cpu_usage_percent", 0.0),
                memory_usage_mb=metrics.get("memory_usage_mb", 0),
                attack_type=metrics.get("attack_type", "unknown"),
                ai_optimization_score=metrics.get("ai_optimization_score", 0.0),
                persian_timestamp=self._convert_to_persian_date(metrics.get("timestamp", time.time()))
            )
            
            # Update active sessions
            self.active_sessions[session_id] = live_metrics
            
            # Broadcast to all clients
            asyncio.create_task(self.broadcast_to_all_clients({
                "type": WebSocketMessageType.METRICS_UPDATE.value,
                "data": asdict(live_metrics)
            }))
            
        except Exception as e:
            logger.error(f"خطا در به‌روزرسانی متریک‌ها: {e}")
    
    async def send_session_data(self, websocket: WebSocketServerProtocol, session_id: str):
        """Send current session data to a specific client"""
        if session_id in self.active_sessions:
            metrics = self.active_sessions[session_id]
            await self.send_to_client(websocket, {
                "type": WebSocketMessageType.METRICS_UPDATE.value,
                "data": asdict(metrics)
            })
    
    async def send_all_sessions(self, websocket: WebSocketServerProtocol):
        """Send data for all active sessions"""
        all_sessions = []
        for session_id, metrics in self.active_sessions.items():
            all_sessions.append(asdict(metrics))
        
        await self.send_to_client(websocket, {
            "type": "all_sessions_data",
            "data": {
                "sessions": all_sessions,
                "count": len(all_sessions),
                "timestamp": time.time()
            }
        })
    
    async def start_server(self):
        """Start the WebSocket server"""
        self.is_running = True
        logger.info(f"شروع سرور WebSocket روی {self.host}:{self.port}")
        
        try:
            self.server = await websockets.serve(
                self.register_client,
                self.host,
                self.port,
                ping_interval=30,
                ping_timeout=10
            )
            
            logger.info(f"سرور WebSocket روی ws://{self.host}:{self.port} راه‌اندازی شد")
            
            # Keep server running
            await self.server.wait_closed()
            
        except Exception as e:
            logger.error(f"خطا در راه‌اندازی سرور WebSocket: {e}")
            raise
    
    def stop_server(self):
        """Stop the WebSocket server"""
        self.is_running = False
        if self.server:
            self.server.close()
            logger.info("سرور WebSocket متوقف شد")

class LiveDisplayClient:
    """
    WebSocket client for live monitoring
    کلاینت WebSocket برای نظارت زنده
    """
    
    def __init__(self, server_url: str = "ws://localhost:8765"):
        self.server_url = server_url
        self.websocket = None
        self.is_connected = False
        self.message_handlers = {}
        
    def add_message_handler(self, message_type: str, handler):
        """Add a message handler"""
        self.message_handlers[message_type] = handler
    
    async def connect(self):
        """Connect to WebSocket server"""
        try:
            self.websocket = await websockets.connect(self.server_url)
            self.is_connected = True
            logger.info(f"متصل به سرور WebSocket: {self.server_url}")
            
            # Start receiving messages
            await self.receive_messages()
            
        except Exception as e:
            logger.error(f"خطا در اتصال به سرور WebSocket: {e}")
            self.is_connected = False
    
    async def receive_messages(self):
        """Receive and process messages from server"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                message_type = data.get("type")
                
                # Call appropriate handler
                if message_type in self.message_handlers:
                    handler = self.message_handlers[message_type]
                    await handler(data.get("data", {}))
                else:
                    logger.debug(f"پیام دریافت شد: {message_type}")
                    
        except ConnectionClosed:
            logger.info("اتصال WebSocket بسته شد")
            self.is_connected = False
        except Exception as e:
            logger.error(f"خطا در دریافت پیام‌ها: {e}")
            self.is_connected = False
    
    async def send_message(self, message_type: str, data: Dict):
        """Send message to server"""
        if not self.is_connected or not self.websocket:
            logger.warning("اتصال WebSocket برقرار نیست")
            return
        
        try:
            message = json.dumps({
                "type": message_type,
                "data": data
            }, ensure_ascii=False, default=str)
            
            await self.websocket.send(message)
            
        except Exception as e:
            logger.error(f"خطا در ارسال پیام: {e}")
    
    async def disconnect(self):
        """Disconnect from server"""
        self.is_connected = False
        if self.websocket:
            await self.websocket.close()
            logger.info("از سرور WebSocket قطع شد")

class LiveDisplayManager:
    """
    Manager for live display functionality
    مدیر عملکرد نمایش زنده
    """
    
    def __init__(self):
        self.server = LiveDisplayServer()
        self.client = None
        self.is_initialized = False
        self.update_queue = asyncio.Queue()
        self.update_task = None
        
    def initialize(self, host: str = "localhost", port: int = 8765):
        """Initialize live display system"""
        try:
            # Start WebSocket server in background thread
            server_thread = threading.Thread(target=self._run_server, args=(host, port))
            server_thread.daemon = True
            server_thread.start()
            
            # Create client for testing
            self.client = LiveDisplayClient(f"ws://{host}:{port}")
            
            self.is_initialized = True
            logger.info("سیستم نمایش زنده راه‌اندازی شد")
            
        except Exception as e:
            logger.error(f"خطا در راه‌اندازی سیستم نمایش زنده: {e}")
            raise
    
    def _run_server(self, host: str, port: int):
        """Run WebSocket server in background"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self.server.start_server())
        except Exception as e:
            logger.error(f"خطا در اجرای سرور: {e}")
    
    def update_metrics(self, session_id: str, metrics: Dict):
        """Update metrics for a session"""
        if not self.is_initialized:
            logger.warning("سیستم نمایش زنده راه‌اندازی نشده است")
            return
        
        self.server.update_session_metrics(session_id, metrics)
    
    def get_connected_clients_count(self) -> int:
        """Get number of connected clients"""
        return len(self.server.connected_clients)
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        return list(self.server.active_sessions.keys())
    
    def stop(self):
        """Stop the live display system"""
        if self.server:
            self.server.stop_server()
        
        if self.client:
            asyncio.create_task(self.client.disconnect())
        
        self.is_initialized = False
        logger.info("سیستم نمایش زنده متوقف شد")

# JavaScript/HTML for live display page
LIVE_DISPLAY_HTML = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نمایش زنده شبیه‌سازی - SecureRedLab</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/axios@1.6.0/dist/axios.min.js"></script>
    <style>
        body { font-family: 'Vazirmatn', sans-serif; }
        .metric-card { transition: all 0.3s ease; }
        .metric-card:hover { transform: translateY(-2px); }
        .live-indicator { animation: pulse 2s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
    </style>
</head>
<body class="bg-gray-900 text-white">
    <div class="container mx-auto px-4 py-6">
        <!-- Header -->
        <div class="flex justify-between items-center mb-6">
            <h1 class="text-3xl font-bold text-blue-400">
                <i class="fas fa-broadcast-tower mr-2"></i>
                نمایش زنده شبیه‌سازی
            </h1>
            <div class="flex items-center space-x-4">
                <div class="flex items-center">
                    <div class="w-3 h-3 bg-green-500 rounded-full live-indicator mr-2"></div>
                    <span class="text-sm">زنده</span>
                </div>
                <div class="text-sm text-gray-400">
                    <span id="connection-status">در حال اتصال...</span>
                </div>
            </div>
        </div>

        <!-- Session Selection -->
        <div class="bg-gray-800 rounded-lg p-4 mb-6">
            <h2 class="text-lg font-semibold mb-3">انتخاب جلسه</h2>
            <select id="session-selector" class="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600">
                <option value="">-- جلسه را انتخاب کنید --</option>
            </select>
        </div>

        <!-- Main Metrics Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div class="metric-card bg-gray-800 rounded-lg p-4 border border-gray-700">
                <div class="flex items-center justify-between mb-2">
                    <h3 class="text-sm text-gray-400">پهنای باند</h3>
                    <i class="fas fa-tachometer-alt text-blue-400"></i>
                </div>
                <div class="text-2xl font-bold text-blue-400" id="bandwidth-metric">0.0</div>
                <div class="text-xs text-gray-500">Gb/s</div>
            </div>

            <div class="metric-card bg-gray-800 rounded-lg p-4 border border-gray-700">
                <div class="flex items-center justify-between mb-2">
                    <h3 class="text-sm text-gray-400">درخواست‌ها/ثانیه</h3>
                    <i class="fas fa-bolt text-yellow-400"></i>
                </div>
                <div class="text-2xl font-bold text-yellow-400" id="rps-metric">0</div>
                <div class="text-xs text-gray-500">درخواست</div>
            </div>

            <div class="metric-card bg-gray-800 rounded-lg p-4 border border-gray-700">
                <div class="flex items-center justify-between mb-2">
                    <h3 class="text-sm text-gray-400">بات‌های فعال</h3>
                    <i class="fas fa-robot text-green-400"></i>
                </div>
                <div class="text-2xl font-bold text-green-400" id="bots-metric">0</div>
                <div class="text-xs text-gray-500">بات</div>
            </div>

            <div class="metric-card bg-gray-800 rounded-lg p-4 border border-gray-700">
                <div class="flex items-center justify-between mb-2">
                    <h3 class="text-sm text-gray-400">نرخ دور زدن</h3>
                    <i class="fas fa-shield-alt text-purple-400"></i>
                </div>
                <div class="text-2xl font-bold text-purple-400" id="evasion-metric">0%</div>
                <div class="text-xs text-gray-500">میزان موفقیت</div>
            </div>
        </div>

        <!-- Charts Section -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <div class="bg-gray-800 rounded-lg p-4">
                <h3 class="text-lg font-semibold mb-4">پهنای باند در زمان واقعی</h3>
                <canvas id="bandwidth-chart" width="400" height="200"></canvas>
            </div>

            <div class="bg-gray-800 rounded-lg p-4">
                <h3 class="text-lg font-semibold mb-4">درخواست‌ها در زمان واقعی</h3>
                <canvas id="requests-chart" width="400" height="200"></canvas>
            </div>
        </div>

        <!-- Activity Log -->
        <div class="bg-gray-800 rounded-lg p-4">
            <h3 class="text-lg font-semibold mb-4">گزارش فعالیت</h3>
            <div id="activity-log" class="space-y-2 max-h-64 overflow-y-auto">
                <div class="text-gray-500 text-sm">در انتظار فعالیت...</div>
            </div>
        </div>
    </div>

    <script src="/static/live_display.js"></script>
</body>
</html>
"""

# JavaScript for live display functionality
LIVE_DISPLAY_JS = """
// SecureRedLab Live Display JavaScript
// جاوااسکریپت نمایش زنده SecureRedLab

class LiveDisplayManager {
    constructor() {
        this.ws = null;
        this.charts = {};
        this.maxDataPoints = 50;
        this.isConnected = false;
        this.currentSession = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        
        this.initializeCharts();
        this.connect();
    }
    
    initializeCharts() {
        // Bandwidth Chart
        const bandwidthCtx = document.getElementById('bandwidth-chart').getContext('2d');
        this.charts.bandwidth = new Chart(bandwidthCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'پهنای باند (Gb/s)',
                    data: [],
                    borderColor: 'rgb(59, 130, 246)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: 'rgb(229, 231, 235)' }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: 'rgb(156, 163, 175)' },
                        grid: { color: 'rgb(55, 65, 81)' }
                    },
                    y: {
                        ticks: { color: 'rgb(156, 163, 175)' },
                        grid: { color: 'rgb(55, 65, 81)' }
                    }
                }
            }
        });
        
        // Requests Chart
        const requestsCtx = document.getElementById('requests-chart').getContext('2d');
        this.charts.requests = new Chart(requestsCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'درخواست‌ها/ثانیه',
                    data: [],
                    borderColor: 'rgb(251, 191, 36)',
                    backgroundColor: 'rgba(251, 191, 36, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: 'rgb(229, 231, 235)' }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: 'rgb(156, 163, 175)' },
                        grid: { color: 'rgb(55, 65, 81)' }
                    },
                    y: {
                        ticks: { color: 'rgb(156, 163, 175)' },
                        grid: { color: 'rgb(55, 65, 81)' }
                    }
                }
            }
        });
    }
    
    connect() {
        const wsUrl = `ws://${window.location.hostname}:8765`;
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.updateConnectionStatus('متصل', 'text-green-400');
                this.addActivityLog('به سرور نمایش زنده متصل شد', 'success');
                
                // Subscribe to all sessions
                this.sendMessage('get_all_sessions', {});
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (error) {
                    console.error('Error parsing message:', error);
                }
            };
            
            this.ws.onclose = () => {
                this.isConnected = false;
                this.updateConnectionStatus('قطع شده', 'text-red-400');
                this.addActivityLog('اتصال با سرور قطع شد', 'error');
                
                // Attempt reconnection
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    setTimeout(() => {
                        this.reconnectAttempts++;
                        this.connect();
                    }, 5000 * this.reconnectAttempts);
                }
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.addActivityLog('خطا در اتصال WebSocket', 'error');
            };
            
        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
            this.addActivityLog('ایجاد اتصال WebSocket ناموفق بود', 'error');
        }
    }
    
    handleMessage(data) {
        const { type, data: messageData } = data;
        
        switch (type) {
            case 'metrics_update':
                this.updateMetrics(messageData);
                break;
                
            case 'all_sessions_data':
                this.updateSessionSelector(messageData.sessions);
                break;
                
            case 'heartbeat':
                // Handle heartbeat
                break;
                
            default:
                console.log('Unknown message type:', type);
        }
    }
    
    updateMetrics(metrics) {
        if (this.currentSession && metrics.session_id !== this.currentSession) {
            return; // Ignore metrics for other sessions
        }
        
        // Update metric displays
        document.getElementById('bandwidth-metric').textContent = metrics.bandwidth_gbps.toFixed(1);
        document.getElementById('rps-metric').textContent = metrics.requests_per_second.toLocaleString();
        document.getElementById('bots-metric').textContent = metrics.active_bots.toLocaleString();
        document.getElementById('evasion-metric').textContent = (metrics.evasion_rate * 100).toFixed(1) + '%';
        
        // Update charts
        this.updateChart('bandwidth', 
            new Date(metrics.timestamp).toLocaleTimeString('fa-IR'),
            metrics.bandwidth_gbps
        );
        
        this.updateChart('requests',
            new Date(metrics.timestamp).toLocaleTimeString('fa-IR'),
            metrics.requests_per_second
        );
        
        // Add activity log
        this.addActivityLog(
            `متریک‌ها به‌روزرسانی شدند: پهنای باند=${metrics.bandwidth_gbps.toFixed(1)} Gb/s, بات‌ها=${metrics.active_bots}`,
            'info'
        );
    }
    
    updateChart(chartName, label, value) {
        const chart = this.charts[chartName];
        if (!chart) return;
        
        // Add new data point
        chart.data.labels.push(label);
        chart.data.datasets[0].data.push(value);
        
        // Remove old data points if exceeding limit
        if (chart.data.labels.length > this.maxDataPoints) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
        }
        
        chart.update('none');
    }
    
    updateSessionSelector(sessions) {
        const selector = document.getElementById('session-selector');
        selector.innerHTML = '<option value="">-- جلسه را انتخاب کنید --</option>';
        
        sessions.forEach(session => {
            const option = document.createElement('option');
            option.value = session.session_id;
            option.textContent = `جلسه ${session.session_id} (${session.attack_type})`;
            selector.appendChild(option);
        });
        
        // Add change listener
        selector.onchange = (e) => {
            this.currentSession = e.target.value;
            if (this.currentSession) {
                this.sendMessage('subscribe_session', { session_id: this.currentSession });
                this.addActivityLog(`مشترک جلسه ${this.currentSession} شدید`, 'info');
            }
        };
    }
    
    updateConnectionStatus(status, colorClass) {
        const statusElement = document.getElementById('connection-status');
        statusElement.textContent = status;
        statusElement.className = colorClass;
    }
    
    addActivityLog(message, type = 'info') {
        const logContainer = document.getElementById('activity-log');
        const timestamp = new Date().toLocaleTimeString('fa-IR');
        
        const logEntry = document.createElement('div');
        logEntry.className = `text-sm ${
            type === 'error' ? 'text-red-400' :
            type === 'success' ? 'text-green-400' :
            type === 'warning' ? 'text-yellow-400' :
            'text-gray-300'
        }`;
        logEntry.innerHTML = `<span class="text-gray-500">[${timestamp}]</span> ${message}`;
        
        // Add to top of log
        if (logContainer.children.length === 1 && logContainer.children[0].classList.contains('text-gray-500')) {
            logContainer.innerHTML = '';
        }
        logContainer.insertBefore(logEntry, logContainer.firstChild);
        
        // Keep only last 50 entries
        while (logContainer.children.length > 50) {
            logContainer.removeChild(logContainer.lastChild);
        }
        
        // Auto-scroll to top
        logContainer.scrollTop = 0;
    }
    
    sendMessage(type, data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type, data }));
        }
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.liveDisplay = new LiveDisplayManager();
});
"""

# Export for use in other modules
__all__ = [
    'LiveDisplayServer',
    'LiveDisplayClient',
    'LiveDisplayManager',
    'WebSocketMessageType',
    'LiveMetrics',
    'LIVE_DISPLAY_HTML',
    'LIVE_DISPLAY_JS'
]