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
        scan_result = self.scanner.scan_networks()
        networks = scan_result.get('networks', [])
        probed_networks = scan_result.get('probed_networks', [])
        signal_info = self.scanner.get_signal_info()
        noise_floor = self.scanner.get_noise_floor()
        
        analysis['scan_data'] = {
            'networks': networks,
            'probed_networks': probed_networks,
            'network_count': len(networks),
            'rssi': signal_info.get('rssi') if signal_info else None,
            'tx_rate': signal_info.get('tx_rate') if signal_info else None,
            'rx_rate': signal_info.get('rx_rate') if signal_info else None,
            'noise': noise_floor
        }
        print(f"   Found {len(networks)} networks")
        if probed_networks:
            print(f"   Found {len(probed_networks)} devices probing networks")
        
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
        
        networks = analysis['scan_data'].get('networks', [])
        if networks:
            probed = analysis['scan_data'].get('probed_networks', [])
            probed = probed if probed else []
            
            bssid_to_ssids = {}
            for item in probed:
                device_mac = item.get('device_mac', '')
                ssids = item.get('probed_ssids', [])
                for ssid in ssids:
                    ssid = ssid.strip()
                    if ssid:
                        bssid_to_ssids[ssid] = ssid
            
            print("\n   📶 Detected Networks:")
            print(f"   {'SSID':<20} {'BSSID':<18} {'Ch':<4} {'RSSI':<6} {'Band':<6}")
            print(f"   {'-'*65}")
            for net in networks[:10]:
                bssid = net.get('bssid', 'N/A')
                ch = net.get('channel', '?')
                rssi = net.get('rssi', '?')
                band = net.get('band', '?')[:5]
                
                hidden_ssid = '<Hidden>'
                for probed_item in probed:
                    connected_bssid = probed_item.get('connected_bssid', '')
                    if connected_bssid and connected_bssid.lower() == bssid.lower():
                        ssids = probed_item.get('probed_ssids', [])
                        for ssid in ssids:
                            ssid = ssid.strip()
                            if ssid and ssid != '(not associated)':
                                hidden_ssid = ssid[:19]
                                break
                
                print(f"   {hidden_ssid:<20} {bssid:<18} {ch:<4} {rssi:<6} {band:<6}")
        
        probed = analysis['scan_data'].get('probed_networks', [])
        if probed:
            print("\n   📱 Connected Devices:")
            print(f"   {'Device MAC':<19} {'Connected To (BSSID)':<19} {'Signal':<8}")
            print(f"   {'-'*50}")
            connected_devices = []
            for item in probed:
                connected_bssid = item.get('connected_bssid', '')
                if connected_bssid and ':' in connected_bssid:
                    device_mac = item.get('device_mac', 'N/A')
                    signal = item.get('signal', 'N/A')
                    connected_devices.append({
                        'device': device_mac,
                        'bssid': connected_bssid,
                        'signal': signal
                    })
                    print(f"   {device_mac:<19} {connected_bssid:<19}")
            
            if connected_devices:
                bssid_set = {d['bssid'] for d in connected_devices}
                print(f"\n   📶 Networks: {len(bssid_set)}")
                for bssid in sorted(bssid_set):
                    count = sum(1 for d in connected_devices if d['bssid'] == bssid)
                    print(f"      {bssid}: {count} device(s) connected")
            
            searching = []
            for item in probed:
                ssids = item.get('probed_ssids', [])
                device_mac = item.get('device_mac', 'N/A')
                for ssid in ssids:
                    ssid = ssid.strip()
                    if ssid and ssid not in [d.get('connected_to') for d in searching]:
                        searching.append({
                            'device': device_mac,
                            'ssid': ssid
                        })
            
            if searching:
                print("\n   🔍 Device Search History:")
                print(f"   {'Device MAC':<19} {'Searching For':<25}")
                print(f"   {'-'*45}")
                seen_ssids = set()
                for item in searching[:15]:
                    ssid = item.get('ssid', 'N/A')
                    if ssid not in seen_ssids:
                        print(f"   {item.get('device', 'N/A'):<19} {ssid:<25}")
                        seen_ssids.add(ssid)
        
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
        lat = perf.get('latency') or {}
        lat_avg = lat.get('latency_avg')
        print(f"   Latency: {lat_avg:.1f} ms (avg)" if lat_avg is not None else "   Latency: N/A")
        print(f"   Jitter: {lat.get('jitter', 'N/A')} ms")
        print(f"   Packet Loss: {lat.get('packet_loss', 'N/A')}%")
        
        tp = perf.get('throughput') or {}
        tp_mbps = tp.get('throughput_mbps')
        print(f"   Throughput: {tp_mbps} Mbps ({tp.get('type', 'N/A')})" if tp_mbps else "   Throughput: N/A")
        
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
