#!/usr/bin/env python3
"""
Wi-Fi Interference Detection Engine
Detects co-channel, adjacent channel, and calculates interference scores
"""

import json
from typing import List, Dict
from collections import defaultdict


class InterferenceDetector:
    CHANNEL_2_4GHZ_WIDTH = {
        1: (2401, 2423),
        2: (2406, 2428),
        3: (2411, 2433),
        4: (2416, 2438),
        5: (2421, 2443),
        6: (2426, 2448),
        7: (2431, 2453),
        8: (2436, 2458),
        9: (2441, 2463),
        10: (2446, 2468),
        11: (2451, 2473),
        12: (2456, 2478),
        13: (2461, 2483),
        14: (2473, 2495)
    }
    
    def __init__(self):
        self.networks = []
        self.analysis_results = {}
        
    def analyze(self, networks: List[Dict]) -> Dict:
        """Main analysis method"""
        self.networks = networks
        
        return {
            'co_channel_interference': self._detect_co_channel(),
            'adjacent_channel_interference': self._detect_adjacent_channel(),
            'channel_congestion': self._analyze_channel_congestion(),
            'recommendations': self._generate_recommendations()
        }
    
    def _detect_co_channel(self) -> Dict:
        """Detect interference from networks on same channel"""
        channel_networks = defaultdict(list)
        
        for net in self.networks:
            if 'channel' in net and net['channel']:
                rssi = net.get('rssi', -100)
                if rssi > -90 and rssi < 0:
                    channel_networks[net['channel']].append(net)
        
        co_channel_results = {}
        
        for channel, nets in channel_networks.items():
            if len(nets) > 1:
                avg_rssi = sum(n.get('rssi', -100) for n in nets) / len(nets)
                interference_score = len(nets) * (avg_rssi + 100) / 100
                
                co_channel_results[channel] = {
                    'network_count': len(nets),
                    'networks': [{'ssid': n.get('ssid', 'Hidden'), 
                                  'rssi': n.get('rssi')} for n in nets],
                    'avg_rssi': round(avg_rssi, 2),
                    'interference_score': round(interference_score, 2),
                    'severity': self._score_to_severity(interference_score)
                }
        
        return co_channel_results
    
    def _detect_adjacent_channel(self) -> Dict:
        """Detect adjacent channel interference (2.4GHz overlap)"""
        adjacent_results = {}
        
        for net in self.networks:
            if net.get('band') != '2.4GHz' or not net.get('channel'):
                continue
                
            channel = net['channel']
            if channel not in self.CHANNEL_2_4GHZ_WIDTH:
                continue
                
            net_range = self.CHANNEL_2_4GHZ_WIDTH[channel]
            overlapping = []
            
            for other in self.networks:
                if other == net or not other.get('channel'):
                    continue
                if other.get('band') != '2.4GHz':
                    continue
                if other['channel'] not in self.CHANNEL_2_4GHZ_WIDTH:
                    continue
                
                other_range = self.CHANNEL_2_4GHZ_WIDTH[other['channel']]
                
                if self._ranges_overlap(net_range, other_range):
                    overlapping.append({
                        'ssid': other.get('ssid', 'Hidden'),
                        'channel': other['channel'],
                        'rssi': other.get('rssi')
                    })
            
            if overlapping:
                adjacent_results[f"{net.get('ssid', 'Unknown')}_ch{channel}"] = {
                    'channel': channel,
                    'overlapping_networks': overlapping,
                    'overlap_count': len(overlapping),
                    'severity': self._calculate_adjacent_severity(len(overlapping))
                }
        
        return adjacent_results
    
    def _ranges_overlap(self, range1: tuple, range2: tuple) -> bool:
        """Check if two frequency ranges overlap"""
        return range1[0] <= range2[1] and range2[0] <= range1[1]
    
    def _analyze_channel_congestion(self) -> Dict:
        """Calculate congestion levels per channel"""
        channel_stats = defaultdict(lambda: {'count': 0, 'rssi_sum': 0, 'networks': []})
        
        for net in self.networks:
            if 'channel' in net and net['channel']:
                rssi = net.get('rssi', -100)
                if rssi <= -90 or rssi == -1:
                    continue
                ch = net['channel']
                channel_stats[ch]['count'] += 1
                channel_stats[ch]['rssi_sum'] += rssi
                channel_stats[ch]['networks'].append(net.get('ssid', 'Hidden'))
        
        congestion = {}
        for ch, stats in channel_stats.items():
            if stats['count'] > 0:
                avg_rssi = stats['rssi_sum'] / stats['count']
            else:
                avg_rssi = -100
            
            congestion[ch] = {
                'network_count': stats['count'],
                'avg_rssi': round(avg_rssi, 2),
                'networks': stats['networks'],
                'congestion_level': self._calc_congestion_level(stats['count'], avg_rssi)
            }
        
        return congestion
    
    def _calc_congestion_level(self, count: int, avg_rssi: int) -> str:
        """Calculate congestion level"""
        if count == 0:
            return 'EMPTY'
        elif count <= 2:
            return 'LOW'
        elif count <= 4:
            return 'MEDIUM' if avg_rssi > -70 else 'LOW'
        elif count <= 6:
            return 'HIGH' if avg_rssi > -65 else 'MEDIUM'
        else:
            return 'CRITICAL'
    
    def _score_to_severity(self, score: float) -> str:
        """Convert interference score to severity"""
        if score < 1:
            return 'LOW'
        elif score < 2:
            return 'MEDIUM'
        elif score < 3:
            return 'HIGH'
        else:
            return 'CRITICAL'
    
    def _calculate_adjacent_severity(self, overlap_count: int) -> str:
        """Calculate adjacent channel interference severity"""
        if overlap_count <= 1:
            return 'LOW'
        elif overlap_count <= 3:
            return 'MEDIUM'
        elif overlap_count <= 5:
            return 'HIGH'
        else:
            return 'CRITICAL'
    
    def _generate_recommendations(self) -> Dict:
        """Generate channel recommendations"""
        recommendations = {
            '2.4GHz': self._recommend_2_4ghz_channel(),
            '5GHz': self._recommend_5ghz_channel()
        }
        return recommendations
    
    def _recommend_2_4ghz_channel(self) -> Dict:
        """Recommend best 2.4GHz channel"""
        ideal_channels = [1, 6, 11]
        
        channel_stats = defaultdict(lambda: {'count': 0, 'total_rssi': 0})
        
        for net in self.networks:
            if net.get('band') != '2.4GHz' or not net.get('channel'):
                continue
            rssi = net.get('rssi', -100)
            if rssi <= -90 or rssi == -1:
                continue
            ch = net['channel']
            channel_stats[ch]['count'] += 1
            channel_stats[ch]['total_rssi'] += rssi
        
        best_channel = None
        best_score = float('inf')
        
        for ch in ideal_channels:
            stats = channel_stats.get(ch, {'count': 0, 'total_rssi': 0})
            if stats['count'] > 0:
                score = stats['count'] * 10 + (stats['total_rssi'] / stats['count'] + 100) / 10
            else:
                score = 0
            if score < best_score:
                best_score = score
                best_channel = ch
        
        return {
            'recommended': best_channel,
            'reason': self._get_recommendation_reason(best_channel, channel_stats),
            'alternative_channels': [c for c in ideal_channels if c != best_channel]
        }
    
    def _recommend_5ghz_channel(self) -> Dict:
        """Recommend best 5GHz channel"""
        channel_stats = defaultdict(lambda: {'count': 0})
        
        for net in self.networks:
            if net.get('band') != '5GHz' or not net.get('channel'):
                continue
            channel_stats[net['channel']]['count'] += 1
        
        least_congested = min(channel_stats.keys(), 
                             key=lambda x: channel_stats[x]['count'],
                             default=None)
        
        return {
            'recommended': least_congested,
            'reason': 'Least congested 5GHz channel' if least_congested else 'No 5GHz networks detected',
            'available_channels': sorted(channel_stats.keys())
        }
    
    def _get_recommendation_reason(self, channel, stats: Dict) -> str:
        """Get reason for recommendation"""
        if not channel:
            return 'No networks detected'
        
        count = stats.get(channel, {'count': 0})['count']
        
        if count == 0:
            return f'Channel {channel} is clear'
        else:
            return f'Channel {channel} has only {count} network(s)'


def main():
    detector = InterferenceDetector()
    
    sample_networks = [
        {'ssid': 'Network1', 'channel': 6, 'rssi': -60, 'band': '2.4GHz'},
        {'ssid': 'Network2', 'channel': 6, 'rssi': -65, 'band': '2.4GHz'},
        {'ssid': 'Network3', 'channel': 6, 'rssi': -70, 'band': '2.4GHz'},
        {'ssid': 'Network4', 'channel': 1, 'rssi': -55, 'band': '2.4GHz'},
        {'ssid': 'Network5', 'channel': 11, 'rssi': -60, 'band': '2.4GHz'},
        {'ssid': 'Network6', 'channel': 5, 'rssi': -65, 'band': '2.4GHz'},
        {'ssid': 'Network7', 'channel': 36, 'rssi': -50, 'band': '5GHz'},
    ]
    
    results = detector.analyze(sample_networks)
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
