#!/usr/bin/env python3
"""
Correlation Engine
Correlates interference metrics with performance data
"""

import json
from typing import Dict, List
from datetime import datetime, timedelta


class CorrelationEngine:
    def __init__(self):
        self.history = []
        self.correlation_threshold = 0.6
        
    def correlate(self, scan_data: Dict, performance_data: Dict, 
                  interference_data: Dict) -> Dict:
        """Correlate interference with performance impact"""
        
        correlation = {
            'timestamp': datetime.now().isoformat(),
            'interference_impact': self._calculate_impact(scan_data, interference_data),
            'performance_correlation': self._correlate_with_performance(
                interference_data, performance_data
            ),
            'diagnosis': self._generate_diagnosis(interference_data, performance_data),
            'actionable_insights': self._generate_insights(interference_data, performance_data)
        }
        
        self.history.append(correlation)
        
        return correlation
    
    def _calculate_impact(self, scan_data: Dict, interference_data: Dict) -> Dict:
        """Calculate interference impact score"""
        
        impact_factors = {
            'co_channel_score': 0,
            'adjacent_channel_score': 0,
            'congestion_score': 0
        }
        
        co_channel = interference_data.get('co_channel_interference', {})
        if co_channel:
            for ch, data in co_channel.items():
                severity_weights = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
                impact_factors['co_channel_score'] += severity_weights.get(
                    data.get('severity', 'LOW'), 1
                ) * data.get('network_count', 0)
        
        adjacent = interference_data.get('adjacent_channel_interference', {})
        if adjacent:
            impact_factors['adjacent_channel_score'] = len(adjacent)
        
        congestion = interference_data.get('channel_congestion', {})
        for ch, data in congestion.items():
            level_weights = {'EMPTY': 0, 'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
            impact_factors['congestion_score'] += level_weights.get(
                data.get('congestion_level', 'LOW'), 1
            )
        
        total_impact = sum(impact_factors.values())
        
        if total_impact < 3:
            level = 'MINIMAL'
        elif total_impact < 6:
            level = 'LOW'
        elif total_impact < 10:
            level = 'MEDIUM'
        elif total_impact < 15:
            level = 'HIGH'
        else:
            level = 'CRITICAL'
        
        return {
            'score': total_impact,
            'level': level,
            'factors': impact_factors,
            'signal_strength': scan_data.get('rssi'),
            'noise_floor': scan_data.get('noise'),
            'snr': self._calculate_snr(
                scan_data.get('rssi', -100),
                scan_data.get('noise', -100)
            )
        }
    
    def _calculate_snr(self, rssi, noise) -> float:
        """Calculate Signal-to-Noise Ratio"""
        if rssi is None or noise is None:
            return 0
        if noise >= 0:
            noise = -100
        return rssi - noise
    
    def _correlate_with_performance(self, interference_data: Dict, 
                                    performance_data: Dict) -> Dict:
        """Correlate interference with performance metrics"""
        
        correlation = {
            'latency_impact': 'unknown',
            'throughput_impact': 'unknown',
            'stability_impact': 'unknown'
        }
        
        latency = performance_data.get('latency', {})
        if latency:
            avg_latency = latency.get('latency_avg', 0)
            if avg_latency:
                if avg_latency < 20:
                    correlation['latency_impact'] = 'excellent'
                elif avg_latency < 50:
                    correlation['latency_impact'] = 'normal'
                elif avg_latency < 100:
                    correlation['latency_impact'] = 'degraded'
                else:
                    correlation['latency_impact'] = 'poor'
        
        throughput = performance_data.get('throughput', {})
        if throughput:
            mbps = throughput.get('throughput_mbps', 0)
            if mbps:
                if mbps > 100:
                    correlation['throughput_impact'] = 'excellent'
                elif mbps > 50:
                    correlation['throughput_impact'] = 'normal'
                elif mbps > 20:
                    correlation['throughput_impact'] = 'degraded'
                else:
                    correlation['throughput_impact'] = 'poor'
        
        packet_loss = latency.get('packet_loss') if latency else None
        if packet_loss is None or packet_loss == 0:
            correlation['stability_impact'] = 'excellent'
        elif packet_loss < 1:
            correlation['stability_impact'] = 'normal'
        elif packet_loss < 5:
            correlation['stability_impact'] = 'degraded'
        else:
            correlation['stability_impact'] = 'poor'
        
        return correlation
    
    def _generate_diagnosis(self, interference_data: Dict, 
                            performance_data: Dict) -> Dict:
        """Generate diagnosis based on all data"""
        
        diagnosis = {
            'is_slow_due_to_interference': False,
            'primary_cause': None,
            'secondary_causes': [],
            'confidence': 0
        }
        
        impact = interference_data.get('channel_congestion', {})
        critical_channels = [ch for ch, data in impact.items() 
                           if data.get('congestion_level') in ['HIGH', 'CRITICAL']]
        
        co_channel = interference_data.get('co_channel_interference', {})
        high_co_channel = [ch for ch, data in co_channel.items() 
                          if data.get('severity') in ['HIGH', 'CRITICAL']]
        
        if high_co_channel:
            diagnosis['is_slow_due_to_interference'] = True
            diagnosis['primary_cause'] = 'co_channel_interference'
            diagnosis['secondary_causes'].append(f'Channels {high_co_channel} are congested')
            diagnosis['confidence'] = 0.85
        
        if critical_channels:
            diagnosis['is_slow_due_to_interference'] = True
            if not diagnosis['primary_cause']:
                diagnosis['primary_cause'] = 'channel_congestion'
            diagnosis['secondary_causes'].append(
                f'Critical congestion on channels: {critical_channels}'
            )
            diagnosis['confidence'] = max(diagnosis['confidence'], 0.75)
        
        return diagnosis
    
    def _generate_insights(self, interference_data: Dict, 
                          performance_data: Dict) -> List[Dict]:
        """Generate actionable insights"""
        
        insights = []
        
        recommendations = interference_data.get('recommendations', {})
        
        if recommendations.get('2.4GHz', {}).get('recommended'):
            ch = recommendations['2.4GHz']['recommended']
            insights.append({
                'type': 'recommendation',
                'priority': 'high',
                'message': f'Recommended 2.4GHz channel: {ch}',
                'action': f'Switch your AP to channel {ch}'
            })
        
        co_channel = interference_data.get('co_channel_interference', {})
        for ch, data in co_channel.items():
            if data.get('severity') in ['HIGH', 'CRITICAL']:
                count = data.get('network_count', 0)
                insights.append({
                    'type': 'warning',
                    'priority': 'high',
                    'message': f'Channel {ch} has {count} overlapping networks',
                    'action': 'Avoid this channel or switch bands'
                })
        
        throughput = performance_data.get('throughput', {})
        if throughput.get('throughput_mbps'):
            mbps = throughput['throughput_mbps']
            if mbps < 30:
                insights.append({
                    'type': 'performance_alert',
                    'priority': 'medium',
                    'message': f'Throughput is low ({mbps} Mbps)',
                    'action': 'Check interference levels and signal strength'
                })
        
        latency = performance_data.get('latency') or {}
        latency_avg = latency.get('latency_avg')
        if latency_avg is not None and latency_avg > 50:
            insights.append({
                'type': 'performance_alert',
                'priority': 'medium',
                'message': f'High latency detected ({latency_avg:.1f} ms)',
                'action': 'Investigate network congestion'
            })
        
        return insights
    
    def get_trend_analysis(self, duration_minutes: int = 30) -> Dict:
        """Analyze trends from history"""
        
        if len(self.history) < 2:
            return {'error': 'Insufficient data for trend analysis'}
        
        recent = [h for h in self.history 
                 if datetime.fromisoformat(h['timestamp']) > 
                 datetime.now() - timedelta(minutes=duration_minutes)]
        
        if len(recent) < 2:
            return {'error': 'Not enough recent data'}
        
        impact_scores = [h['interference_impact']['score'] for h in recent]
        
        return {
            'data_points': len(recent),
            'impact_trend': 'stable' if max(impact_scores) - min(impact_scores) < 2 
                           else ('improving' if impact_scores[-1] < impact_scores[0] 
                                else 'worsening'),
            'avg_impact': sum(impact_scores) / len(impact_scores),
            'max_impact': max(impact_scores),
            'min_impact': min(impact_scores)
        }


def main():
    engine = CorrelationEngine()
    
    sample_scan = {'rssi': -65, 'noise': -90}
    sample_perf = {
        'latency': {'latency_avg': 35, 'packet_loss': 0.5},
        'throughput': {'throughput_mbps': 45}
    }
    sample_interference = {
        'channel_congestion': {
            6: {'congestion_level': 'HIGH', 'network_count': 5},
            1: {'congestion_level': 'LOW', 'network_count': 2}
        },
        'co_channel_interference': {
            6: {'network_count': 5, 'severity': 'HIGH'}
        },
        'recommendations': {
            '2.4GHz': {'recommended': 11}
        }
    }
    
    result = engine.correlate(sample_scan, sample_perf, sample_interference)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    from datetime import timedelta
    main()
