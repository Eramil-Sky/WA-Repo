#!/usr/bin/env python3
"""
Database Module for Wi-Fi Analyzer
Stores and retrieves analysis history
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional


class AnalyzerDatabase:
    def __init__(self, db_path: str = 'wifi_analyzer.db'):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                rssi INTEGER,
                noise INTEGER,
                snr REAL,
                throughput REAL,
                latency_avg REAL,
                latency_max REAL,
                latency_min REAL,
                packet_loss REAL,
                interference_score REAL,
                congestion_level TEXT,
                data TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS networks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER,
                ssid TEXT,
                bssid TEXT,
                channel INTEGER,
                rssi INTEGER,
                band TEXT,
                FOREIGN KEY (scan_id) REFERENCES scans(id)
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp ON scans(timestamp)
        ''')
        
        conn.commit()
        conn.close()
    
    def save_scan(self, scan_data: Dict) -> int:
        """Save scan data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO scans (timestamp, rssi, noise, snr, throughput, 
                             latency_avg, latency_max, latency_min, packet_loss,
                             interference_score, congestion_level, data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            scan_data.get('timestamp', datetime.now().isoformat()),
            scan_data.get('rssi'),
            scan_data.get('noise'),
            scan_data.get('snr'),
            scan_data.get('throughput'),
            scan_data.get('latency_avg'),
            scan_data.get('latency_max'),
            scan_data.get('latency_min'),
            scan_data.get('packet_loss'),
            scan_data.get('interference_score'),
            scan_data.get('congestion_level'),
            json.dumps(scan_data.get('raw_data', {}))
        ))
        
        scan_id = cursor.lastrowid
        
        for network in scan_data.get('networks', []):
            cursor.execute('''
                INSERT INTO networks (scan_id, ssid, bssid, channel, rssi, band)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                scan_id,
                network.get('ssid'),
                network.get('bssid'),
                network.get('channel'),
                network.get('rssi'),
                network.get('band')
            ))
        
        conn.commit()
        conn.close()
        
        return scan_id
    
    def get_recent_scans(self, limit: int = 100) -> List[Dict]:
        """Get recent scan history"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM scans 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        scans = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return scans
    
    def get_scan_networks(self, scan_id: int) -> List[Dict]:
        """Get networks for a specific scan"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM networks WHERE scan_id = ?
        ''', (scan_id,))
        
        networks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return networks
    
    def get_channel_stats(self, hours: int = 24) -> Dict:
        """Get channel statistics over time"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT channel, COUNT(*) as count, AVG(rssi) as avg_rssi
            FROM networks n
            JOIN scans s ON n.scan_id = s.id
            WHERE s.timestamp > datetime('now', '-' || ? || ' hours')
            GROUP BY channel
            ORDER BY count DESC
        ''', (hours,))
        
        stats = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return stats
    
    def get_performance_trends(self, hours: int = 24) -> Dict:
        """Get performance trends over time"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                timestamp,
                throughput,
                latency_avg,
                packet_loss,
                interference_score
            FROM scans
            WHERE timestamp > datetime('now', '-' || ? || ' hours')
            ORDER BY timestamp ASC
        ''', (hours,))
        
        trends = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {
            'data_points': len(trends),
            'trends': trends
        }
    
    def clear_old_data(self, days: int = 30):
        """Clear data older than specified days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM networks 
            WHERE scan_id IN (
                SELECT id FROM scans 
                WHERE timestamp < datetime('now', '-' || ? || ' days')
            )
        ''', (days,))
        
        cursor.execute('''
            DELETE FROM scans 
            WHERE timestamp < datetime('now', '-' || ? || ' days')
        ''', (days,))
        
        conn.commit()
        conn.close()


def main():
    db = AnalyzerDatabase()
    
    sample_scan = {
        'timestamp': datetime.now().isoformat(),
        'rssi': -65,
        'noise': -90,
        'snr': 25,
        'throughput': 75.5,
        'latency_avg': 25.3,
        'latency_max': 45.2,
        'latency_min': 15.1,
        'packet_loss': 0.5,
        'interference_score': 3.2,
        'congestion_level': 'MEDIUM',
        'networks': [
            {'ssid': 'Network1', 'channel': 6, 'rssi': -60, 'band': '2.4GHz'},
            {'ssid': 'Network2', 'channel': 6, 'rssi': -65, 'band': '2.4GHz'},
        ]
    }
    
    scan_id = db.save_scan(sample_scan)
    print(f"Saved scan with ID: {scan_id}")
    
    scans = db.get_recent_scans(5)
    print(f"Retrieved {len(scans)} recent scans")
    
    stats = db.get_channel_stats(24)
    print(f"Channel stats: {stats}")


if __name__ == '__main__':
    main()
