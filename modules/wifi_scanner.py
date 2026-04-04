#!/usr/bin/env python3
"""
Wi-Fi Signal Scanner Module
Collects SSID, Channel, RSSI, Band information
"""

import subprocess
import re
import json
from datetime import datetime
from typing import List


class WiFiScanner:
    def __init__(self, interface: str = 'wlan0'):
        self.interface = interface
        self.supported_bands: list = [2.4, 5]
        
    def scan_networks(self) -> list:
        """Scan for available Wi-Fi networks"""
        try:
            result = subprocess.check_output(
                ['sudo', 'iw', 'dev', self.interface, 'scan'],
                stderr=subprocess.DEVNULL,
                timeout=30
            ).decode('utf-8', errors='ignore')
            
            return self._parse_scan_output(result)
        except subprocess.TimeoutExpired:
            print(f"Scan timeout on {self.interface}")
            return []
        except Exception as e:
            print(f"Scan error: {e}")
            return []
    
    def _parse_scan_output(self, output: str) -> list:
        """Parse iw scan output into structured data"""
        networks = []
        current_network = {}
        
        for line in output.split('\n'):
            line = line.strip()
            
            if line.startswith('BSS '):
                if current_network:
                    networks.append(current_network)
                current_network = {
                    'timestamp': datetime.now().isoformat(),
                    'bssid': line.split()[1].rstrip('(on ' + self.interface + ')')
                }
            
            elif line.startswith('SSID:'):
                current_network['ssid'] = line.split('SSID:')[1].strip()
            
            elif 'signal:' in line:
                signal_match = re.search(r'signal: ([-\d]+)', line)
                if signal_match:
                    current_network['rssi'] = int(signal_match.group(1))
            
            elif line.startswith('freq:'):
                freq_match = re.search(r'freq: (\d+)', line)
                if freq_match:
                    freq = int(freq_match.group(1))
                    current_network['frequency'] = freq
                    current_network['channel'] = self._freq_to_channel(freq)
                    current_network['band'] = '2.4GHz' if freq < 3000 else '5GHz'
            
            elif 'SSID:' in line and not current_network.get('ssid'):
                ssid = line.split('SSID:')[1].strip()
                if ssid:
                    current_network['ssid'] = ssid
        
        if current_network:
            networks.append(current_network)
        
        return networks
    
    def _freq_to_channel(self, freq: int) -> int:
        """Convert frequency to channel number"""
        if 2412 <= freq <= 2484:
            if freq == 2484:
                return 14
            return (freq - 2407) // 5
        elif 5170 <= freq <= 5825:
            return (freq - 5000) // 5
        return 0
    
    def get_signal_info(self):
        """Get current connection signal information"""
        try:
            result = subprocess.check_output(
                ['iw', 'dev', self.interface, 'link'],
                stderr=subprocess.DEVNULL
            ).decode('utf-8', errors='ignore')
            
            info = {}
            
            for line in result.split('\n'):
                line = line.strip()
                if 'signal:' in line:
                    signal_match = re.search(r'signal: ([-\d]+)', line)
                    if signal_match:
                        info['rssi'] = int(signal_match.group(1))
                elif 'tx bitrate:' in line:
                    match = re.search(r'(\d+) MGbit', line)
                    if match:
                        info['tx_rate'] = int(match.group(1))
                elif 'rx bitrate:' in line:
                    match = re.search(r'(\d+) MGbit', line)
                    if match:
                        info['rx_rate'] = int(match.group(1))
            
            return info if info else None
        except Exception as e:
            print(f"Signal info error: {e}")
            return None
    
    def get_noise_floor(self):
        """Get noise floor using iw survey dump"""
        try:
            result = subprocess.check_output(
                ['sudo', 'iw', 'dev', self.interface, 'survey', 'dump'],
                stderr=subprocess.DEVNULL
            ).decode('utf-8', errors='ignore')
            
            noise_match = re.search(r'noise: ([-\d]+)', result)
            if noise_match:
                return int(noise_match.group(1))
        except Exception as e:
            print(f"Noise floor error: {e}")
        return None
    
    def get_channel_utilization(self):
        """Get channel busy time percentage"""
        try:
            result = subprocess.check_output(
                ['sudo', 'iw', 'dev', self.interface, 'survey', 'dump'],
                stderr=subprocess.DEVNULL
            ).decode('utf-8', errors='ignore')
            
            data = {}
            in_channel = False
            for line in result.split('\n'):
                if 'frequency:' in line:
                    in_channel = True
                elif in_channel:
                    if 'channel active time:' in line:
                        match = re.search(r'(\d+)', line)
                        if match:
                            data['active_time'] = int(match.group(1))
                    elif 'channel busy time:' in line:
                        match = re.search(r'(\d+)', line)
                        if match:
                            data['busy_time'] = int(match.group(1))
                    elif 'channel receive time:' in line:
                        in_channel = False
            
            if 'active_time' in data and 'busy_time' in data:
                data['utilization'] = (data['busy_time'] / data['active_time'] * 100 
                                       if data['active_time'] > 0 else 0)
                return data
        except Exception as e:
            print(f"Channel utilization error: {e}")
        return None


def main():
    scanner = WiFiScanner()
    print("🔍 Scanning Wi-Fi networks...\n")
    
    networks = scanner.scan_networks()
    print(f"📡 Found {len(networks)} networks:\n")
    print(f"{'SSID':<20} {'Channel':<8} {'RSSI':<8} {'Band':<8}")
    print("-" * 50)
    
    for net in networks:
        ssid = net.get('ssid', 'Hidden')[:19]
        ch = net.get('channel', 'N/A')
        rssi = net.get('rssi', 'N/A')
        band = net.get('band', 'N/A')
        print(f"{ssid:<20} {str(ch):<8} {str(rssi):<8} {band:<8}")
    
    print("\n📶 Current signal info:")
    signal = scanner.get_signal_info()
    if signal:
        print(f"   RSSI: {signal.get('rssi')} dBm")
        print(f"   TX Rate: {signal.get('tx_rate', 'N/A')} Mbps")
        print(f"   RX Rate: {signal.get('rx_rate', 'N/A')} Mbps")
    
    print("\n📊 Noise floor:")
    noise = scanner.get_noise_floor()
    print(f"   {noise} dBm" if noise else "   Unable to read")


if __name__ == '__main__':
    main()
