#!/usr/bin/env python3
"""
Windows-compatible Wi-Fi Analyzer
Scans actual network connection using netsh commands
"""

import subprocess
import re
import json
from datetime import datetime


def get_current_connection():
    """Get current Wi-Fi connection info using netsh"""
    try:
        result = subprocess.check_output(
            ['netsh', 'wlan', 'show', 'interfaces'],
            stderr=subprocess.DEVNULL,
            text=True
        )
        
        info = {}
        for line in result.split('\n'):
            line = line.strip()
            if line.startswith('SSID') and 'BSSID' not in line:
                info['ssid'] = line.split(':', 1)[1].strip()
            elif line.startswith('BSSID'):
                info['bssid'] = line.split(':', 1)[1].strip()
            elif line.startswith('Signal'):
                signal_match = re.search(r'(\d+)%', line)
                if signal_match:
                    info['signal_percent'] = int(signal_match.group(1))
            elif line.startswith('Rssi'):
                rssi_match = re.search(r'(-?\d+)', line)
                if rssi_match:
                    info['rssi'] = int(rssi_match.group(1))
            elif line.startswith('Channel'):
                ch_match = re.search(r'(\d+)', line)
                if ch_match:
                    info['channel'] = int(ch_match.group(1))
            elif line.startswith('Band'):
                band = line.split(':', 1)[1].strip()
                info['band'] = band
        
        return info if info else None
    except Exception as e:
        return None


def scan_networks():
    """Scan for available Wi-Fi networks using netsh"""
    try:
        result = subprocess.check_output(
            ['netsh', 'wlan', 'show', 'networks', 'mode=bssid'],
            stderr=subprocess.DEVNULL,
            text=True
        )
        
        networks = []
        lines = result.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith('SSID') and ':' in line and 'BSSID' not in line and 'Network type' not in line:
                ssid = line.split(':', 1)[1].strip()
                signal_pct = None
                channel = None
                band = None
                
                j = i + 1
                while j < len(lines) and not lines[j].strip().startswith('SSID'):
                    sub_line = lines[j].strip()
                    
                    if sub_line.startswith('Signal'):
                        sig_match = re.search(r'(\d+)%', sub_line)
                        if sig_match:
                            signal_pct = int(sig_match.group(1))
                    elif sub_line.startswith('Channel'):
                        ch_match = re.search(r'(\d+)', sub_line)
                        if ch_match:
                            channel = int(ch_match.group(1))
                    elif sub_line.startswith('Band'):
                        band = '5GHz' if '5' in sub_line else '2.4GHz'
                    
                    j += 1
                
                if channel and signal_pct:
                    rssi = int(-100 + (signal_pct * 0.55))
                    networks.append({
                        'ssid': ssid,
                        'channel': channel,
                        'rssi': rssi,
                        'band': band
                    })
                
                i = j
            else:
                i += 1
        
        return networks
    except Exception as e:
        return []


def test_latency(target='8.8.8.8', count=5):
    """Test latency using ping"""
    try:
        result = subprocess.check_output(
            ['ping', '-n', str(count), target],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=30
        )
        
        stats = {}
        
        loss_match = re.search(r'(\d+)% loss', result)
        if loss_match:
            stats['packet_loss'] = int(loss_match.group(1))
        
        rtt_match = re.search(
            r'Minimum = (\d+)ms, Maximum = (\d+)ms, Average = (\d+)ms',
            result
        )
        if rtt_match:
            stats['latency_min'] = int(rtt_match.group(1))
            stats['latency_max'] = int(rtt_match.group(2))
            stats['latency_avg'] = int(rtt_match.group(3))
            stats['jitter'] = stats['latency_max'] - stats['latency_min']
        else:
            stats['latency_avg'] = None
            stats['packet_loss'] = 100
        
        return stats
    except Exception as e:
        return {'latency_avg': None, 'packet_loss': 100}


def analyze_interference(networks):
    """Analyze network interference"""
    channel_counts = {}
    
    for net in networks:
        ch = net['channel']
        if ch not in channel_counts:
            channel_counts[ch] = {'count': 0, 'total_rssi': 0, 'networks': []}
        channel_counts[ch]['count'] += 1
        channel_counts[ch]['total_rssi'] += net['rssi']
        channel_counts[ch]['networks'].append(net['ssid'])
    
    congestion = {}
    for ch, data in channel_counts.items():
        avg_rssi = data['total_rssi'] / data['count']
        
        if data['count'] <= 2:
            level = 'LOW'
        elif data['count'] <= 4:
            level = 'MEDIUM'
        else:
            level = 'HIGH' if avg_rssi > -70 else 'MEDIUM'
        
        congestion[ch] = {
            'network_count': data['count'],
            'avg_rssi': round(avg_rssi, 1),
            'networks': data['networks'],
            'congestion_level': level
        }
    
    ideal_24 = [1, 6, 11]
    best_24 = min(ideal_24, key=lambda c: channel_counts.get(c, {'count': 0})['count'])
    
    return {
        'channel_congestion': congestion,
        'recommendations': {
            '2.4GHz': {'recommended': best_24, 'reason': f'Channel {best_24} has lowest congestion'},
            '5GHz': {'recommended': 36, 'reason': 'Less crowded band'}
        }
    }


