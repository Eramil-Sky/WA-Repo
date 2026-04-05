#!/usr/bin/env python3
"""
Wi-Fi Performance Testing Module
Tests throughput, latency, jitter, and packet loss
"""

import subprocess
import re
import time
import statistics
from typing import Dict, Optional


class PerformanceTester:
    def __init__(self, interface: str = 'wlan0'):
        self.interface = interface
        
    def run_all_tests(self, target: str = '8.8.8.8', server: str = None) -> Dict:
        """Run all performance tests"""
        return {
            'latency': self.test_latency(target),
            'throughput': self.test_throughput(server) if server else self._simulate_throughput(),
            'quality': self.assess_connection_quality()
        }
    
    def test_latency(self, target: str = '8.8.8.8', count: int = 10) -> Dict:
        """Test latency and jitter using ping"""
        try:
            result = subprocess.check_output(
                ['ping', '-c', str(count), '-I', self.interface, target],
                stderr=subprocess.DEVNULL,
                timeout=30
            ).decode('utf-8', errors='ignore')
            
            return self._parse_ping_result(result)
        except Exception as e:
            try:
                result = subprocess.check_output(
                    ['ping', '-c', str(count), target],
                    stderr=subprocess.DEVNULL,
                    timeout=30
                ).decode('utf-8', errors='ignore')
                
                return self._parse_ping_result(result)
            except Exception as e2:
                return {
                    'error': str(e2),
                    'latency_avg': None,
                    'latency_min': None,
                    'latency_max': None,
                    'packet_loss': 100,
                    'note': 'Interface in monitor mode or no route to host'
                }
    
    def _parse_ping_result(self, output: str) -> Dict:
        """Parse ping output"""
        stats = {}
        
        loss_match = re.search(r'(\d+)% packet loss', output)
        if loss_match:
            stats['packet_loss'] = int(loss_match.group(1))
        
        rtt_match = re.search(
            r'rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)',
            output
        )
        if rtt_match:
            stats['latency_min'] = float(rtt_match.group(1))
            stats['latency_avg'] = float(rtt_match.group(2))
            stats['latency_max'] = float(rtt_match.group(3))
            stats['jitter'] = float(rtt_match.group(4))
        else:
            single_match = re.search(
                r'min/avg/max[^=]*= ([\d.]+)/([\d.]+)/([\d.]+)',
                output
            )
            if single_match:
                stats['latency_min'] = float(single_match.group(1))
                stats['latency_avg'] = float(single_match.group(2))
                stats['latency_max'] = float(single_match.group(3))
                stats['jitter'] = 0
        
        return stats
    
    def test_throughput(self, server: str = None, duration: int = 10) -> Dict:
        """Test throughput using iperf3"""
        if not server:
            return self._simulate_throughput()
        
        try:
            result = subprocess.check_output(
                ['iperf3', '-c', server, '-t', str(duration), '-J'],
                stderr=subprocess.DEVNULL,
                timeout=duration + 10
            ).decode('utf-8', errors='ignore')
            
            return self._parse_iperf_result(result)
        except Exception as e:
            return {
                'error': str(e),
                'throughput_mbps': None,
                'type': 'error'
            }
    
    def _parse_iperf_result(self, output: str) -> Dict:
        """Parse iperf3 JSON output"""
        import json
        try:
            data = json.loads(output)
            bits_per_sec = data['end']['sum_sent']['bits_per_second']
            mbps = bits_per_sec / 1_000_000
            
            return {
                'throughput_mbps': round(mbps, 2),
                'type': 'iperf3'
            }
        except:
            return {'throughput_mbps': 0, 'type': 'error'}
    
    def _simulate_throughput(self) -> Dict:
        """Simulate throughput based on signal quality"""
        signal_info = self._get_interface_stats()
        
        if not signal_info:
            return {
                'throughput_mbps': None,
                'type': 'simulation',
                'note': 'No signal info available'
            }
        
        rssi = signal_info.get('rssi', -100)
        
        if rssi >= -50:
            throughput = 200 + (abs(rssi) - 50) * 2
        elif rssi >= -60:
            throughput = 100 + (abs(rssi) - 60) * 10
        elif rssi >= -70:
            throughput = 50 + (abs(rssi) - 70) * 5
        elif rssi >= -80:
            throughput = 20 + (abs(rssi) - 80) * 3
        else:
            throughput = max(5, 10 + (abs(rssi) - 85) * 2)
        
        return {
            'throughput_mbps': round(throughput, 2),
            'type': 'estimated',
            'based_on_rssi': rssi
        }
    
    def _get_interface_stats(self) -> Optional[Dict]:
        """Get current interface statistics"""
        try:
            result = subprocess.check_output(
                ['iw', 'dev', self.interface, 'link'],
                stderr=subprocess.DEVNULL
            ).decode('utf-8', errors='ignore')
            
            stats = {}
            
            signal_match = re.search(r'signal: ([-\d]+)', result)
            if signal_match:
                stats['rssi'] = int(signal_match.group(1))
            
            tx_match = re.search(r'tx bitrate: ([\d.]+) (\w+)', result)
            if tx_match:
                stats['tx_rate'] = float(tx_match.group(1))
                stats['tx_unit'] = tx_match.group(2)
            
            rx_match = re.search(r'rx bitrate: ([\d.]+) (\w+)', result)
            if rx_match:
                stats['rx_rate'] = float(rx_match.group(1))
                stats['rx_unit'] = rx_match.group(2)
            
            return stats if stats else None
        except:
            return None
    
    def assess_connection_quality(self) -> Dict:
        """Assess overall connection quality"""
        signal = self._get_interface_stats()
        latency = self.test_latency()
        
        quality = {
            'score': 0,
            'rating': 'UNKNOWN',
            'factors': []
        }
        
        if signal and 'rssi' in signal:
            rssi_score = self._rate_rssi(signal['rssi'])
            quality['factors'].append({'metric': 'Signal Strength', 'score': rssi_score})
            quality['score'] += rssi_score * 0.4
        
        if latency.get('latency_avg'):
            latency_score = self._rate_latency(latency['latency_avg'])
            quality['factors'].append({'metric': 'Latency', 'score': latency_score})
            quality['score'] += latency_score * 0.3
        
        if latency.get('packet_loss', 0) == 0:
            quality['factors'].append({'metric': 'Packet Loss', 'score': 100})
            quality['score'] += 30
        else:
            pl_score = max(0, 100 - latency['packet_loss'] * 10)
            quality['factors'].append({'metric': 'Packet Loss', 'score': pl_score})
            quality['score'] += pl_score * 0.3
        
        quality['score'] = min(100, quality['score'])
        quality['rating'] = self._get_rating(quality['score'])
        
        return quality
    
    def _rate_rssi(self, rssi: int) -> float:
        """Rate RSSI value"""
        if rssi >= -50:
            return 100
        elif rssi >= -60:
            return 90 + (rssi + 60) * 1
        elif rssi >= -70:
            return 70 + (rssi + 70) * 2
        elif rssi >= -80:
            return 50 + (rssi + 80) * 2
        else:
            return max(10, 30 + (rssi + 85))
    
    def _rate_latency(self, latency: float) -> float:
        """Rate latency value"""
        if latency <= 10:
            return 100
        elif latency <= 30:
            return 90 + (30 - latency) * 0.5
        elif latency <= 50:
            return 70 + (50 - latency) * 1
        elif latency <= 100:
            return 50 + (100 - latency) * 0.4
        else:
            return max(10, 30 - (latency - 100) * 0.2)
    
    def _get_rating(self, score: float) -> str:
        """Get quality rating"""
        if score >= 90:
            return 'EXCELLENT'
        elif score >= 75:
            return 'GOOD'
        elif score >= 50:
            return 'FAIR'
        elif score >= 25:
            return 'POOR'
        else:
            return 'CRITICAL'


def main():
    tester = PerformanceTester()
    
    print("📊 Running performance tests...\n")
    
    print("🌐 Latency Test:")
    latency = tester.test_latency()
    if 'error' not in latency:
        print(f"   Avg: {latency.get('latency_avg', 'N/A')} ms")
        print(f"   Min: {latency.get('latency_min', 'N/A')} ms")
        print(f"   Max: {latency.get('latency_max', 'N/A')} ms")
        print(f"   Jitter: {latency.get('jitter', 'N/A')} ms")
        print(f"   Packet Loss: {latency.get('packet_loss', 'N/A')}%")
    
    print("\n⚡ Throughput Test:")
    throughput = tester.test_throughput()
    print(f"   {throughput.get('throughput_mbps', 'N/A')} Mbps ({throughput.get('type', 'N/A')})")
    
    print("\n📶 Connection Quality:")
    quality = tester.assess_connection_quality()
    print(f"   Score: {quality['score']:.1f}/100 ({quality['rating']})")
    for factor in quality['factors']:
        print(f"   - {factor['metric']}: {factor['score']:.1f}")


if __name__ == '__main__':
    main()
