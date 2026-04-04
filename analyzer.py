#!/usr/bin/env python3
"""
Wi-Fi Interference Analyzer - Main Application
Orchestrates all modules and provides dashboard
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.wifi_scanner import WiFiScanner
from modules.interference_detector import InterferenceDetector
from modules.performance_tester import PerformanceTester
from modules.correlation_engine import CorrelationEngine
from modules.database import AnalyzerDatabase
from datetime import datetime
import json


class WiFiInterferenceAnalyzer:
    def __init__(self, interface: str = 'wlan0'):
        self.interface = interface
        self.scanner = WiFiScanner(interface)
        self.detector = InterferenceDetector()
        self.tester = PerformanceTester(interface)
        self.correlator = CorrelationEngine()
        self.database = AnalyzerDatabase()
    
    def run_full_analysis(self) -> dict:
        """Run complete analysis cycle"""
        print("🔍 Starting Wi-Fi Interference Analysis...\n")
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'interface': self.interface,
            'scan_data': {},
            'interference_data': {},
            'performance_data': {},
            'correlation_data': {},
            'recommendations': []
        }
        
        print("📡 Scanning networks...")
        networks = self.scanner.scan_networks()
        signal_info = self.scanner.get_signal_info()
        noise_floor = self.scanner.get_noise_floor()
        
        analysis['scan_data'] = {
            'networks': networks,
            'network_count': len(networks),
            'rssi': signal_info.get('rssi') if signal_info else None,
            'tx_rate': signal_info.get('tx_rate') if signal_info else None,
            'rx_rate': signal_info.get('rx_rate') if signal_info else None,
            'noise': noise_floor
        }
        print(f"   Found {len(networks)} networks")
        
        print("📊 Analyzing interference...")
        analysis['interference_data'] = self.detector.analyze(networks)
        
        congested = sum(1 for ch, data in 
                       analysis['interference_data'].get('channel_congestion', {}).items()
                       if data.get('congestion_level') in ['HIGH', 'CRITICAL'])
        print(f"   {congested} congested channels detected")
        
        print("⚡ Testing performance...")
        analysis['performance_data'] = self.tester.run_all_tests()
        
        if analysis['performance_data'].get('latency'):
            lat = analysis['performance_data']['latency']
            print(f"   Latency: {lat.get('latency_avg', 'N/A')} ms")
        
        if analysis['performance_data'].get('throughput'):
            tp = analysis['performance_data']['throughput']
            print(f"   Throughput: {tp.get('throughput_mbps', 'N/A')} Mbps")
        
        print("🧠 Correlating data...")
        analysis['correlation_data'] = self.correlator.correlate(
            analysis['scan_data'],
            analysis['performance_data'],
            analysis['interference_data']
        )
        
        impact_level = analysis['correlation_data']['interference_impact']['level']
        print(f"   Interference Impact: {impact_level}")
        
        analysis['recommendations'] = self._extract_recommendations(analysis)
        
        self.database.save_scan({
            'timestamp': analysis['timestamp'],
            'rssi': analysis['scan_data'].get('rssi'),
            'noise': analysis['scan_data'].get('noise'),
            'snr': analysis['correlation_data']['interference_impact'].get('snr'),
            'throughput': analysis['performance_data'].get('throughput', {}).get('throughput_mbps'),
            'latency_avg': analysis['performance_data'].get('latency', {}).get('latency_avg'),
            'latency_max': analysis['performance_data'].get('latency', {}).get('latency_max'),
            'latency_min': analysis['performance_data'].get('latency', {}).get('latency_min'),
            'packet_loss': analysis['performance_data'].get('latency', {}).get('packet_loss'),
            'interference_score': analysis['correlation_data']['interference_impact']['score'],
            'congestion_level': impact_level,
            'networks': networks
        })
        
        print("\n✅ Analysis complete!")
        
        return analysis
    
    def _extract_recommendations(self, analysis: dict) -> list:
        """Extract actionable recommendations"""
        recs = []
        
        rec_24 = analysis['interference_data'].get('recommendations', {}).get('2.4GHz', {})
        if rec_24.get('recommended'):
            recs.append({
                'type': 'channel',
                'priority': 'high',
                'message': f"Switch to channel {rec_24['recommended']} for 2.4GHz",
                'reason': rec_24.get('reason', '')
            })
        
        rec_5 = analysis['interference_data'].get('recommendations', {}).get('5GHz', {})
        if rec_5.get('recommended'):
            recs.append({
                'type': 'band',
                'priority': 'medium',
                'message': f"Consider 5GHz channel {rec_5['recommended']}",
                'reason': rec_5.get('reason', '')
            })
        
        for insight in analysis['correlation_data'].get('actionable_insights', []):
            recs.append(insight)
        
        return recs
    
    def print_summary(self, analysis: dict):
        """Print analysis summary"""
        print("\n" + "=" * 60)
        print("📊 WI-FI INTERFERENCE ANALYSIS SUMMARY")
        print("=" * 60)
        
        print("\n📡 Network Overview:")
        print(f"   Networks detected: {analysis['scan_data']['network_count']}")
        print(f"   Your signal: {analysis['scan_data'].get('rssi', 'N/A')} dBm")
        print(f"   Noise floor: {analysis['scan_data'].get('noise', 'N/A')} dBm")
        
        snr = analysis['correlation_data']['interference_impact'].get('snr')
        if snr:
            print(f"   SNR: {snr:.1f} dB")
        
        print("\n📊 Interference Impact:")
        impact = analysis['correlation_data']['interference_impact']
        print(f"   Level: {impact['level']}")
        print(f"   Score: {impact['score']:.1f}")
        
        congestion = analysis['interference_data'].get('channel_congestion', {})
        if congestion:
            print("\n   Channel Congestion:")
            for ch in sorted(congestion.keys()):
                data = congestion[ch]
                print(f"   - Channel {ch}: {data['network_count']} networks ({data['congestion_level']})")
        
        print("\n⚡ Performance Metrics:")
        perf = analysis['performance_data']
        if perf.get('latency'):
            lat = perf['latency']
            print(f"   Latency: {lat.get('latency_avg', 'N/A'):.1f} ms (avg)")
            print(f"   Jitter: {lat.get('jitter', 'N/A')} ms")
            print(f"   Packet Loss: {lat.get('packet_loss', 'N/A')}%")
        
        if perf.get('throughput'):
            tp = perf['throughput']
            print(f"   Throughput: {tp.get('throughput_mbps', 'N/A')} Mbps ({tp.get('type', 'N/A')})")
        
        print("\n💡 Recommendations:")
        for i, rec in enumerate(analysis['recommendations'], 1):
            print(f"   {i}. [{rec['priority'].upper()}] {rec['message']}")
        
        print("\n" + "=" * 60)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Wi-Fi Interference Analyzer')
    parser.add_argument('-i', '--interface', default='wlan0', help='Wi-Fi interface')
    parser.add_argument('-j', '--json', action='store_true', help='Output as JSON')
    parser.add_argument('--db', default='wifi_analyzer.db', help='Database path')
    
    args = parser.parse_args()
    
    analyzer = WiFiInterferenceAnalyzer(interface=args.interface)
    
    try:
        analysis = analyzer.run_full_analysis()
        
        if args.json:
            print(json.dumps(analysis, indent=2))
        else:
            analyzer.print_summary(analysis)
            
    except KeyboardInterrupt:
        print("\n\nAnalysis cancelled by user")
    except Exception as e:
        print(f"\nError: {e}")
        if args.json:
            print(json.dumps({'error': str(e)}))
        raise


if __name__ == '__main__':
    main()