def calculate_impact(rssi, noise, networks, congestion):
    """Calculate interference impact score"""
    snr = rssi - noise
    
    congested_channels = sum(1 for c in congestion.values() 
                            if c['congestion_level'] in ['HIGH', 'CRITICAL'])
    
    impact_score = congested_channels * 2 + (100 - max(0, snr)) / 20
    
    if impact_score < 2:
        level = 'LOW'
    elif impact_score < 4:
        level = 'MEDIUM'
    elif impact_score < 6:
        level = 'HIGH'
    else:
        level = 'CRITICAL'
    
    return {
        'score': round(impact_score, 1),
        'level': level,
        'snr': snr
    }


def main():
    print("=" * 60)
    print("  Wi-Fi Interference Analyzer (Windows)")
    print("=" * 60)
    print()
    
    print("📡 Scanning networks...")
    networks = scan_networks()
    
    print("📶 Getting connection info...")
    connection = get_current_connection()
    
    print("⚡ Testing latency...")
    latency = test_latency()
    
    if not networks:
        print("  No networks found. Make sure Wi-Fi is enabled.")
        return
    
    signal = connection if connection else {'rssi': -70}
    interference = analyze_interference(networks)
    
    my_channel = connection.get('channel') if connection else None
    my_rssi = connection.get('rssi', -70) if connection else -70
    impact = calculate_impact(my_rssi, -90, networks, interference['channel_congestion'])
    
    print("\n📡 DETECTED NETWORKS")
    print("-" * 60)
    print(f"{'SSID':<25} {'Channel':<10} {'RSSI':<10} {'Band':<10}")
    print()
    for net in sorted(networks, key=lambda x: x['channel']):
        marker = " *" if my_channel and net['channel'] == my_channel else ""
        print(f"{net['ssid']:<25} {net['channel']:<10} {net['rssi']:<10} {net['band']:<10}{marker}")
    
    if my_channel:
        print("\n  * = Your network")
    
    print()
    print("📊 CHANNEL CONGESTION")
    print("-" * 60)
    for ch in sorted(interference['channel_congestion'].keys()):
        data = interference['channel_congestion'][ch]
        level_indicator = '🔴' if data['congestion_level'] == 'HIGH' else \
                         '🟡' if data['congestion_level'] == 'MEDIUM' else '🟢'
        marker = " *" if my_channel and ch == my_channel else ""
        print(f"  Channel {ch}: {data['network_count']} networks {level_indicator} {data['congestion_level']}{marker}")
    
    print()
    print("📶 YOUR CONNECTION")
    print("-" * 60)
    if connection:
        print(f"  SSID: {connection.get('ssid', 'N/A')}")
        print(f"  RSSI: {connection.get('rssi', 'N/A')} dBm ({connection.get('signal_percent', 'N/A')}%)")
        print(f"  Channel: {connection.get('channel', 'N/A')}")
        print(f"  Band: {connection.get('band', 'N/A')}")
    else:
        print("  Could not get connection info")
    
    print()
    print("⚡ PERFORMANCE TEST")
    print("-" * 60)
    if latency.get('latency_avg'):
        print(f"  Latency: {latency['latency_avg']} ms (avg)")
        print(f"  Latency: {latency['latency_min']}-{latency['latency_max']} ms (min-max)")
        print(f"  Jitter: {latency['jitter']} ms")
        print(f"  Packet Loss: {latency['packet_loss']}%")
    else:
        print("  Could not test latency (check internet connection)")
    
    print()
    print("🎯 INTERFERENCE IMPACT")
    print("-" * 60)
    print(f"  Level: {impact['level']}")
    print(f"  Score: {impact['score']}")
    print(f"  SNR: {impact['snr']} dB")
    
    print()
    print("💡 RECOMMENDATIONS")
    print("-" * 60)
    rec_24 = interference['recommendations']['2.4GHz']
    print(f"  → Switch to 2.4GHz Channel {rec_24['recommended']} ({rec_24['reason']})")
    rec_5 = interference['recommendations']['5GHz']
    print(f"  → Consider 5GHz Channel {rec_5['recommended']} ({rec_5['reason']})")
    
    print()
    print("=" * 60)
    print()
    
    return {
        'networks': networks,
        'connection': connection,
        'latency': latency,
        'interference': interference,
        'impact': impact
    }


if __name__ == '__main__':
    main()
