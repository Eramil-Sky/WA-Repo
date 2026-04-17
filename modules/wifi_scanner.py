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
        
    def _ensure_monitor_mode(self) -> bool:
        """Ensure interface is in monitor mode"""
        import time
        try:
            subprocess.run(['sudo', 'killall', 'airodump-ng'], stderr=subprocess.DEVNULL)
            time.sleep(0.5)
            
            result = subprocess.run(['iw', 'dev'], capture_output=True, text=True, timeout=5)
            if self.interface in result.stdout and 'Monitor' in result.stdout:
                return True
            
            subprocess.run(['sudo', 'ip', 'link', 'set', self.interface, 'down'], stderr=subprocess.DEVNULL)
            result1 = subprocess.run(['sudo', 'iw', 'dev', self.interface, 'set', 'type', 'monitor'], capture_output=True, text=True)
            subprocess.run(['sudo', 'ip', 'link', 'set', self.interface, 'up'], stderr=subprocess.DEVNULL)
            time.sleep(1)
            
            result = subprocess.run(['iw', 'dev'], capture_output=True, text=True, timeout=5)
            if self.interface in result.stdout and 'Monitor' in result.stdout:
                return True
            
            subprocess.run(['sudo', 'ip', 'link', 'set', self.interface, 'down'], stderr=subprocess.DEVNULL)
            subprocess.run(['sudo', 'modprobe', '-r', '88XXau'], stderr=subprocess.DEVNULL)
            time.sleep(1)
            subprocess.run(['sudo', 'modprobe', '88XXau'], stderr=subprocess.DEVNULL)
            time.sleep(2)
            
            subprocess.run(['sudo', 'ip', 'link', 'set', self.interface, 'up'], stderr=subprocess.DEVNULL)
            subprocess.run(['sudo', 'iw', 'dev', self.interface, 'set', 'type', 'monitor'], stderr=subprocess.DEVNULL)
            time.sleep(1)
            
            result = subprocess.run(['iw', 'dev'], capture_output=True, text=True, timeout=5)
            return self.interface in result.stdout and 'Monitor' in result.stdout
        except Exception as e:
            print(f"Monitor mode error: {e}")
            return False
    
    def _run_airodump_scan(self, duration: int = 20) -> str:
        """Run airodump-ng and return CSV content"""
        import os
        import time
        
        subprocess.run(['sudo', 'killall', 'airodump-ng'], stderr=subprocess.DEVNULL)
        subprocess.run(['sudo', 'killall', '-9', 'airodump-ng'], stderr=subprocess.DEVNULL)
        time.sleep(1)
        
        csv_file = '/tmp/scan_temp'
        for f in [f'{csv_file}-01.csv', f'{csv_file}-01.kismet.csv']:
            if os.path.exists(f):
                os.remove(f)
        
        proc = subprocess.Popen(
            ['sudo', 'airodump-ng', '--background', '1', '-o', 'csv', '-w', csv_file, self.interface],
            stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL
        )
        
        time.sleep(duration)
        subprocess.run(['sudo', 'killall', 'airodump-ng'], stderr=subprocess.DEVNULL)
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except:
            subprocess.run(['sudo', 'killall', '-9', 'airodump-ng'], stderr=subprocess.DEVNULL)
        
        csv_path = f'{csv_file}-01.csv'
        if os.path.exists(csv_path):
            with open(csv_path, 'r') as f:
                return f.read()
        return ''
    
    def scan_networks(self) -> dict:
        """Scan for available Wi-Fi networks using airodump-ng with improved reliability"""
        import os
        import time
        
        self._ensure_monitor_mode()
        
        all_networks = {}
        all_probed = []
        
        for scan_num in range(2):
            csv_content = self._run_airodump_scan(duration=15)
            if csv_content:
                networks = self._parse_airodump_csv(csv_content)
                probed = self.get_probed_networks(csv_content)
                
                for net in networks:
                    bssid = net.get('bssid', '')
                    if bssid and bssid not in all_networks:
                        all_networks[bssid] = net
                    elif bssid in all_networks:
                        existing = all_networks[bssid]
                        if net.get('rssi', -100) > existing.get('rssi', -100):
                            all_networks[bssid] = net
                
                for item in probed:
                    found = False
                    for i, p in enumerate(all_probed):
                        if p.get('device_mac') == item.get('device_mac'):
                            found = True
                            break
                    if not found:
                        all_probed.append(item)
        
        return {
            'networks': list(all_networks.values()),
            'probed_networks': all_probed
        }
    
    def fast_scan(self) -> dict:
        """Quick single scan for dashboard - faster response time"""
        import os
        import time
        import signal
        
        subprocess.run(['sudo', 'killall', 'airodump-ng'], stderr=subprocess.DEVNULL)
        time.sleep(0.3)
        
        try:
            result = subprocess.run(['iw', 'dev', self.interface, 'info'], capture_output=True, text=True, timeout=3)
        except:
            try:
                subprocess.run(['sudo', 'ip', 'link', 'set', self.interface, 'down'], stderr=subprocess.DEVNULL)
                subprocess.run(['sudo', 'iw', 'dev', self.interface, 'set', 'type', 'monitor'], stderr=subprocess.DEVNULL)
                subprocess.run(['sudo', 'ip', 'link', 'set', self.interface, 'up'], stderr=subprocess.DEVNULL)
                time.sleep(0.5)
            except:
                pass
        
        csv_file = '/tmp/fast_scan'
        for f in [f'{csv_file}-01.csv', f'{csv_file}-01.kismet.csv']:
            if os.path.exists(f):
                os.remove(f)
        
        proc = subprocess.Popen(
            ['sudo', 'airodump-ng', '--background', '1', '-o', 'csv', '-w', csv_file, self.interface],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        
        time.sleep(8)
        subprocess.run(['sudo', 'killall', 'airodump-ng'], stderr=subprocess.DEVNULL)
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except:
            subprocess.run(['sudo', 'killall', '-9', 'airodump-ng'], stderr=subprocess.DEVNULL)
        
        csv_path = f'{csv_file}-01.csv'
        if os.path.exists(csv_path):
            try:
                with open(csv_path, 'r') as f:
                    csv_content = f.read()
                networks = self._parse_airodump_csv(csv_content)
                probed = self.get_probed_networks(csv_content)
                return {'networks': networks, 'probed_networks': probed}
            except:
                return {'networks': [], 'probed_networks': []}
        
        return {'networks': [], 'probed_networks': []}
    
    def scan_networks_with_channels(self) -> list:
        """Scan with channel-by-channel approach for accurate channel info (slower but more accurate)"""
        import os
        import time
        
        subprocess.run(['sudo', 'killall', 'airodump-ng'], stderr=subprocess.DEVNULL)
        for f in ['/tmp/ch_scan-01.csv', '/tmp/ch_scan-01.kismet.csv']:
            if os.path.exists(f):
                os.remove(f)
        
        channels_2g = [1, 6, 11, 3, 8, 13]
        channels_5g = [36, 40, 44, 48, 52, 56, 60, 64, 100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 144, 149, 153, 157, 161, 165]
        all_channels = channels_2g + channels_5g
        
        bssid_channels = {}
        bssid_data = {}
        
        for ch in all_channels:
            subprocess.run(['sudo', 'killall', 'airodump-ng'], stderr=subprocess.DEVNULL)
            time.sleep(0.3)
            
            try:
                proc = subprocess.Popen(
                    ['sudo', 'airodump-ng', '--channel', str(ch), '-o', 'csv', '-w', '/tmp/ch_scan', self.interface],
                    stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL
                )
                time.sleep(5)
                subprocess.run(['sudo', 'killall', 'airodump-ng'], stderr=subprocess.DEVNULL)
                try:
                    proc.terminate()
                    proc.wait(timeout=3)
                except:
                    subprocess.run(['sudo', 'killall', '-9', 'airodump-ng'], stderr=subprocess.DEVNULL)
            except:
                pass
            
            try:
                if os.path.exists('/tmp/ch_scan-01.csv'):
                    with open('/tmp/ch_scan-01.csv', 'r') as f:
                        content = f.read()
                    for line in content.split('\n'):
                        if line.startswith('BSSID') or 'First time' in line or not line.strip() or 'Station' in line:
                            continue
                        parts = [p.strip() for p in line.split(',')]
                        if len(parts) >= 14:
                            bssid = parts[0].strip()
                            if not bssid or len(bssid) != 17 or ':' not in bssid:
                                continue
                            try:
                                power_str = parts[8].strip() if len(parts) > 8 else '-100'
                                rssi = int(power_str) if power_str.lstrip('-').isdigit() else -100
                                essid_len = int(parts[12].strip()) if parts[12].strip().isdigit() else 0
                                essid = parts[13].strip() if len(parts) > 13 else ''
                            except:
                                continue
                            
                            if bssid not in bssid_channels:
                                bssid_channels[bssid] = ch
                                bssid_data[bssid] = {'rssi': rssi, 'essid': essid, 'essid_len': essid_len}
                            else:
                                if rssi > bssid_data[bssid]['rssi']:
                                    bssid_data[bssid]['rssi'] = rssi
                                    bssid_data[bssid]['essid'] = essid
                                    bssid_data[bssid]['essid_len'] = essid_len
            except:
                pass
        
        networks = []
        for bssid, ch in bssid_channels.items():
            data = bssid_data[bssid]
            freq = self._channel_to_freq(ch)
            band = '2.4GHz' if 2400 <= freq <= 2500 else '5GHz'
            essid = data['essid'] if data['essid_len'] > 0 else '<Hidden>'
            
            networks.append({
                'timestamp': datetime.now().isoformat(),
                'bssid': bssid,
                'ssid': essid,
                'rssi': data['rssi'],
                'channel': ch,
                'frequency': freq,
                'band': band
            })
        
        subprocess.run(['sudo', 'rm', '-f', '/tmp/ch_scan-01.csv', '/tmp/ch_scan-01.kismet.csv'], stderr=subprocess.DEVNULL)
        
        return networks
    
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
                    
                    if not bssid or len(bssid) != 17 or ':' not in bssid:
                        continue
                    
                    if bssid.replace(':', '') == '0' * 12 or bssid == '00:00:00:00:00:00':
                        continue
                    
                    channel = int(channel_str) if channel_str.isdigit() and int(channel_str) > 0 else None
                    rssi = int(power_str) if power_str.lstrip('-').isdigit() else -100
                    
                    if rssi == -1 or rssi < -95:
                        continue
                    
                    essid = parts[13].strip() if len(parts) > 13 else ''
                    if not essid and parts[12].strip().isdigit():
                        essid_len_check = int(parts[12].strip())
                        if essid_len_check > 0 and len(parts) > 14:
                            essid = parts[14].strip() if len(parts) > 14 else ''
                    ssid = essid if essid else '<Hidden>'
                    
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
    
    def get_probed_networks(self, csv_data: str) -> list:
        """Extract probed ESSIDs and connected BSSIDs from station data (reveals hidden SSIDs)"""
        probed = []
        lines = csv_data.strip().split('\n')
        in_station_section = False
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('Station'):
                in_station_section = True
                continue
            
            if in_station_section and line and not line.startswith('BSSID'):
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 6:
                    station_mac = parts[0].strip()
                    if station_mac and len(station_mac) == 17 and ':' in station_mac:
                        signal_str = parts[3].strip() if len(parts) > 3 else '-100'
                        signal = int(signal_str) if signal_str.lstrip('-').isdigit() else -100
                        connected_bssid = parts[5].strip() if len(parts) > 5 else ''
                        probed_essids = parts[6].strip() if len(parts) > 6 else ''
                        
                        item = {
                            'device_mac': station_mac,
                            'probed_ssids': [],
                            'connected_bssid': '',
                            'signal': signal
                        }
                        
                        if connected_bssid and connected_bssid != '(not associated)' and ':' in connected_bssid:
                            if not (connected_bssid.replace(':', '') == '0' * 12 or connected_bssid == '00:00:00:00:00:00'):
                                item['connected_bssid'] = connected_bssid
                        
                        if probed_essids and probed_essids != '(not associated)':
                            item['probed_ssids'] = [s.strip() for s in probed_essids.split(',') if s.strip()]
                        
                        if item['probed_ssids'] or item['connected_bssid']:
                            probed.append(item)
        
        return probed
    
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
