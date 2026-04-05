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
        """Scan for available Wi-Fi networks using airodump-ng"""
        import os
        import signal
        import time
        
        subprocess.run(['sudo', 'killall', 'airodump-ng'], stderr=subprocess.DEVNULL)
        for f in ['/tmp/scan_temp-01.csv', '/tmp/scan_temp-01.kismet.csv']:
            if os.path.exists(f):
                os.remove(f)
        
        proc = subprocess.Popen(
            ['sudo', 'airodump-ng', '--background', '1', '-o', 'csv', '-w', '/tmp/scan_temp', self.interface],
            stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL
        )
        
        time.sleep(8)
        subprocess.run(['sudo', 'killall', 'airodump-ng'], stderr=subprocess.DEVNULL)
        proc.terminate()
        
        try:
            if os.path.exists('/tmp/scan_temp-01.csv'):
                with open('/tmp/scan_temp-01.csv', 'r') as f:
                    return self._parse_airodump_csv(f.read())
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
    
    def _parse_airodump_csv(self, csv_data: str) -> list:
        """Parse airodump-ng CSV output into structured data"""
        networks = []
        lines = csv_data.strip().split('\n')
        for line in lines:
            if not line or line.startswith('BSSID') or 'First time seen' in line or line.startswith('Station'):
                continue
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 14:
                try:
                    bssid = parts[0]
                    channel_str = parts[3].strip()
                    power_str = parts[8].strip()
                    essid_len = int(parts[12].strip()) if parts[12].strip().isdigit() else 0
                    essid = parts[13].strip() if len(parts) > 13 else ''
                    
                    if not bssid or len(bssid) != 17 or ':' not in bssid:
                        continue
                    
                    channel = int(channel_str) if channel_str.isdigit() and int(channel_str) > 0 else None
                    rssi = int(power_str) if power_str.lstrip('-').isdigit() else -100
                    
                    ssid = essid if essid and essid_len > 0 else '<Hidden>'
                    
                    freq = 0
                    band = 'Unknown'
                    if channel:
                        freq = self._channel_to_freq(channel)
                        band = '2.4GHz' if 2400 <= freq <= 2500 else '5GHz'
                    elif rssi > -100:
                        freq = 2437
                        band = '2.4GHz'
                        channel = 6
                    
                    networks.append({
                        'timestamp': datetime.now().isoformat(),
                        'bssid': bssid,
                        'ssid': ssid,
                        'rssi': rssi,
                        'channel': channel if channel else 1,
                        'frequency': freq if freq else 2437,
                        'band': band
                    })
                except (ValueError, IndexError):
                    continue
        return networks
    
    def _channel_to_freq(self, channel: int) -> int:
        """Convert channel to frequency"""
        if 1 <= channel <= 13:
            return 2407 + (channel * 5)
        elif channel == 14:
            return 2484
        elif 36 <= channel <= 165:
            return 5000 + (channel * 5)
        return 2437
    
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
