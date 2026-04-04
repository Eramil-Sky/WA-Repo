#!/usr/bin/env python3
"""
Flask Web Dashboard for Wi-Fi Interference Analyzer
"""

from flask import Flask, render_template, jsonify, request
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.wifi_scanner import WiFiScanner
from modules.interference_detector import InterferenceDetector
from modules.performance_tester import PerformanceTester
from modules.correlation_engine import CorrelationEngine
from modules.database import AnalyzerDatabase

app = Flask(__name__)

scanner = WiFiScanner()
detector = InterferenceDetector()
tester = PerformanceTester()
correlator = CorrelationEngine()
db = AnalyzerDatabase()


@app.route('/')
def index():
    return render_template('dashboard.html')


@app.route('/api/analyze')
def analyze():
    try:
        networks = scanner.scan_networks()
        signal_info = scanner.get_signal_info()
        noise_floor = scanner.get_noise_floor()
        interference_data = detector.analyze(networks)
        performance_data = tester.run_all_tests()
        
        scan_data = {
            'networks': networks,
            'network_count': len(networks),
            'rssi': signal_info.get('rssi') if signal_info else None,
            'tx_rate': signal_info.get('tx_rate') if signal_info else None,
            'rx_rate': signal_info.get('rx_rate') if signal_info else None,
            'noise': noise_floor
        }
        
        correlation_data = correlator.correlate(
            scan_data, performance_data, interference_data
        )
        
        db.save_scan({
            'timestamp': '',
            'rssi': scan_data.get('rssi'),
            'noise': scan_data.get('noise'),
            'snr': correlation_data['interference_impact'].get('snr'),
            'throughput': performance_data.get('throughput', {}).get('throughput_mbps'),
            'latency_avg': performance_data.get('latency', {}).get('latency_avg'),
            'latency_max': performance_data.get('latency', {}).get('latency_max'),
            'latency_min': performance_data.get('latency', {}).get('latency_min'),
            'packet_loss': performance_data.get('latency', {}).get('packet_loss'),
            'interference_score': correlation_data['interference_impact']['score'],
            'congestion_level': correlation_data['interference_impact']['level'],
            'networks': networks
        })
        
        return jsonify({
            'success': True,
            'scan_data': scan_data,
            'interference_data': interference_data,
            'performance_data': performance_data,
            'correlation_data': correlation_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/history')
def history():
    limit = request.args.get('limit', 100, type=int)
    scans = db.get_recent_scans(limit)
    return jsonify({'success': True, 'scans': scans})


@app.route('/api/trends')
def trends():
    hours = request.args.get('hours', 24, type=int)
    trends_data = db.get_performance_trends(hours)
    return jsonify({'success': True, 'trends': trends_data})


@app.route('/api/channel_stats')
def channel_stats():
    hours = request.args.get('hours', 24, type=int)
    stats = db.get_channel_stats(hours)
    return jsonify({'success': True, 'stats': stats})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
