#!/usr/bin/env python3
"""
WA-CPE Wi-Fi Analyzer Dashboard
Web-based dashboard for real-time Wi-Fi analysis
"""

from flask import Flask, render_template_string, jsonify, request, redirect, session, Response
import subprocess
import threading
import time
import os
import sys
import csv
import io
from datetime import datetime

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
analyzer_paused = False
analyzer_interface = 'wlan1'

def run_analysis():
    """Run continuous analysis in background"""
    global latest_analysis, analyzer_running, analyzer_paused
    
    scanner = WiFiScanner(analyzer_interface)
    detector = InterferenceDetector()
    tester = PerformanceTester(analyzer_interface)
    correlator = CorrelationEngine()
    
    while analyzer_running:
        try:
            if not analyzer_paused:
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
                    'channel_congestion': interference_data.get('channel_congestion', {}),
                    'paused': False
                }
            else:
                latest_analysis['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
                latest_analysis['paused'] = True
                
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

@app.route('/api/pause', methods=['POST'])
@require_auth
def pause_monitoring():
    """Pause live monitoring"""
    global analyzer_paused
    analyzer_paused = True
    return jsonify({'status': 'paused', 'message': 'Monitoring paused'})

@app.route('/api/resume', methods=['POST'])
@require_auth
def resume_monitoring():
    """Resume live monitoring"""
    global analyzer_paused
    analyzer_paused = False
    return jsonify({'status': 'running', 'message': 'Monitoring resumed'})

@app.route('/api/status')
@require_auth
def get_status():
    """Get monitoring status"""
    return jsonify({
        'running': analyzer_running,
        'paused': analyzer_paused
    })

@app.route('/api/export/csv')
@require_auth
def export_csv():
    """Export data as CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Wi-Fi Analyzer Export - ' + (latest_analysis.get('timestamp') or datetime.now().strftime('%Y-%m-%d %H:%M:%S'))])
    writer.writerow([])
    
    writer.writerow(['=== NETWORKS ==='])
    writer.writerow(['SSID', 'BSSID', 'Channel', 'Band', 'RSSI (dBm)', 'Encryption'])
    for net in latest_analysis.get('networks', []):
        writer.writerow([
            net.get('ssid', 'Hidden'),
            net.get('bssid', ''),
            net.get('channel', ''),
            net.get('band', ''),
            net.get('rssi', ''),
            net.get('encryption', '')
        ])
    
    writer.writerow([])
    writer.writerow(['=== CONNECTED DEVICES ==='])
    writer.writerow(['MAC Address', 'Manufacturer', 'Connected BSSID', 'Signal (dBm)', 'Probed SSIDs'])
    for dev in latest_analysis.get('connected_devices', []):
        writer.writerow([
            dev.get('device_mac', ''),
            dev.get('manufacturer', ''),
            dev.get('connected_bssid', ''),
            dev.get('signal', ''),
            ', '.join(dev.get('probed_ssids', []))
        ])
    
    writer.writerow([])
    writer.writerow(['=== SEARCHING DEVICES ==='])
    writer.writerow(['MAC Address', 'Manufacturer', 'Signal (dBm)', 'Probed SSIDs'])
    for dev in latest_analysis.get('searching_devices', []):
        writer.writerow([
            dev.get('device_mac', ''),
            dev.get('manufacturer', ''),
            dev.get('signal', ''),
            ', '.join(dev.get('probed_ssids', []))
        ])
    
    writer.writerow([])
    writer.writerow(['=== INTERFERENCE DATA ==='])
    interf = latest_analysis.get('interference', {})
    writer.writerow(['Level', 'Score'])
    writer.writerow([interf.get('level', 'N/A'), interf.get('score', 0)])
    
    writer.writerow([])
    writer.writerow(['=== CHANNEL CONGESTION (2.4 GHz) ==='])
    writer.writerow(['Channel', 'Network Count', 'Congestion Level'])
    for ch, data in latest_analysis.get('channel_congestion', {}).items():
        if isinstance(data, dict):
            writer.writerow([ch, data.get('network_count', 0), data.get('congestion_level', 'N/A')])
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=wifi_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
    )

@app.route('/api/export/html')
@require_auth
def export_html():
    """Export data as HTML report"""
    timestamp = latest_analysis.get('timestamp') or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    interf = latest_analysis.get('interference', {})
    
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wi-Fi Analysis Report - {timestamp}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #00d9ff; border-bottom: 2px solid #0f3460; padding-bottom: 10px; }}
        h2 {{ color: #0f3460; margin-top: 30px; }}
        .timestamp {{ color: #888; font-size: 14px; margin-bottom: 20px; }}
        .stat-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0; }}
        .stat-box {{ background: #f0f9ff; padding: 20px; border-radius: 10px; text-align: center; }}
        .stat-value {{ font-size: 28px; font-weight: bold; color: #00d9ff; }}
        .stat-label {{ font-size: 12px; color: #666; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th {{ background: #0f3460; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #eee; }}
        tr:hover {{ background: #f5f5f5; }}
        .interference-bar {{ height: 30px; border-radius: 15px; margin: 15px 0; }}
        .level-minimal {{ background: linear-gradient(90deg, #00ff00, #00cc00); }}
        .level-low {{ background: linear-gradient(90deg, #88ff00, #66cc00); }}
        .level-medium {{ background: linear-gradient(90deg, #ffcc00, #ff9900); }}
        .level-high {{ background: linear-gradient(90deg, #ff6600, #ff3300); }}
        .level-critical {{ background: linear-gradient(90deg, #ff0000, #cc0000); }}
        .level-minimal-bg {{ background: #d4edda; }}
        .level-low-bg {{ background: #c3e6cb; }}
        .level-medium-bg {{ background: #fff3cd; }}
        .level-high-bg {{ background: #ffe5d0; }}
        .level-critical-bg {{ background: #f8d7da; }}
        .recommendation {{ background: #e7f3ff; border-left: 4px solid #00d9ff; padding: 15px; margin: 10px 0; border-radius: 0 5px 5px 0; }}
        .footer {{ margin-top: 30px; text-align: center; color: #888; font-size: 12px; }}
        @media print {{ body {{ background: white; }} .container {{ box-shadow: none; }} }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Wi-Fi Analysis Report</h1>
        <p class="timestamp">Generated: {timestamp}</p>
        
        <div class="stat-grid">
            <div class="stat-box">
                <div class="stat-value">{len(latest_analysis.get('networks', []))}</div>
                <div class="stat-label">Networks</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{len(latest_analysis.get('connected_devices', []))}</div>
                <div class="stat-label">Connected Devices</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{len(latest_analysis.get('searching_devices', []))}</div>
                <div class="stat-label">Searching Devices</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{interf.get('score', 0)}</div>
                <div class="stat-label">Interference Score</div>
            </div>
        </div>
        
        <h2>Interference Level: {interf.get('level', 'N/A')}</h2>
        <div class="interference-bar level-{interf.get('level', 'medium').lower()}" style="width: {min(interf.get('score', 50), 100)}%;"></div>
        
        <h2>Detected Networks ({len(latest_analysis.get('networks', []))})</h2>
        <table>
            <tr>
                <th>SSID</th>
                <th>BSSID</th>
                <th>Channel</th>
                <th>Band</th>
                <th>RSSI</th>
                <th>Encryption</th>
            </tr>'''
    
    for net in latest_analysis.get('networks', []):
        html_content += f'''
            <tr>
                <td>{net.get('ssid', '<Hidden>')}</td>
                <td>{net.get('bssid', '')}</td>
                <td>{net.get('channel', '')}</td>
                <td>{net.get('band', '')}</td>
                <td>{net.get('rssi', '')} dBm</td>
                <td>{net.get('encryption', '')}</td>
            </tr>'''
    
    html_content += '''
        </table>
        
        <h2>Connected Devices</h2>
        <table>
            <tr>
                <th>MAC Address</th>
                <th>Manufacturer</th>
                <th>Connected To</th>
                <th>Signal</th>
                <th>Probed Networks</th>
            </tr>'''
    
    for dev in latest_analysis.get('connected_devices', []):
        html_content += f'''
            <tr>
                <td>{dev.get('device_mac', '')}</td>
                <td>{dev.get('manufacturer', 'Unknown')}</td>
                <td>{dev.get('connected_bssid', '')}</td>
                <td>{dev.get('signal', '')} dBm</td>
                <td>{', '.join(dev.get('probed_ssids', []))}</td>
            </tr>'''
    
    html_content += '''
        </table>
        
        <h2>Devices Searching for Wi-Fi</h2>
        <table>
            <tr>
                <th>MAC Address</th>
                <th>Manufacturer</th>
                <th>Signal</th>
                <th>Probed Networks</th>
            </tr>'''
    
    for dev in latest_analysis.get('searching_devices', []):
        html_content += f'''
            <tr>
                <td>{dev.get('device_mac', '')}</td>
                <td>{dev.get('manufacturer', 'Unknown')}</td>
                <td>{dev.get('signal', '')} dBm</td>
                <td>{', '.join(dev.get('probed_ssids', []))}</td>
            </tr>'''
    
    html_content += '''
        </table>
        
        <h2>Channel Congestion (2.4 GHz)</h2>
        <table>
            <tr>
                <th>Channel</th>
                <th>Network Count</th>
                <th>Congestion Level</th>
            </tr>'''
    
    congestion = latest_analysis.get('channel_congestion', {})
    for ch in sorted([c for c in congestion.keys() if str(c).isdigit()], key=lambda x: int(x)):
        data = congestion[ch]
        if isinstance(data, dict):
            level = data.get('congestion_level', 'N/A')
            html_content += f'''
            <tr class="level-{level.lower()}-bg">
                <td>{ch}</td>
                <td>{data.get('network_count', 0)}</td>
                <td>{level}</td>
            </tr>'''
    
    html_content += '''
        </table>
        
        <h2>Recommendations</h2>'''
    
    recs = latest_analysis.get('recommendations', {})
    if recs:
        for band, rec in recs.items():
            if isinstance(rec, dict) and rec.get('recommended'):
                html_content += f'''
        <div class="recommendation">
            <strong>{band}:</strong> Recommended channel {rec.get('recommended')}
            {f"({rec.get('reason', '')})" if rec.get('reason') else ""}
        </div>'''
    else:
        html_content += '<p>No recommendations available</p>'
    
    html_content += f'''
        <div class="footer">
            <p>Generated by WA-CPE Wi-Fi Analyzer on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>'''
    
    return Response(
        html_content,
        mimetype='text/html',
        headers={'Content-Disposition': f'attachment; filename=wifi_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'}
    )

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
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header-left h1 {
            color: #00d9ff;
            font-size: 28px;
        }
        
        .header-left .subtitle {
            color: #888;
            font-size: 14px;
            margin-top: 5px;
        }
        
        .header-right {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .control-btn {
            background: #0f3460;
            color: #00d9ff;
            border: 1px solid #00d9ff;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s;
        }
        
        .control-btn:hover {
            background: #00d9ff;
            color: #1a1a2e;
        }
        
        .control-btn.pause-btn {
            background: #ff9800;
            border-color: #ff9800;
            color: #fff;
        }
        
        .control-btn.pause-btn:hover {
            background: #f57c00;
            border-color: #f57c00;
        }
        
        .control-btn.resume-btn {
            background: #4caf50;
            border-color: #4caf50;
            color: #fff;
        }
        
        .control-btn.resume-btn:hover {
            background: #388e3c;
            border-color: #388e3c;
        }
        
        .control-btn.logout-btn {
            background: #f44336;
            border-color: #f44336;
            color: #fff;
        }
        
        .control-btn.logout-btn:hover {
            background: #d32f2f;
            border-color: #d32f2f;
        }
        
        .status-bar {
            background: rgba(0,217,255,0.1);
            padding: 10px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #0f3460;
        }
        
        .status-left {
            display: flex;
            gap: 20px;
            align-items: center;
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
        
        .status-dot.paused {
            background: #ff9800;
            animation: none;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .status-label {
            font-size: 14px;
        }
        
        .status-label.paused {
            color: #ff9800;
        }
        
        .export-buttons {
            display: flex;
            gap: 10px;
        }
        
        .export-btn {
            background: #0f3460;
            color: #00d9ff;
            border: 1px solid #00d9ff;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12px;
            display: flex;
            align-items: center;
            gap: 5px;
            transition: all 0.3s;
        }
        
        .export-btn:hover {
            background: #00d9ff;
            color: #1a1a2e;
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
            font-size: 14px;
            font-weight: bold;
            color: #00d9ff;
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
        
        .paused-banner {
            background: rgba(255,152,0,0.2);
            border: 2px solid #ff9800;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            text-align: center;
            display: none;
        }
        
        .paused-banner.visible {
            display: block;
        }
        
        .paused-banner h3 {
            color: #ff9800;
            margin-bottom: 5px;
        }
        
        .paused-banner p {
            color: #888;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-left">
            <h1>📡 WA-CPE Wi-Fi Analyzer</h1>
            <div class="subtitle">Real-time Wi-Fi Interference Analysis</div>
        </div>
        <div class="header-right">
            <button class="control-btn" onclick="exportData('csv')">
                📥 Export CSV
            </button>
            <button class="control-btn" onclick="exportData('html')">
                📄 Export HTML
            </button>
            <button class="control-btn pause-btn" id="pauseBtn" onclick="togglePause()">
                ⏸️ Pause
            </button>
            <button class="control-btn logout-btn" onclick="window.location.href='/logout'">
                🚪 Logout
            </button>
        </div>
    </div>
    
    <div class="status-bar">
        <div class="status-left">
            <div class="status-item">
                <div class="status-dot" id="statusDot"></div>
                <span class="status-label" id="statusLabel">Live Monitoring Active</span>
            </div>
            <div class="status-item">
                <span>Last Update: <span id="lastUpdate">--:--:--</span></span>
            </div>
            <div class="status-item">
                <span>Interface: wlan1</span>
            </div>
        </div>
    </div>
    
    <div class="main-content">
        <div class="card full-width">
            <div class="paused-banner" id="pausedBanner">
                <h3>⏸️ Monitoring Paused</h3>
                <p>Data is frozen. Click Resume to continue live updates.</p>
            </div>
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
        let isPaused = false;
        let updateInterval = null;
        
        function togglePause() {
            const endpoint = isPaused ? '/api/resume' : '/api/pause';
            fetch(endpoint, { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    isPaused = !isPaused;
                    updatePauseUI();
                })
                .catch(error => {
                    console.error('Error toggling pause:', error);
                });
        }
        
        function updatePauseUI() {
            const pauseBtn = document.getElementById('pauseBtn');
            const statusDot = document.getElementById('statusDot');
            const statusLabel = document.getElementById('statusLabel');
            const pausedBanner = document.getElementById('pausedBanner');
            
            if (isPaused) {
                pauseBtn.innerHTML = '▶️ Resume';
                pauseBtn.classList.remove('pause-btn');
                pauseBtn.classList.add('resume-btn');
                statusDot.classList.add('paused');
                statusLabel.textContent = 'Monitoring Paused';
                statusLabel.classList.add('paused');
                pausedBanner.classList.add('visible');
                if (updateInterval) {
                    clearInterval(updateInterval);
                    updateInterval = null;
                }
            } else {
                pauseBtn.innerHTML = '⏸️ Pause';
                pauseBtn.classList.remove('resume-btn');
                pauseBtn.classList.add('pause-btn');
                statusDot.classList.remove('paused');
                statusLabel.textContent = 'Live Monitoring Active';
                statusLabel.classList.remove('paused');
                pausedBanner.classList.remove('visible');
                updateDashboard();
                updateInterval = setInterval(updateDashboard, 5000);
            }
        }
        
        function updateDashboard() {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    if (data.paused === undefined) {
                        data.paused = false;
                    }
                    
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
                const color = count >= 3 ? '#ff4444' : count >= 2 ? '#ffaa00' : count >= 1 ? '#00d9ff' : '#1a5a6e';
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
        
        function exportData(format) {
            const endpoint = format === 'csv' ? '/api/export/csv' : '/api/export/html';
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
            const link = document.createElement('a');
            link.href = endpoint;
            link.download = format === 'csv' ? `wifi_analysis_${timestamp}.csv` : `wifi_analysis_${timestamp}.html`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
        
        updateInterval = setInterval(updateDashboard, 5000);
        updateDashboard();
    </script>
</body>
</html>
'''

def start_dashboard(interface='wlan1', host='0.0.0.0', port=5000):
    """Start the web dashboard"""
    global analyzer_interface, analyzer_running, analyzer_paused
    
    analyzer_interface = interface
    analyzer_running = True
    analyzer_paused = False
    
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
