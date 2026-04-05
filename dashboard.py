#!/usr/bin/env python3
"""
WA-CPE Wi-Fi Analyzer Dashboard
Web-based dashboard for real-time Wi-Fi analysis
"""

from flask import Flask, render_template_string, jsonify, request, redirect, session
import subprocess
import threading
import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.wifi_scanner import WiFiScanner
from modules.interference_detector import InterferenceDetector
from modules.performance_tester import PerformanceTester
from modules.correlation_engine import CorrelationEngine

app = Flask(__name__)
app.secret_key = 'wa-cpe-wifi-analyzer-secret-key-2026'

USERNAME = 'admin'
PASSWORD = 'Logmein@1'

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect('/')
        else:
            return render_template_string(LOGIN_HTML, error='Invalid credentials')
    
    return render_template_string(LOGIN_HTML)

@app.route('/logout')
def logout():
    """Logout"""
    session.pop('logged_in', None)
    return redirect('/login')

def require_auth(f):
    """Decorator to require authentication"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@require_auth
def dashboard():
    """Main dashboard page"""
    return render_template_string(DASHBOARD_HTML)

latest_analysis = {
    'timestamp': None,
    'networks': [],
    'connected_devices': [],
    'searching_devices': [],
    'interference': {'level': 'N/A', 'score': 0},
    'recommendations': [],
    'channel_congestion': {}
}

analyzer_running = False
analyzer_interface = 'wlan1'

def run_analysis():
    """Run continuous analysis in background"""
    global latest_analysis, analyzer_running
    
    scanner = WiFiScanner(analyzer_interface)
    detector = InterferenceDetector()
    tester = PerformanceTester(analyzer_interface)
    correlator = CorrelationEngine()
    
    while analyzer_running:
        try:
            scan_result = scanner.scan_networks()
            networks = scan_result.get('networks', [])
            probed = scan_result.get('probed_networks', [])
            
            connected = []
            searching = []
            for item in probed:
                conn_bssid = item.get('connected_bssid', '')
                if conn_bssid and ':' in conn_bssid:
                    connected.append(item)
                else:
                    searching.append(item)
            
            interference_data = detector.analyze(networks)
            performance_data = tester.run_all_tests()
            
            correlation = correlator.correlate(
                {'networks': networks, 'network_count': len(networks)},
                performance_data,
                interference_data
            )
            
            latest_analysis = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'networks': networks,
                'connected_devices': connected,
                'searching_devices': searching,
                'interference': correlation.get('interference_impact', {}),
                'recommendations': interference_data.get('recommendations', {}),
                'channel_congestion': interference_data.get('channel_congestion', {})
            }
            
        except Exception as e:
            latest_analysis['error'] = str(e)
        
        time.sleep(10)

@app.route('/api/data')
@require_auth
def get_data():
    """API endpoint for real-time data"""
    return jsonify(latest_analysis)

@app.route('/api/networks')
@require_auth
def get_networks():
    """API endpoint for networks only"""
    return jsonify({
        'networks': latest_analysis.get('networks', []),
        'connected': latest_analysis.get('connected_devices', []),
        'searching': latest_analysis.get('searching_devices', [])
    })

@app.route('/api/interference')
@require_auth
def get_interference():
    """API endpoint for interference data"""
    return jsonify({
        'interference': latest_analysis.get('interference', {}),
        'congestion': latest_analysis.get('channel_congestion', {}),
        'recommendations': latest_analysis.get('recommendations', {})
    })

LOGIN_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WA-CPE Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .login-box {
            background: rgba(255,255,255,0.1);
            padding: 40px;
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.1);
            width: 350px;
            text-align: center;
        }
        .login-box h1 { color: #00d9ff; margin-bottom: 10px; font-size: 24px; }
        .login-box p { color: #888; margin-bottom: 30px; font-size: 14px; }
        .input-group { margin-bottom: 20px; text-align: left; }
        .input-group label { display: block; color: #888; font-size: 12px; margin-bottom: 5px; }
        .input-group input {
            width: 100%; padding: 12px;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            background: rgba(255,255,255,0.05);
            color: #fff; font-size: 14px;
        }
        .input-group input:focus { outline: none; border-color: #00d9ff; }
        .btn {
            width: 100%; padding: 12px;
            background: #00d9ff; color: #1a1a2e;
            border: none; border-radius: 8px;
            font-size: 14px; font-weight: bold; cursor: pointer;
        }
        .btn:hover { background: #00b8d9; }
        .error {
            background: rgba(255,0,0,0.2); color: #ff6666;
            padding: 10px; border-radius: 8px;
            margin-bottom: 20px; font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="login-box">
        <h1>📡 WA-CPE Wi-Fi Analyzer</h1>
        <p>Please login to access the dashboard</p>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        <form method="POST">
            <div class="input-group">
                <label>Username</label>
                <input type="text" name="username" placeholder="Enter username" required>
            </div>
            <div class="input-group">
                <label>Password</label>
                <input type="password" name="password" placeholder="Enter password" required>
            </div>
            <button type="submit" class="btn">Login</button>
        </form>
    </div>
</body>
</html>
'''

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WA-CPE Wi-Fi Analyzer Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
        }
        
        .header {
            background: rgba(0,0,0,0.3);
            padding: 20px 40px;
            border-bottom: 2px solid #0f3460;
        }
        
        .header h1 {
            color: #00d9ff;
            font-size: 28px;
        }
        
        .header .subtitle {
            color: #888;
            font-size: 14px;
            margin-top: 5px;
        }
        
        .status-bar {
            background: rgba(0,217,255,0.1);
            padding: 10px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #0f3460;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #00d9ff;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            padding: 20px 40px;
        }
        
        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .card-title {
            font-size: 18px;
            color: #00d9ff;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .card-title .icon {
            font-size: 24px;
        }
        
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .stat-box {
            background: rgba(0,217,255,0.1);
            border-radius: 10px;
            padding: 15px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: #00d9ff;
        }
        
        .stat-label {
            font-size: 12px;
            color: #888;
            margin-top: 5px;
        }
        
        .interference-gauge {
            width: 100%;
            height: 30px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            overflow: hidden;
            margin: 15px 0;
        }
        
        .interference-bar {
            height: 100%;
            border-radius: 15px;
            transition: width 0.5s ease;
        }
        
        .level-minimal { background: linear-gradient(90deg, #00ff00, #00cc00); }
        .level-low { background: linear-gradient(90deg, #88ff00, #66cc00); }
        .level-medium { background: linear-gradient(90deg, #ffcc00, #ff9900); }
        .level-high { background: linear-gradient(90deg, #ff6600, #ff3300); }
        .level-critical { background: linear-gradient(90deg, #ff0000, #cc0000); }
        
        .network-list {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .network-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            margin-bottom: 8px;
        }
        
        .network-info {
            flex: 1;
        }
        
        .network-name {
            font-weight: bold;
            margin-bottom: 4px;
        }
        
        .network-details {
            font-size: 12px;
            color: #888;
        }
        
        .network-signal {
            text-align: right;
        }
        
        .signal-strength {
            font-size: 24px;
            font-weight: bold;
        }
        
        .signal-label {
            font-size: 10px;
            color: #888;
        }
        
        .heatmap {
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
            margin-top: 15px;
        }
        
        .channel-bar {
            width: 40px;
            text-align: center;
        }
        
        .channel-number {
            font-size: 10px;
            color: #888;
            margin-bottom: 5px;
        }
        
        .channel-fill {
            background: #00d9ff;
            border-radius: 5px;
            transition: height 0.3s ease;
        }
        
        .recommendation-box {
            background: rgba(0,217,255,0.1);
            border-left: 4px solid #00d9ff;
            padding: 15px;
            border-radius: 0 10px 10px 0;
            margin-bottom: 15px;
        }
        
        .recommendation-title {
            font-weight: bold;
            color: #00d9ff;
            margin-bottom: 8px;
        }
        
        .device-list {
            max-height: 200px;
            overflow-y: auto;
        }
        
        .device-item {
            display: flex;
            justify-content: space-between;
            padding: 10px;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            margin-bottom: 8px;
        }
        
        .full-width {
            grid-column: 1 / -1;
        }
        
        .timestamp {
            color: #666;
            font-size: 12px;
        }
        
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(255,255,255,0.05);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #00d9ff;
            border-radius: 4px;
        }
        
        .loading {
            text-align: center;
            padding: 50px;
            color: #888;
        }
        
        .loading::after {
            content: '';
            animation: dots 1.5s infinite;
        }
        
        @keyframes dots {
            0%, 20% { content: '.'; }
            40% { content: '..'; }
            60%, 100% { content: '...'; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📡 WA-CPE Wi-Fi Analyzer Dashboard</h1>
        <div class="subtitle">Real-time Wi-Fi Interference Analysis</div>
    </div>
    
    <div class="status-bar">
        <div class="status-item">
            <div class="status-dot"></div>
            <span>Live Monitoring Active</span>
        </div>
        <div class="status-item">
            <span>Last Update: <span id="lastUpdate">--:--:--</span></span>
        </div>
        <div class="status-item">
            <span>Interface: wlan1</span>
        </div>
    </div>
    
    <div class="main-content">
        <div class="card full-width">
            <div class="card-title">
                <span class="icon">📊</span>
                Network Statistics
            </div>
            <div class="stat-grid">
                <div class="stat-box">
                    <div class="stat-value" id="networkCount">0</div>
                    <div class="stat-label">Networks</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value" id="connectedCount">0</div>
                    <div class="stat-label">Connected</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value" id="searchingCount">0</div>
                    <div class="stat-label">Searching</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value" id="interferenceScore">0</div>
                    <div class="stat-label">Interference</div>
                </div>
            </div>
            
            <div class="card-title">
                <span class="icon">📺</span>
                Channel Heatmap (2.4 GHz)
            </div>
            <div class="heatmap" id="heatmap"></div>
        </div>
        
        <div class="card">
            <div class="card-title">
                <span class="icon">📶</span>
                Detected Networks
            </div>
            <div class="network-list" id="networkList">
                <div class="loading">Loading data</div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-title">
                <span class="icon">💡</span>
                Recommendations
            </div>
            <div id="recommendations">
                <div class="loading">Loading recommendations</div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-title">
                <span class="icon">📱</span>
                Connected Devices
            </div>
            <div class="device-list" id="connectedList">
                <div class="loading">Loading devices</div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-title">
                <span class="icon">🔍</span>
                Devices Searching for Wi-Fi
            </div>
            <div class="device-list" id="searchingList">
                <div class="loading">Loading devices</div>
            </div>
        </div>
    </div>
    
    <script>
        function updateDashboard() {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('lastUpdate').textContent = data.timestamp || '--:--:--';
                    document.getElementById('networkCount').textContent = data.networks ? data.networks.length : 0;
                    document.getElementById('connectedCount').textContent = data.connected_devices ? data.connected_devices.length : 0;
                    document.getElementById('searchingCount').textContent = data.searching_devices ? data.searching_devices.length : 0;
                    
                    const interference = data.interference || {};
                    document.getElementById('interferenceScore').textContent = interference.score || 0;
                    
                    updateNetworkList(data.networks || []);
                    updateConnectedList(data.connected_devices || []);
                    updateSearchingList(data.searching_devices || []);
                    updateHeatmap(data.networks || []);
                    updateRecommendations(data);
                })
                .catch(error => {
                    console.error('Error fetching data:', error);
                });
        }
        
        function updateNetworkList(networks) {
            const container = document.getElementById('networkList');
            if (networks.length === 0) {
                container.innerHTML = '<div class="loading">No networks detected</div>';
                return;
            }
            
            container.innerHTML = networks.map(net => `
                <div class="network-item">
                    <div class="network-info">
                        <div class="network-name">${net.ssid || '<Hidden>'}</div>
                        <div class="network-details">${net.bssid} | Ch ${net.channel || '?'} | ${net.band || ''}</div>
                    </div>
                    <div class="network-signal">
                        <div class="signal-strength">${net.rssi || '?'}</div>
                        <div class="signal-label">dBm</div>
                    </div>
                </div>
            `).join('');
        }
        
        function updateConnectedList(devices) {
            const container = document.getElementById('connectedList');
            if (devices.length === 0) {
                container.innerHTML = '<div class="loading">No connected devices</div>';
                return;
            }
            
            container.innerHTML = devices.map(dev => `
                <div class="device-item">
                    <div>
                        <strong>${dev.manufacturer || 'Unknown'}</strong>
                        <div style="font-size:11px;color:#888">${dev.device_mac || ''}</div>
                    </div>
                    <div style="text-align:right">
                        <div>${dev.connected_bssid || ''}</div>
                        <div style="font-size:11px;color:#888">RSSI: ${dev.signal || '?'}</div>
                    </div>
                </div>
            `).join('');
        }
        
        function updateSearchingList(devices) {
            const container = document.getElementById('searchingList');
            if (devices.length === 0) {
                container.innerHTML = '<div class="loading">No searching devices</div>';
                return;
            }
            
            container.innerHTML = devices.map(dev => `
                <div class="device-item">
                    <div>
                        <strong>${dev.manufacturer || 'Unknown'}</strong>
                        <div style="font-size:11px;color:#888">${dev.device_mac || ''}</div>
                    </div>
                    <div style="text-align:right">
                        <div>${(dev.probed_ssids || []).join(', ')}</div>
                        <div style="font-size:11px;color:#888">RSSI: ${dev.signal || '?'}</div>
                    </div>
                </div>
            `).join('');
        }
        
        function updateHeatmap(networks) {
            const container = document.getElementById('heatmap');
            const channelCounts = {};
            
            for (let ch = 1; ch <= 13; ch++) {
                channelCounts[ch] = 0;
            }
            
            networks.forEach(net => {
                if (net.band && net.band.includes('2.4') && net.channel) {
                    channelCounts[net.channel] = (channelCounts[net.channel] || 0) + 1;
                }
            });
            
            let html = '';
            for (let ch = 1; ch <= 13; ch++) {
                const count = channelCounts[ch];
                const height = Math.min(count * 20, 80);
                const color = count >= 3 ? '#ff4444' : count >= 2 ? '#ffaa00' : count >= 1 ? '#00d9ff' : '#333';
                html += `
                    <div class="channel-bar">
                        <div class="channel-number">${ch}</div>
                        <div class="channel-fill" style="height:${height}px;background:${color}"></div>
                    </div>
                `;
            }
            container.innerHTML = html;
        }
        
        function updateRecommendations(data) {
            const container = document.getElementById('recommendations');
            const rec24 = data.recommendations && data.recommendations['2.4GHz'];
            const rec5 = data.recommendations && data.recommendations['5GHz'];
            
            if (!rec24 && !rec5) {
                container.innerHTML = '<div class="loading">No recommendations</div>';
                return;
            }
            
            let html = '';
            
            if (rec24 && rec24.recommended) {
                html += `
                    <div class="recommendation-box">
                        <div class="recommendation-title">📶 Switch to 2.4 GHz Channel ${rec24.recommended}</div>
                        <p>Recommended for less interference in 2.4 GHz band</p>
                    </div>
                `;
            }
            
            if (rec5 && rec5.recommended) {
                html += `
                    <div class="recommendation-box">
                        <div class="recommendation-title">🚀 Consider 5 GHz (Channel ${rec5.recommended})</div>
                        <p>5 GHz has more channels and less interference</p>
                    </div>
                `;
            }
            
            container.innerHTML = html;
        }
        
        setInterval(updateDashboard, 5000);
        updateDashboard();
    </script>
</body>
</html>
'''

def start_dashboard(interface='wlan1', host='0.0.0.0', port=5000):
    """Start the web dashboard"""
    global analyzer_interface, analyzer_running
    
    analyzer_interface = interface
    analyzer_running = True
    
    analysis_thread = threading.Thread(target=run_analysis, daemon=True)
    analysis_thread.start()
    
    print(f"Starting WA-CPE Dashboard on http://{host}:{port}")
    print("Access from any device on your network!")
    print("Press Ctrl+C to stop")
    
    app.run(host=host, port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='WA-CPE Wi-Fi Analyzer Dashboard')
    parser.add_argument('-i', '--interface', default='wlan1', help='Wi-Fi interface')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind')
    parser.add_argument('-p', '--port', type=int, default=5000, help='Port to listen')
    
    args = parser.parse_args()
    
    start_dashboard(interface=args.interface, host=args.host, port=args.port)
