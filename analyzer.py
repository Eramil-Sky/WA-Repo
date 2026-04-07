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
        self._oui_cache = {}
        self._load_oui_database()
    
    def _load_oui_database(self):
        """Load OUI database for manufacturer lookup"""
        oui_file = '/tmp/oui_database.txt'
        
        if os.path.exists(oui_file):
            return
        
        common_ouis = {
            '00:00:00': 'Unknown',
            '00:03:93': 'Apple',
            '00:05:69': 'VMware',
            '00:0C:29': 'VMware',
            '00:0D:3A': 'Microsoft',
            '00:11:32': 'Synology',
            '00:13:3C': 'Belkin',
            '00:14:BF': 'Linksys',
            '00:17:88': 'Philips',
            '00:1A:22': 'Cisco',
            '00:1B:63': 'Apple',
            '00:1C:B3': 'Apple',
            '00:1D:4F': 'Apple',
            '00:1E:52': 'Apple',
            '00:1E:C2': 'Apple',
            '00:1F:5B': 'Apple',
            '00:1F:F3': 'Apple',
            '00:21:E9': 'Apple',
            '00:22:41': 'Apple',
            '00:23:12': 'Apple',
            '00:23:32': 'Apple',
            '00:23:6C': 'Apple',
            '00:23:DF': 'Apple',
            '00:24:36': 'Apple',
            '00:25:00': 'Apple',
            '00:25:4B': 'Apple',
            '00:25:BC': 'Apple',
            '00:26:08': 'Apple',
            '00:26:4A': 'Apple',
            '00:26:B0': 'Apple',
            '00:26:BB': 'Apple',
            '00:30:65': 'Apple',
            '00:3E:E1': 'Apple',
            '00:50:56': 'VMware',
            '00:50:F2': 'Microsoft',
            '00:60:2F': 'Cisco',
            '00:0F:B5': 'Netgear',
            '00:14:6C': 'Netgear',
            '00:18:4D': 'Netgear',
            '00:1B:2F': 'Netgear',
            '00:1E:2A': 'Netgear',
            '00:1F:33': 'Netgear',
            '00:22:3F': 'Netgear',
            '00:24:B2': 'Netgear',
            '00:26:F2': 'Netgear',
            '08:36:C9': 'TP-Link',
            '10:FE:ED': 'TP-Link',
            '14:CC:20': 'TP-Link',
            '14:CF:92': 'TP-Link',
            '18:A6:F7': 'TP-Link',
            '1C:3B:F3': 'TP-Link',
            '30:B5:C2': 'TP-Link',
            '50:C7:BF': 'TP-Link',
            '54:C8:0F': 'TP-Link',
            '5C:63:BF': 'TP-Link',
            '5C:89:9A': 'TP-Link',
            '64:66:B3': 'TP-Link',
            '6C:5A:B0': 'TP-Link',
            '78:A1:06': 'TP-Link',
            '84:16:F9': 'TP-Link',
            '88:25:93': 'TP-Link',
            '90:F6:52': 'TP-Link',
            '94:0C:6D': 'TP-Link',
            '98:DA:C4': 'TP-Link',
            'A0:F3:C1': 'TP-Link',
            'AC:84:C6': 'TP-Link',
            'B0:4E:26': 'TP-Link',
            'B0:95:75': 'TP-Link',
            'B0:BE:76': 'TP-Link',
            'C0:25:E9': 'TP-Link',
            'C0:4A:00': 'TP-Link',
            'C4:6E:1F': 'TP-Link',
            'C4:E9:84': 'TP-Link',
            'CC:32:E5': 'TP-Link',
            'D4:6E:0E': 'TP-Link',
            'D8:07:B6': 'TP-Link',
            'D8:47:32': 'TP-Link',
            'DC:2B:2A': 'TP-Link',
            'E0:05:C5': 'TP-Link',
            'E8:94:F6': 'TP-Link',
            'EC:08:6B': 'TP-Link',
            'EC:17:2F': 'TP-Link',
            'F0:F3:36': 'TP-Link',
            'F4:EC:38': 'TP-Link',
            'F4:F2:6D': 'TP-Link',
            'F8:1A:67': 'TP-Link',
            'F8:D1:11': 'TP-Link',
            '00:1A:2B': 'Asus',
            '00:1D:60': 'Asus',
            '00:1E:8C': 'Asus',
            '00:22:15': 'Asus',
            '00:23:54': 'Asus',
            '00:24:8C': 'Asus',
            '00:26:18': 'Asus',
            '08:60:6E': 'Asus',
            '10:BF:48': 'Asus',
            '14:DA:E9': 'Asus',
            '14:DD:A9': 'Asus',
            '1C:87:2C': 'Asus',
            '1C:B7:2C': 'Asus',
            '20:CF:30': 'Asus',
            '2C:4D:54': 'Asus',
            '2C:56:DC': 'Asus',
            '30:85:A9': 'Asus',
            '38:D5:47': 'Asus',
            '3C:97:0E': 'Asus',
            '40:16:7E': 'Asus',
            '48:5B:39': 'Asus',
            '4C:ED:FB': 'Asus',
            '50:46:5D': 'Asus',
            '54:04:A6': 'Asus',
            '60:45:CB': 'Asus',
            '74:D0:2B': 'Asus',
            '7C:87:CE': 'Asus',
            'AC:22:0B': 'Asus',
            'AC:9E:17': 'Asus',
            'B0:6E:BF': 'Asus',
            'BC:AE:C5': 'Asus',
            'BC:EE:7B': 'Asus',
            'C8:60:00': 'Asus',
            'D8:50:E6': 'Asus',
            'F4:6D:04': 'Asus',
            'F8:32:E4': 'Asus',
            '04:D4:C4': 'Merry', 
            '00:24:01': 'D-Link',
            '00:1B:11': 'D-Link',
            '00:1C:F0': 'D-Link',
            '00:1E:58': 'D-Link',
            '00:21:91': 'D-Link',
            '00:22:B0': 'D-Link',
            '00:26:5A': 'D-Link',
            '00:50:BA': 'D-Link',
            '14:D6:4D': 'D-Link',
            '1C:7E:E5': 'D-Link',
            '28:10:7B': 'D-Link',
            '34:08:04': 'D-Link',
            '5C:D9:98': 'D-Link',
            '78:54:2E': 'D-Link',
            '90:94:E4': 'D-Link',
            '9C:D6:43': 'D-Link',
            'A0:AB:1B': 'D-Link',
            'AC:F1:DF': 'D-Link',
            'B8:A3:86': 'D-Link',
            'BC:F6:85': 'D-Link',
            'C0:A0:BB': 'D-Link',
            'C4:A8:1D': 'D-Link',
            'CC:B2:55': 'D-Link',
            'E0:1C:FC': 'D-Link',
            'E4:6F:13': 'D-Link',
            'EC:22:80': 'D-Link',
            'F0:7D:68': 'D-Link',
            'FC:75:16': 'D-Link',
            '00:26:5B': 'TRENDnet',
            '00:14:D1': 'TRENDnet',
            '00:11:32': 'Synology',
            '00:0B:6B': 'Cisco-Linksys',
            '00:04:4B': 'Nvidia',
            '18:67:B0': 'Samsung',
            '20:64:32': 'Samsung',
            '28:98:7B': 'Samsung',
            '3C:5A:B4': 'Samsung',
            '40:0E:85': 'Samsung',
            '50:01:BB': 'Samsung',
            '50:A4:C8': 'Samsung',
            '5C:0A:5B': 'Samsung',
            '5C:3C:27': 'Samsung',
            '64:77:91': 'Samsung',
            '68:27:37': 'Samsung',
            '74:45:8A': 'Samsung',
            '78:25:AD': 'Samsung',
            '78:9F:70': 'Samsung',
            '80:65:6D': 'Samsung',
            '84:11:9E': 'Samsung',
            '84:25:DB': 'Samsung',
            '88:32:9B': 'Samsung',
            '8C:77:12': 'Samsung',
            '90:18:7C': 'Samsung',
            '94:35:0A': 'Samsung',
            '94:B1:0A': 'Samsung',
            '9C:02:98': 'Samsung',
            '9C:52:F8': 'Samsung',
            '9C:65:B0': 'Samsung',
            'A0:07:98': 'Samsung',
            'A0:0B:BA': 'Samsung',
            'A0:9F:10': 'Samsung',
            'A4:07:B6': 'Samsung',
            'A4:8C:DB': 'Samsung',
            'A8:06:00': 'Samsung',
            'AC:36:13': 'Samsung',
            'AC:5A:14': 'Samsung',
            'B0:47:BF': 'Samsung',
            'B0:72:BF': 'Samsung',
            'B0:C5:59': 'Samsung',
            'B4:3A:28': 'Samsung',
            'B4:79:A7': 'Samsung',
            'B8:5A:73': 'Samsung',
            'B8:D9:CE': 'Samsung',
            'BC:14:01': 'Samsung',
            'BC:20:A4': 'Samsung',
            'BC:44:86': 'Samsung',
            'BC:79:AD': 'Samsung',
            'C0:BD:D1': 'Samsung',
            'C4:57:6E': 'Samsung',
            'C8:38:70': 'Samsung',
            'C8:7E:75': 'Samsung',
            'CC:07:AB': 'Samsung',
            'D0:22:BE': 'Samsung',
            'D0:59:E4': 'Samsung',
            'D0:87:E2': 'Samsung',
            'D0:C1:B1': 'Samsung',
            'D0:DF:C7': 'Samsung',
            'D4:87:D8': 'Samsung',
            'D8:90:E8': 'Samsung',
            'D8:C7:71': 'Samsung',
            'DC:66:72': 'Samsung',
            'E0:5F:45': 'Samsung',
            'E0:B9:4D': 'Samsung',
            'E4:12:1D': 'Samsung',
            'E4:58:B8': 'Samsung',
            'E4:7C:F9': 'Samsung',
            'E4:92:FB': 'Samsung',
            'E4:E0:C5': 'Samsung',
            'E8:4E:CE': 'Samsung',
            'EC:1F:72': 'Samsung',
            'EC:9B:F3': 'Samsung',
            'F0:25:B7': 'Samsung',
            'F0:5A:09': 'Samsung',
            'F0:72:8C': 'Samsung',
            'F0:E7:7E': 'Samsung',
            'F4:09:D8': 'Samsung',
            'F4:42:8F': 'Samsung',
            'F4:8B:32': 'Samsung',
            'F4:C7:14': 'Samsung',
            'F8:04:2E': 'Samsung',
            'F8:77:B8': 'Samsung',
            'F8:77:C5': 'Samsung',
            'FC:19:10': 'Samsung',
            'FC:8F:C4': 'Samsung',
            '28:6A:BA': 'Huawei',
            '34:00:A3': 'Huawei',
            '34:29:12': 'Huawei',
            '38:BC:01': 'Huawei',
            '3C:47:11': 'Huawei',
            '40:4D:8E': 'Huawei',
            '44:55:B1': 'Huawei',
            '48:3C:0C': 'Huawei',
            '48:62:76': 'Huawei',
            '4C:8B:EF': 'Huawei',
            '50:01:6B': 'Huawei',
            '50:A7:2B': 'Huawei',
            '54:25:EA': 'Huawei',
            '58:1F:28': 'Huawei',
            '5C:4C:A9': 'Huawei',
            '60:DE:44': 'Huawei',
            '60:E7:01': 'Huawei',
            '64:16:F0': 'Huawei',
            '68:89:C1': 'Huawei',
            '6C:B7:49': 'Huawei',
            '70:54:F5': 'Huawei',
            '70:72:3C': 'Huawei',
            '74:59:09': 'Huawei',
            '78:D7:5F': 'Huawei',
            '7C:60:97': 'Huawei',
            '80:41:26': 'Huawei',
            '80:B6:86': 'Huawei',
            '84:46:FE': 'Huawei',
            '88:3D:24': 'Huawei',
            '88:53:95': 'Huawei',
            '8C:34:FD': 'Huawei',
            '90:67:1C': 'Huawei',
            '90:B0:ED': 'Huawei',
            '94:04:9C': 'Huawei',
            '98:46:0A': 'Huawei',
            '9C:37:F4': 'Huawei',
            '9C:5C:8E': 'Huawei',
            '9C:E3:3F': 'Huawei',
            'A0:08:6F': 'Huawei',
            'A4:71:74': 'Huawei',
            'A4:99:47': 'Huawei',
            'A8:C8:3A': 'Huawei',
            'AC:4E:91': 'Huawei',
            'AC:61:EA': 'Huawei',
            'AC:85:3D': 'Huawei',
            'AC:E2:15': 'Huawei',
            'B0:5B:67': 'Huawei',
            'B4:15:13': 'Huawei',
            'B8:3E:59': 'Huawei',
            'B8:BC:1B': 'Huawei',
            'BC:25:E0': 'Huawei',
            'BC:62:0E': 'Huawei',
            'C0:1A:DA': 'Huawei',
            'C4:07:2F': 'Huawei',
            'C4:86:E9': 'Huawei',
            'C8:0D:83': 'Huawei',
            'CC:96:A0': 'Huawei',
            'D0:65:CA': 'Huawei',
            'D0:7A:B5': 'Huawei',
            'D0:BA:E4': 'Huawei',
            'D4:61:FE': 'Huawei',
            'D4:6A:A8': 'Huawei',
            'D4:6E:5C': 'Huawei',
            'D4:87:D8': 'Huawei',
            'DC:D2:FC': 'Huawei',
            'E0:24:7F': 'Huawei',
            'E0:97:96': 'Huawei',
            'E4:35:C8': 'Huawei',
            'E4:68:A3': 'Huawei',
            'E8:08:8B': 'Huawei',
            'E8:CD:2D': 'Huawei',
            'EC:23:3D': 'Huawei',
            'EC:38:8F': 'Huawei',
            'EC:CB:30': 'Huawei',
            'F0:43:47': 'Huawei',
            'F4:55:9C': 'Huawei',
            'F4:C7:73': 'Huawei',
            'F4:F5:DB': 'Huawei',
            'F8:01:13': 'Huawei',
            'FC:48:EF': 'Huawei',
            '30:AE:A4': 'ESP',
            '30:83:98': 'ESP',
            '3C:61:05': 'ESP',
            '3C:71:BF': 'ESP',
            '4C:11:AE': 'ESP',
            '5C:CF:7F': 'ESP',
            '60:01:94': 'ESP',
            '68:C6:3A': 'ESP',
            '70:03:9F': 'ESP',
            '7C:9E:BD': 'ESP',
            '80:7D:3A': 'ESP',
            '80:7E:5F': 'ESP',
            '84:0D:8E': 'ESP',
            '84:CC:A8': 'ESP',
            '84:F3:EB': 'ESP',
            '8C:AA:B5': 'ESP',
            '90:97:D5': 'ESP',
            '94:B9:7E': 'ESP',
            '98:CD:AC': 'ESP',
            '98:F4:AB': 'ESP',
            'A0:20:A6': 'ESP',
            'A4:7B:9D': 'ESP',
            'A4:CF:12': 'ESP',
            'AC:67:B2': 'ESP',
            'AC:D0:74': 'ESP',
            'B4:E6:2D': 'ESP',
            'BC:DD:C2': 'ESP',
            'C4:4F:33': 'ESP',
            'C8:2B:96': 'ESP',
            'CC:50:E3': 'ESP',
            'D8:A0:1D': 'ESP',
            'D8:BF:C0': 'ESP',
            'DC:4F:22': 'ESP',
            'EC:FA:BC': 'ESP',
            'F0:08:D1': 'ESP',
            'F4:CF:A2': 'ESP',
            'F8:F0:82': 'ESP',
            'B4:A7:C6': 'Realtek',
            '00:E0:4C': 'Realtek',
            '00:04:5A': 'Realtek',
            '00:1A:A0': 'Realtek',
            '20:CF:30': 'Asus',
            'DC:2B:2A': 'TP-Link',
            '48:F8:B3': 'Intel',
            '3C:A9:F4': 'Intel',
            '00:1E:67': 'Intel',
            '00:1F:3B': 'Intel',
            '00:20:E0': 'Intel',
            '00:22:FA': 'Intel',
            '00:24:D6': 'Intel',
            '00:24:D7': 'Intel',
            '00:26:C6': 'Intel',
            '00:26:C7': 'Intel',
            '04:7B:9D': 'Intel',
            '08:D4:2B': 'Intel',
            '0C:54:15': 'Intel',
            '10:02:B5': 'Intel',
            '18:3D:A2': 'Intel',
            '1C:4B:D6': 'Intel',
            '1C:C0:18': 'Intel',
            '20:79:18': 'Intel',
            '24:0A:64': 'Intel',
            '28:C6:3F': 'Intel',
            '2C:D0:5A': 'Intel',
            '34:02:86': 'Intel',
            '34:13:E8': 'Intel',
            '34:E6:AD': 'Intel',
            '38:DE:AD': 'Intel',
            '3C:97:0E': 'Asus',
            '3C:DC:BC': 'HP',
            '00:1A:4B': 'HP',
            '00:21:5A': 'HP',
            '00:22:64': 'HP',
            '00:23:7D': 'HP',
            '00:24:81': 'HP',
            '00:25:B3': 'HP',
            '00:26:55': 'HP',
            '00:26:F1': 'HP',
            '08:2E:5F': 'HP',
            '10:1F:74': 'HP',
            '10:60:4B': 'HP',
            '14:02:EC': 'HP',
            '14:58:D0': 'HP',
            '18:A9:9B': 'HP',
            '1C:98:EC': 'HP',
            '1C:C1:DE': 'HP',
            '20:67:7C': 'HP',
            '24:BE:05': 'HP',
            '28:92:4A': 'HP',
            '28:80:23': 'HP',
            '2C:27:D7': 'HP',
            '2C:41:38': 'HP',
            '2C:44:FD': 'HP',
            '2C:59:E5': 'HP',
            '30:8D:99': 'HP',
            '30:E1:71': 'HP',
            '34:64:A9': 'HP',
            '38:63:BB': 'HP',
            '38:EA:A7': 'HP',
            '3C:4A:92': 'HP',
            '3C:D9:1B': 'HP',
            '40:B0:34': 'HP',
            '40:B9:3C': 'HP',
            '44:1E:A1': 'HP',
            '44:31:92': 'HP',
            '4C:39:09': 'HP',
            '50:65:F3': 'HP',
            '54:EE:75': 'HP',
            '58:20:B1': 'HP',
            '5C:B9:01': 'HP',
            '5C:E0:C5': 'HP',
            '60:9F:C2': 'HP',
            '60:BE:B4': 'HP',
            '64:51:06': 'HP',
            '64:8D:09': 'HP',
            '68:B5:99': 'HP',
            '6C:3B:E5': 'HP',
            '70:10:6F': 'HP',
            '70:5A:0F': 'HP',
            '70:85:C2': 'HP',
            '74:46:A0': 'HP',
            '78:AC:C0': 'HP',
            '78:E3:B5': 'HP',
            '78:E7:D1': 'HP',
            '7C:11:BE': 'HP',
            '80:C1:6E': 'HP',
            '84:34:97': 'HP',
            '84:A4:66': 'HP',
            '88:51:FB': 'HP',
            '8C:DC:D4': 'HP',
            '94:57:A5': 'HP',
            '98:4B:E1': 'HP',
            '98:E7:F4': 'HP',
            '9C:8E:99': 'HP',
            '9C:B6:54': 'HP',
            'A0:1D:48': 'HP',
            'A0:2B:B8': 'HP',
            'A0:48:1C': 'HP',
            'A0:8C:FD': 'HP',
            'A4:5D:36': 'HP',
            'A8:20:66': 'Apple',
            'AC:87:A3': 'HP',
            'AC:BC:32': 'HP',
            'B0:5A:DA': 'HP',
            'B0:6E:BF': 'Asus',
            'B4:39:D6': 'HP',
            'B4:99:BA': 'HP',
            'B4:B5:2F': 'HP',
            'B8:AF:67': 'HP',
            'BC:EA:FA': 'HP',
            'C0:91:34': 'HP',
            'C4:34:6B': 'HP',
            'C8:B5:AD': 'HP',
            'C8:CB:B8': 'HP',
            'CC:3D:82': 'HP',
            'D0:7E:28': 'HP',
            'D0:BF:9C': 'HP',
            'D4:85:64': 'HP',
            'D4:C9:EF': 'HP',
            'D8:9D:67': 'HP',
            'D8:D3:85': 'HP',
            'DC:4A:3E': 'HP',
            'DC:53:60': 'HP',
            'E0:07:1B': 'HP',
            'E0:D5:5E': 'HP',
            'E4:11:5B': 'HP',
            'E4:A4:71': 'HP',
            'E8:39:35': 'HP',
            'E8:F7:24': 'HP',
            'EC:8E:B5': 'HP',
            'EC:9A:74': 'HP',
            'F0:03:8C': 'HP',
            'F0:62:81': 'HP',
            'F0:92:1C': 'HP',
            'F4:03:43': 'HP',
            'F4:CE:46': 'HP',
            'F4:E9:75': 'HP',
            'F8:BC:12': 'HP',
            'F8:CA:B8': 'HP',
            'F8:D1:11': 'TP-Link',
            '00:04:5A': 'Dell',
            '00:06:5B': 'Dell',
            '00:08:74': 'Dell',
            '00:0B:DB': 'Dell',
            '00:0D:56': 'Dell',
            '00:0F:1F': 'Dell',
            '00:11:43': 'Dell',
            '00:12:3F': 'Dell',
            '00:13:72': 'Dell',
            '00:14:22': 'Dell',
            '00:15:C5': 'Dell',
            '00:16:F0': 'Dell',
            '00:18:8B': 'Dell',
            '00:19:B9': 'Dell',
            '00:1A:A0': 'Realtek',
            '00:1C:23': 'Dell',
            '00:1D:09': 'Dell',
            '00:1E:4F': 'Dell',
            '00:1E:C9': 'Dell',
            '00:21:70': 'Dell',
            '00:21:9B': 'Dell',
            '00:22:19': 'Dell',
            '00:23:AE': 'Dell',
            '00:24:E8': 'Dell',
            '00:25:64': 'Dell',
            '00:26:B9': 'Dell',
            '00:40:45': 'Dell',
            '08:00:1B': 'Dell',
            '10:1F:74': 'HP',
            '14:18:77': 'Dell',
            '14:58:D0': 'HP',
            '14:9E:CF': 'Dell',
            '14:B3:1F': 'Dell',
            '14:FE:B5': 'Dell',
            '18:03:73': 'Dell',
            '18:66:DA': 'Dell',
            '18:DB:F2': 'Dell',
            '18:FB:7B': 'Dell',
            '1C:40:24': 'Dell',
            '20:47:47': 'Dell',
            '24:6E:96': 'Dell',
            '28:F1:0E': 'Dell',
            '34:17:EB': 'Dell',
            '34:E6:D7': 'Dell',
            '34:FD:6A': 'Dell',
            '38:BA:F8': 'Dell',
            '3C:D9:1B': 'HP',
            '44:A8:85': 'Dell',
            '48:4D:7E': 'HP',
            '4C:76:25': 'Dell',
            '4C:80:93': 'Dell',
            '50:9A:4C': 'Dell',
            '54:9F:35': 'Dell',
            '58:94:6B': 'Dell',
            '5C:26:0A': 'Dell',
            '5C:F9:DD': 'Dell',
            '64:00:6A': 'Dell',
            '68:05:CA': 'Dell',
            '6C:F0:49': 'Dell',
            '70:5C:AD': 'Dell',
            '74:86:7A': 'Dell',
            '74:E6:E2': 'Dell',
            '78:2B:CB': 'Dell',
            '78:45:C4': 'Dell',
            '78:AC:C0': 'HP',
            '7C:5C:F8': 'Dell',
            '7C:5F:67': 'Dell',
            '80:18:A7': 'Dell',
            '80:CE:62': 'Dell',
            '84:2B:2B': 'Dell',
            '84:7B:EB': 'Dell',
            '84:8F:69': 'Dell',
            '88:88:3F': 'Dell',
            '88:AE:1D': 'Dell',
            '8C:EC:4B': 'Dell',
            '90:B1:1C': 'Dell',
            '94:57:A5': 'HP',
            '98:90:96': 'Dell',
            '9C:4F:DA': 'Dell',
            '9C:F3:87': 'Dell',
            'A4:1F:72': 'Dell',
            'A4:BA:DB': 'Dell',
            'A8:6D:AA': 'Dell',
            'AC:22:0B': 'Asus',
            'B0:83:FE': 'Dell',
            'B4:E1:0F': 'Dell',
            'B4:96:91': 'Dell',
            'B8:2A:72': 'Dell',
            'B8:CA:3A': 'Dell',
            'B8:E8:56': 'Dell',
            'BC:30:5B': 'Dell',
            'BC:54:36': 'Dell',
            'C8:1E:E7': 'Dell',
            'C8:F7:50': 'Dell',
            'CC:2F:71': 'Dell',
            'D0:67:E5': 'Dell',
            'D4:81:D7': 'Dell',
            'D4:AE:52': 'Dell',
            'D4:BE:D9': 'Dell',
            'D8:9D:67': 'HP',
            'DC:53:60': 'HP',
            'E0:DB:55': 'Dell',
            'E4:43:4B': 'Dell',
            'E8:B2:AC': 'Dell',
            'EC:0E:C4': 'Dell',
            'EC:F4:BB': 'Dell',
            'F0:1F:AF': 'Dell',
            'F0:4D:A2': 'Dell',
            'F4:8E:38': 'Dell',
            'F8:BC:12': 'HP',
            'F8:CA:B8': 'HP',
            'F8:DB:88': 'Dell',
            'F8:E6:1A': 'Dell',
            'F8:FC:AF': 'Dell',
            'FC:F8:AE': 'Dell',
            '00:09:5B': 'Netgear',
            '00:0F:B5': 'Netgear',
            '00:14:6C': 'Netgear',
            '00:1B:2F': 'Netgear',
            '00:1E:2A': 'Netgear',
            '00:1F:33': 'Netgear',
            '00:22:3F': 'Netgear',
            '00:24:B2': 'Netgear',
            '00:26:F2': 'Netgear',
            '08:36:C9': 'TP-Link',
            '10:FE:ED': 'TP-Link',
            '00:0F:66': 'Cisco',
            '00:0C:30': 'Cisco',
            '00:17:DF': 'Cisco',
            '00:18:73': 'Cisco',
            '00:19:2F': 'Cisco',
            '00:19:30': 'Cisco',
            '00:19:55': 'Cisco',
            '00:1A:2B': 'Asus',
            '00:1A:A1': 'Cisco',
            '00:1C:57': 'Cisco',
            '00:1C:58': 'Cisco',
            '00:1C:59': 'Cisco',
            '00:1D:46': 'Cisco',
            '00:1D:70': 'Cisco',
            '00:1E:13': 'Cisco',
            '00:1E:14': 'Cisco',
            '00:1F:6C': 'Cisco',
            '00:1F:CA': 'Cisco',
            '00:22:55': 'Cisco',
            '00:22:90': 'Cisco',
            '00:22:91': 'Cisco',
            '00:22:BF': 'Cisco',
            '00:23:6B': 'Cisco',
            '00:23:AC': 'Cisco',
            '00:24:14': 'Cisco',
            '00:24:33': 'Cisco',
            '00:25:84': 'Cisco',
            '00:25:85': 'Cisco',
            '00:25:9E': 'Cisco',
            '00:26:52': 'Cisco',
            '00:26:53': 'Cisco',
            '00:26:0B': 'Cisco',
            '00:50:0F': 'Cisco',
            '00:53:00': 'Microsoft',
            '00:54:53': 'Microsoft',
            '00:5A:13': 'Microsoft',
            '00:5A:B1': 'Microsoft',
            '00:5D:74': 'Microsoft',
            '00:60:2F': 'Cisco',
            '00:60:47': 'Cisco',
            '00:60:5A': 'Cisco',
            '00:60:7D': 'Cisco',
            '00:60:B3': 'Cisco',
            '00:63:4B': 'Cisco',
            '00:6C:8F': 'Cisco',
            '00:6C:9F': 'Cisco',
            '00:6D:61': 'Cisco',
            '00:70:85': 'Cisco',
            '00:70:DE': 'Cisco',
            '00:70:E4': 'Cisco',
            '00:72:63': 'Cisco',
            '00:73:63': 'Cisco',
            '00:78:88': 'Cisco',
            '00:79:AC': 'Cisco',
            '00:7B:24': 'Cisco',
            '00:7D:4E': 'Cisco',
            '00:7E:28': 'Cisco',
            '00:7E:CA': 'Cisco',
            '00:80:0C': 'Cisco',
            '00:80:A0': 'Cisco',
            '00:80:C7': 'Cisco',
            '00:81:C8': 'Cisco',
            '00:82:82': 'Cisco',
            '00:84:20': 'Cisco',
            '00:86:7C': 'Cisco',
            '00:86:A0': 'Cisco',
            '00:87:2E': 'Cisco',
            '00:87:3E': 'Cisco',
            '00:87:7C': 'Cisco',
            '00:87:E5': 'Cisco',
            '00:89:26': 'Cisco',
            '00:89:3E': 'Cisco',
            '00:8A:2D': 'Cisco',
            '00:8A:7E': 'Cisco',
            '00:8A:86': 'Cisco',
            '00:8B:42': 'Cisco',
            '00:8B:6C': 'Cisco',
            '00:8C:54': 'Cisco',
            '00:8C:8A': 'Cisco',
            '00:8C:BA': 'Cisco',
            '00:8C:F0': 'Cisco',
            '00:8D:12': 'Cisco',
            '00:8D:36': 'Cisco',
            '00:8E:3C': 'Cisco',
            '00:8E:F2': 'Cisco',
            '00:8F:68': 'Cisco',
            '00:90:0C': 'Cisco',
            '00:90:7B': 'Cisco',
            '00:90:BF': 'Cisco',
            '00:91:5C': 'Cisco',
            '00:91:60': 'Cisco',
            '00:91:7A': 'Cisco',
            '00:91:E1': 'Cisco',
            '00:91:FE': 'Cisco',
            '00:92:8E': 'Cisco',
            '00:93:63': 'Cisco',
            '00:93:64': 'Cisco',
            '00:93:9E': 'Cisco',
            '00:93:F0': 'Cisco',
            '00:94:04': 'Cisco',
            '00:94:39': 'Cisco',
            '00:94:60': 'Cisco',
            '00:94:7C': 'Cisco',
            '00:94:96': 'Cisco',
            '00:94:A2': 'Cisco',
            '00:95:5F': 'Cisco',
            '00:95:86': 'Cisco',
            '00:95:9C': 'Cisco',
            '00:96:3A': 'Cisco',
            '00:96:4C': 'Cisco',
            '00:96:6D': 'Cisco',
            '00:96:7C': 'Cisco',
            '00:97:46': 'Cisco',
            '00:97:5A': 'Cisco',
            '00:97:6F': 'Cisco',
            '00:98:14': 'Cisco',
            '00:98:26': 'Cisco',
            '00:98:76': 'Cisco',
            '00:98:9C': 'Cisco',
            '00:99:38': 'Cisco',
            '00:99:54': 'Cisco',
            '00:99:7C': 'Cisco',
            '00:99:90': 'Cisco',
            '00:99:AA': 'Cisco',
            '00:99:B8': 'Cisco',
            '00:99:CC': 'Cisco',
            '00:9A:CD': 'Cisco',
            '00:9A:D2': 'Cisco',
            '00:9A:E0': 'Cisco',
            '00:9A:FC': 'Cisco',
            '00:9B:04': 'Cisco',
            '00:9B:1C': 'Cisco',
            '00:9B:2A': 'Cisco',
            '00:9B:3C': 'Cisco',
            '00:9B:4E': 'Cisco',
            '00:9B:6C': 'Cisco',
            '00:9B:88': 'Cisco',
            '00:9B:A0': 'Cisco',
            '00:9B:B8': 'Cisco',
            '00:9C:02': 'Cisco',
            '00:9C:52': 'Cisco',
            '00:9C:7E': 'Cisco',
            '00:9D:4B': 'Cisco',
            '00:9D:57': 'Cisco',
            '00:9D:8E': 'Cisco',
            '00:9D:9C': 'Cisco',
            '00:9E:1E': 'Cisco',
            '00:9E:38': 'Cisco',
            '00:9E:52': 'Cisco',
            '00:9E:76': 'Cisco',
            '00:9F:4E': 'Cisco',
            '00:9F:68': 'Cisco',
            '00:9F:7C': 'Cisco',
            '00:9F:A6': 'Cisco',
            '00:9F:C8': 'Cisco',
            '00:A0:40': 'Cisco',
            '00:A0:57': 'Cisco',
            '00:A0:8A': 'Cisco',
            '00:A0:A1': 'Cisco',
            '00:A0:C9': 'Cisco',
            '00:A0:D1': 'Cisco',
            '00:A1:0A': 'Cisco',
            '00:A1:28': 'Cisco',
            '00:A1:49': 'Cisco',
            '00:A1:6A': 'Cisco',
            '00:A1:8A': 'Cisco',
            '00:A1:D4': 'Cisco',
            '00:A2:19': 'Cisco',
            '00:A2:4F': 'Cisco',
            '00:A2:91': 'Cisco',
            '00:A2:B3': 'Cisco',
            '00:A2:F3': 'Cisco',
            '00:A3:09': 'Cisco',
            '00:A3:47': 'Cisco',
            '00:A3:7B': 'Cisco',
            '00:A3:97': 'Cisco',
            '00:A3:BB': 'Cisco',
            '00:A4:4F': 'Cisco',
            '00:A4:71': 'HP',
            '00:A4:9D': 'Cisco',
            '00:A4:C3': 'Cisco',
            '00:A4:E9': 'Cisco',
            '00:A5:09': 'Cisco',
            '00:A5:24': 'Cisco',
            '00:A5:4B': 'Cisco',
            '00:A5:74': 'Cisco',
            '00:A5:C5': 'Cisco',
            '00:A5:EC': 'Cisco',
            '00:A6:0C': 'Cisco',
            '00:A6:3F': 'Cisco',
            '00:A6:51': 'Cisco',
            '00:A6:8F': 'Cisco',
            '00:A6:BB': 'Cisco',
            '00:A6:D5': 'Cisco',
            '00:A7:09': 'Cisco',
            '00:A7:39': 'Cisco',
            '00:A7:67': 'Cisco',
            '00:A7:8B': 'Cisco',
            '00:A7:BB': 'Cisco',
            '00:A7:E3': 'Cisco',
            '00:A8:13': 'Cisco',
            '00:A8:3D': 'Cisco',
            '00:A8:73': 'Cisco',
            '00:A8:95': 'Cisco',
            '00:A8:B9': 'Cisco',
            '00:A8:F9': 'Cisco',
            '00:A9:0C': 'Cisco',
            '00:A9:3A': 'Cisco',
            '00:A9:6B': 'Cisco',
            '00:A9:8F': 'Cisco',
            '00:A9:C1': 'Cisco',
            '00:A9:EB': 'Cisco',
            '00:AA:00': 'Intel',
            '00:AA:01': 'Intel',
            '00:AA:02': 'Intel',
            '00:AA:03': 'Intel',
            '00:AA:10': 'Intel',
            '00:AA:11': 'Intel',
            '00:AA:12': 'Intel',
            '00:AA:13': 'Intel',
            '00:AA:20': 'Intel',
            '00:AA:21': 'Intel',
            '00:AA:22': 'Intel',
            '00:AA:23': 'Intel',
            '00:AA:30': 'Intel',
            '00:AA:31': 'Intel',
            '00:AA:32': 'Intel',
            '00:AA:33': 'Intel',
            '00:AA:40': 'Intel',
            '00:AA:41': 'Intel',
            '00:AA:42': 'Intel',
            '00:AA:43': 'Intel',
            '00:AA:50': 'Intel',
            '00:AA:51': 'Intel',
            '00:AA:52': 'Intel',
            '00:AA:53': 'Intel',
            '00:AA:60': 'Intel',
            '00:AA:61': 'Intel',
            '00:AA:62': 'Intel',
            '00:AA:63': 'Intel',
            '00:AA:70': 'Intel',
            '00:AA:71': 'Intel',
            '00:AA:72': 'Intel',
            '00:AA:73': 'Intel',
            '00:AA:80': 'Intel',
            '00:AA:81': 'Intel',
            '00:AA:82': 'Intel',
            'AA:00:00': 'Digital',
            'AA:00:01': 'Digital',
            'AA:00:02': 'Digital',
            'AA:00:03': 'Digital',
            '00:AA:90': 'Intel',
            '00:AA:91': 'Intel',
            '00:AA:92': 'Intel',
            '00:AA:93': 'Intel',
            '00:AA:A0': 'Intel',
            '00:AA:A1': 'Intel',
            '00:AA:A2': 'Intel',
            '00:AA:A3': 'Intel',
            '00:AA:B0': 'Intel',
            '00:AA:B1': 'Intel',
            '00:AA:B2': 'Intel',
            '00:AA:B3': 'Intel',
            '00:AA:C0': 'Intel',
            '00:AA:C1': 'Intel',
            '00:AA:C2': 'Intel',
            '00:AA:C3': 'Intel',
            '00:AA:D0': 'Intel',
            '00:AA:D1': 'Intel',
            '00:AA:D2': 'Intel',
            '00:AA:D3': 'Intel',
            '00:AA:E0': 'Intel',
            '00:AA:E1': 'Intel',
            '00:AA:E2': 'Intel',
            '00:AA:E3': 'Intel',
            '00:AA:F0': 'Intel',
            '00:AA:F1': 'Intel',
            '00:AA:F2': 'Intel',
            '00:AA:F3': 'Intel',
            '00:00:5E': 'IANA',
            '00:03:FF': 'Microsoft',
            '00:0D:3A': 'Microsoft',
            '00:10:60': 'HP',
            '00:10:83': 'HP',
            '00:10:E3': 'HP',
            '00:11:0A': 'HP',
            '00:11:85': 'HP',
            '00:12:79': 'HP',
            '00:13:21': 'HP',
            '00:16:35': 'HP',
            '00:17:08': 'HP',
            '00:18:FE': 'HP',
            '00:19:BB': 'HP',
            '00:1A:4B': 'HP',
            '00:1B:78': 'HP',
            '00:1C:C4': 'HP',
            '00:1D:B3': 'HP',
            '00:1E:0B': 'HP',
            '00:1F:29': 'HP',
            '00:1F:FE': 'HP',
            '00:21:5A': 'HP',
            '00:22:64': 'HP',
            '00:23:7D': 'HP',
            '00:24:81': 'HP',
            '00:25:B3': 'HP',
            '00:26:55': 'HP',
            '00:26:F1': 'HP',
            '00:30:6E': 'HP',
            '00:30:C1': 'HP',
            '00:40:17': 'HP',
            '00:50:8B': 'HP',
            '00:50:9A': 'HP',
            '00:60:B0': 'HP',
            '00:80:A0': 'HP',
            '00:B0:D0': 'HP',
            '00:C0:4F': 'HP',
            '00:C0:7B': 'HP',
            '00:C0:B7': 'HP',
            '00:D0:AD': 'HP',
            '00:D4:85': 'HP',
            '00:D8:C3': 'HP',
            '00:E0:29': 'HP',
            '00:E0:3C': 'HP',
            '00:E0:52': 'HP',
            '00:E0:7C': 'HP',
            '00:E0:98': 'HP',
            '00:E0:B1': 'HP',
            '00:E0:C1': 'HP',
            '00:E0:EE': 'HP',
            '00:E0:F0': 'HP',
            '00:E8:02': 'HP',
            '00:E8:4C': 'HP',
            '00:E8:62': 'HP',
            '00:E8:7A': 'HP',
            '00:E8:A8': 'HP',
            '00:E8:DE': 'HP',
            '00:F0:19': 'HP',
            '00:F0:2D': 'HP',
            '00:F0:61': 'HP',
            '00:F0:6C': 'HP',
            '00:F0:7C': 'HP',
            '00:F0:86': 'HP',
            '00:F0:A0': 'HP',
            '00:F0:C8': 'HP',
            '00:F0:D4': 'HP',
            '00:F0:ED': 'HP',
            '00:F0:F6': 'HP',
            '00:F1:18': 'HP',
            '00:F1:2A': 'HP',
            '00:F1:3F': 'HP',
            '00:F1:4C': 'HP',
            '00:F1:5D': 'HP',
            '00:F1:6B': 'HP',
            '00:F1:7D': 'HP',
            '00:F1:8A': 'HP',
            '00:F1:9C': 'HP',
            '00:F1:A7': 'HP',
            '00:F1:C0': 'HP',
            '00:F1:D3': 'HP',
            '00:F1:E1': 'HP',
            '00:F1:F2': 'HP',
            '00:F2:02': 'HP',
            '00:F2:0E': 'HP',
            '00:F2:14': 'HP',
            '00:F2:1D': 'HP',
            '00:F2:2A': 'HP',
            '00:F2:3E': 'HP',
            '00:F2:4C': 'HP',
            '00:F2:5D': 'HP',
            '00:F2:6A': 'HP',
            '00:F2:7A': 'HP',
            '00:F2:8A': 'HP',
            '00:F2:99': 'HP',
            '00:F2:AA': 'HP',
            '00:F2:B7': 'HP',
            '00:F2:C8': 'HP',
            '00:F2:D7': 'HP',
            '00:F2:E9': 'HP',
            '00:F2:F8': 'HP',
            '00:F3:07': 'HP',
            '00:F3:15': 'HP',
            '00:F3:25': 'HP',
            '00:F3:33': 'HP',
            '00:F3:44': 'HP',
            '00:F3:52': 'HP',
            '00:F3:60': 'HP',
            '00:F3:72': 'HP',
            '00:F3:80': 'HP',
            '00:F3:91': 'HP',
            '00:F3:A0': 'HP',
            '00:F3:B1': 'HP',
            '00:F3:C2': 'HP',
            '00:F3:D0': 'HP',
            '00:F3:E2': 'HP',
            '00:F3:F3': 'HP',
            '00:F4:00': 'HP',
            '00:F4:10': 'HP',
            '00:F4:20': 'HP',
            '00:F4:32': 'HP',
            '00:F4:43': 'HP',
            '00:F4:51': 'HP',
            '00:F4:62': 'HP',
            '00:F4:70': 'HP',
            '00:F4:81': 'HP',
            '00:F4:92': 'HP',
            '00:F4:A0': 'HP',
            '00:F4:B1': 'HP',
            '00:F4:C2': 'HP',
            '00:F4:D2': 'HP',
            '00:F4:E3': 'HP',
            '00:F4:F0': 'HP',
            '00:F5:02': 'HP',
            '00:F5:12': 'HP',
            '00:F5:20': 'HP',
            '00:F5:32': 'HP',
            '00:F5:43': 'HP',
            '00:F5:51': 'HP',
            '00:F5:62': 'HP',
            '00:F5:70': 'HP',
            '00:F5:81': 'HP',
            '00:F5:92': 'HP',
            '00:F5:A0': 'HP',
            '00:F5:B1': 'HP',
            '00:F5:C2': 'HP',
            '00:F5:D2': 'HP',
            '00:F5:E3': 'HP',
            '00:F5:F0': 'HP',
            '00:F6:02': 'HP',
            '00:F6:12': 'HP',
            '00:F6:20': 'HP',
            '00:F6:32': 'HP',
            '00:F6:43': 'HP',
            '00:F6:51': 'HP',
            '00:F6:62': 'HP',
            '00:F6:70': 'HP',
            '00:F6:81': 'HP',
            '00:F6:92': 'HP',
            '00:F6:A0': 'HP',
            '00:F6:B1': 'HP',
            '00:F6:C2': 'HP',
            '00:F6:D2': 'HP',
            '00:F6:E3': 'HP',
            '00:F6:F0': 'HP',
            '00:F7:02': 'HP',
            '00:F7:12': 'HP',
            '00:F7:20': 'HP',
            '00:F7:32': 'HP',
            '00:F7:43': 'HP',
            '00:F7:51': 'HP',
            '00:F7:62': 'HP',
            '00:F7:70': 'HP',
            '00:F7:81': 'HP',
            '00:F7:92': 'HP',
            '00:F7:A0': 'HP',
            '00:F7:B1': 'HP',
            '00:F7:C2': 'HP',
            '00:F7:D2': 'HP',
            '00:F7:E3': 'HP',
            '00:F7:F0': 'HP',
            '00:01:42': 'Cisco',
            '00:01:43': 'Cisco',
            '00:01:64': 'Cisco',
            '00:01:96': 'Cisco',
            '00:01:C7': 'Cisco',
            '00:01:C8': 'Cisco',
            '00:01:C9': 'Cisco',
            '00:01:CA': 'Cisco',
            '00:01:CB': 'Cisco',
            '00:01:CC': 'Cisco',
            '00:01:CD': 'Cisco',
            '00:01:CE': 'Cisco',
            '00:01:CF': 'Cisco',
            '00:01:D0': 'Cisco',
            '00:01:D1': 'Cisco',
            '00:01:D2': 'Cisco',
            '00:01:D3': 'Cisco',
            '00:01:D4': 'Cisco',
            '00:01:D5': 'Cisco',
            '00:01:D6': 'Cisco',
            '00:01:D7': 'Cisco',
            '00:01:D8': 'Cisco',
            '00:01:D9': 'Cisco',
            '00:01:DA': 'Cisco',
            '00:01:DB': 'Cisco',
            '00:01:DC': 'Cisco',
            '00:01:DD': 'Cisco',
            '00:01:DE': 'Cisco',
            '00:01:DF': 'Cisco',
            '00:01:E0': 'Cisco',
            '00:01:E1': 'Cisco',
            '00:01:E2': 'Cisco',
            '00:01:E3': 'Cisco',
            '00:01:E4': 'Cisco',
            '00:01:E5': 'Cisco',
            '00:01:E6': 'Cisco',
            '00:01:E7': 'Cisco',
            '00:01:E8': 'Cisco',
            '00:01:E9': 'Cisco',
            '00:01:EA': 'Cisco',
            '00:01:EB': 'Cisco',
            '00:01:EC': 'Cisco',
            '00:01:ED': 'Cisco',
            '00:01:EE': 'Cisco',
            '00:01:EF': 'Cisco',
            '00:01:F0': 'Cisco',
            '00:01:F1': 'Cisco',
            '00:01:F2': 'Cisco',
            '00:01:F3': 'Cisco',
            '00:01:F4': 'Cisco',
            '00:01:F5': 'Cisco',
            '00:01:F6': 'Cisco',
            '00:01:F7': 'Cisco',
            '00:01:F8': 'Cisco',
            '00:01:F9': 'Cisco',
            '00:01:FA': 'Cisco',
            '00:01:FB': 'Cisco',
            '00:01:FC': 'Cisco',
            '00:01:FD': 'Cisco',
            '00:01:FE': 'Cisco',
            '00:01:FF': 'Cisco',
            '00:0D:28': 'HP',
            '00:0D:29': 'HP',
            '00:0D:2A': 'HP',
            '00:0D:2B': 'HP',
            '00:0D:2C': 'HP',
            '00:0D:2D': 'HP',
            '00:0D:2E': 'HP',
            '00:0D:2F': 'HP',
            '00:0D:30': 'HP',
            '00:0D:31': 'HP',
            '00:0D:32': 'HP',
            '00:0D:33': 'HP',
            '00:0D:34': 'HP',
            '00:0D:35': 'HP',
            '00:0D:36': 'HP',
            '00:0D:37': 'HP',
            '00:0D:38': 'HP',
            '00:0D:39': 'HP',
            '00:0D:3A': 'HP',
            '00:0D:3B': 'HP',
            '00:0D:3C': 'HP',
            '00:0D:3D': 'HP',
            '00:0D:3E': 'HP',
            '00:0D:3F': 'HP',
            '00:0D:40': 'HP',
            '00:0D:41': 'HP',
            '00:0D:42': 'HP',
            '00:0D:43': 'HP',
            '00:0D:44': 'HP',
            '00:0D:45': 'HP',
            '00:0D:46': 'HP',
            '00:0D:47': 'HP',
            '00:0D:48': 'HP',
            '00:0D:49': 'HP',
            '00:0D:4A': 'HP',
            '00:0D:4B': 'HP',
            '00:0D:4C': 'HP',
            '00:0D:4D': 'HP',
            '00:0D:4E': 'HP',
            '00:0D:4F': 'HP',
            '00:0D:50': 'HP',
            '00:0D:51': 'HP',
            '00:0D:52': 'HP',
            '00:0D:53': 'HP',
            '00:0D:54': 'HP',
            '00:0D:55': 'HP',
            '00:0D:56': 'HP',
            '00:0D:57': 'HP',
            '00:0D:58': 'HP',
            '00:0D:59': 'HP',
            '00:0D:5A': 'HP',
            '00:0D:5B': 'HP',
            '00:0D:5C': 'HP',
            '00:0D:5D': 'HP',
            '00:0D:5E': 'HP',
            '00:0D:5F': 'HP',
            '00:0D:60': 'HP',
            '00:0D:61': 'HP',
            '00:0D:62': 'HP',
            '00:0D:63': 'HP',
            '00:0D:64': 'HP',
            '00:0D:65': 'HP',
            '00:0D:66': 'HP',
            '00:0D:67': 'HP',
            '00:0D:68': 'HP',
            '00:0D:69': 'HP',
            '00:0D:6A': 'HP',
            '00:0D:6B': 'HP',
            '00:0D:6C': 'HP',
            '00:0D:6D': 'HP',
            '00:0D:6E': 'HP',
            '00:0D:6F': 'HP',
            '00:0D:70': 'HP',
            '00:0D:71': 'HP',
            '00:0D:72': 'HP',
            '00:0D:73': 'HP',
            '00:0D:74': 'HP',
            '00:0D:75': 'HP',
            '00:0D:76': 'HP',
            '00:0D:77': 'HP',
            '00:0D:78': 'HP',
            '00:0D:79': 'HP',
            '00:0D:7A': 'HP',
            '00:0D:7B': 'HP',
            '00:0D:7C': 'HP',
            '00:0D:7D': 'HP',
            '00:0D:7E': 'HP',
            '00:0D:7F': 'HP',
            '00:0D:80': 'HP',
            '00:0D:81': 'HP',
            '00:0D:82': 'HP',
            '00:0D:83': 'HP',
            '00:0D:84': 'HP',
            '00:0D:85': 'HP',
            '00:0D:86': 'HP',
            '00:0D:87': 'HP',
            '00:0D:88': 'HP',
            '00:0D:89': 'HP',
            '00:0D:8A': 'HP',
            '00:0D:8B': 'HP',
            '00:0D:8C': 'HP',
            '00:0D:8D': 'HP',
            '00:0D:8E': 'HP',
            '00:0D:8F': 'HP',
            '00:0D:90': 'HP',
            '00:0D:91': 'HP',
            '00:0D:92': 'HP',
            '00:0D:93': 'HP',
            '00:0D:94': 'HP',
            '00:0D:95': 'HP',
            '00:0D:96': 'HP',
            '00:0D:97': 'HP',
            '00:0D:98': 'HP',
            '00:0D:99': 'HP',
            '00:0D:9A': 'HP',
            '00:0D:9B': 'HP',
            '00:0D:9C': 'HP',
            '00:0D:9D': 'HP',
            '00:0D:9E': 'HP',
            '00:0D:9F': 'HP',
            '00:0D:A0': 'HP',
            '00:0D:A1': 'HP',
            '00:0D:A2': 'HP',
            '00:0D:A3': 'HP',
            '00:0D:A4': 'HP',
            '00:0D:A5': 'HP',
            '00:0D:A6': 'HP',
            '00:0D:A7': 'HP',
            '00:0D:A8': 'HP',
            '00:0D:A9': 'HP',
            '00:0D:AA': 'HP',
            '00:0D:AB': 'HP',
            '00:0D:AC': 'HP',
            '00:0D:AD': 'HP',
            '00:0D:AE': 'HP',
            '00:0D:AF': 'HP',
            '00:0D:B0': 'HP',
            '00:0D:B1': 'HP',
            '00:0D:B2': 'HP',
            '00:0D:B3': 'HP',
            '00:0D:B4': 'HP',
            '00:0D:B5': 'HP',
            '00:0D:B6': 'HP',
            '00:0D:B7': 'HP',
            '00:0D:B8': 'HP',
            '00:0D:B9': 'HP',
            '00:0D:BA': 'HP',
            '00:0D:BB': 'HP',
            '00:0D:BC': 'HP',
            '00:0D:BD': 'HP',
            '00:0D:BE': 'HP',
            '00:0D:BF': 'HP',
            '00:0D:C0': 'HP',
            '00:0D:C1': 'HP',
            '00:0D:C2': 'HP',
            '00:0D:C3': 'HP',
            '00:0D:C4': 'HP',
            '00:0D:C5': 'HP',
            '00:0D:C6': 'HP',
            '00:0D:C7': 'HP',
            '00:0D:C8': 'HP',
            '00:0D:C9': 'HP',
            '00:0D:CA': 'HP',
            '00:0D:CB': 'HP',
            '00:0D:CC': 'HP',
            '00:0D:CD': 'HP',
            '00:0D:CE': 'HP',
            '00:0D:CF': 'HP',
            '00:0D:D0': 'HP',
            '00:0D:D1': 'HP',
            '00:0D:D2': 'HP',
            '00:0D:D3': 'HP',
            '00:0D:D4': 'HP',
            '00:0D:D5': 'HP',
            '00:0D:D6': 'HP',
            '00:0D:D7': 'HP',
            '00:0D:D8': 'HP',
            '00:0D:D9': 'HP',
            '00:0D:DA': 'HP',
            '00:0D:DB': 'HP',
            '00:0D:DC': 'HP',
            '00:0D:DD': 'HP',
            '00:0D:DE': 'HP',
            '00:0D:DF': 'HP',
            '00:0D:E0': 'HP',
            '00:0D:E1': 'HP',
            '00:0D:E2': 'HP',
            '00:0D:E3': 'HP',
            '00:0D:E4': 'HP',
            '00:0D:E5': 'HP',
            '00:0D:E6': 'HP',
            '00:0D:E7': 'HP',
            '00:0D:E8': 'HP',
            '00:0D:E9': 'HP',
            '00:0D:EA': 'HP',
            '00:0D:EB': 'HP',
            '00:0D:EC': 'HP',
            '00:0D:ED': 'HP',
            '00:0D:EE': 'HP',
            '00:0D:EF': 'HP',
            '00:0D:F0': 'HP',
            '00:0D:F1': 'HP',
            '00:0D:F2': 'HP',
            '00:0D:F3': 'HP',
            '00:0D:F4': 'HP',
            '00:0D:F5': 'HP',
            '00:0D:F6': 'HP',
            '00:0D:F7': 'HP',
            '00:0D:F8': 'HP',
            '00:0D:F9': 'HP',
            '00:0D:FA': 'HP',
            '00:0D:FB': 'HP',
            '00:0D:FC': 'HP',
            '00:0D:FD': 'HP',
            '00:0D:FE': 'HP',
            '00:0D:FF': 'HP',
            'DC:53:60': 'HP',
            'D8:9D:67': 'HP',
            'F8:BC:12': 'HP',
            'F8:CA:B8': 'HP',
            'A0:1D:48': 'HP',
            'F8:75:88': 'HP',
            '00:04:5A': 'Dell',
            '00:06:5B': 'Dell',
            '00:08:74': 'Dell',
            '00:0B:DB': 'Dell',
            '00:0D:56': 'Dell',
            '00:0F:1F': 'Dell',
            '00:11:43': 'Dell',
            '00:12:3F': 'Dell',
            '00:13:72': 'Dell',
            '00:14:22': 'Dell',
            '00:15:C5': 'Dell',
            '00:16:F0': 'Dell',
            '00:18:8B': 'Dell',
            '00:19:B9': 'Dell',
            '00:1A:A0': 'Realtek',
            '00:1C:23': 'Dell',
            '00:1D:09': 'Dell',
            '00:1E:4F': 'Dell',
            '00:1E:C9': 'Dell',
            '00:21:70': 'Dell',
            '00:21:9B': 'Dell',
            '00:22:19': 'Dell',
            '00:23:AE': 'Dell',
            '00:24:E8': 'Dell',
            '00:25:64': 'Dell',
            '00:26:B9': 'Dell',
            '00:40:45': 'Dell',
            '08:00:1B': 'Dell',
            '10:1F:74': 'HP',
            '14:18:77': 'Dell',
            '14:58:D0': 'HP',
            '14:9E:CF': 'Dell',
            '14:B3:1F': 'Dell',
            '14:FE:B5': 'Dell',
            '18:03:73': 'Dell',
            '18:66:DA': 'Dell',
            '18:DB:F2': 'Dell',
            '18:FB:7B': 'Dell',
            '1C:40:24': 'Dell',
            '20:47:47': 'Dell',
            '24:6E:96': 'Dell',
            '28:F1:0E': 'Dell',
            '34:17:EB': 'Dell',
            '34:E6:D7': 'Dell',
            '34:FD:6A': 'Dell',
            '38:BA:F8': 'Dell',
            '3C:D9:1B': 'HP',
            '44:A8:85': 'Dell',
            '48:4D:7E': 'HP',
            '4C:76:25': 'Dell',
            '4C:80:93': 'Dell',
            '50:9A:4C': 'Dell',
            '54:9F:35': 'Dell',
            '58:94:6B': 'Dell',
            '5C:26:0A': 'Dell',
            '5C:F9:DD': 'Dell',
            '64:00:6A': 'Dell',
            '68:05:CA': 'Dell',
            '6C:F0:49': 'Dell',
            '70:5C:AD': 'Dell',
            '74:86:7A': 'Dell',
            '74:E6:E2': 'Dell',
            '78:2B:CB': 'Dell',
            '78:45:C4': 'Dell',
            '78:AC:C0': 'HP',
            '7C:5C:F8': 'Dell',
            '7C:5F:67': 'Dell',
            '80:18:A7': 'Dell',
            '80:CE:62': 'Dell',
            '84:2B:2B': 'Dell',
            '84:7B:EB': 'Dell',
            '84:8F:69': 'Dell',
            '88:88:3F': 'Dell',
            '88:AE:1D': 'Dell',
            '8C:EC:4B': 'Dell',
            '90:B1:1C': 'Dell',
            '94:57:A5': 'HP',
            '98:90:96': 'Dell',
            '9C:4F:DA': 'Dell',
            '9C:F3:87': 'Dell',
            'A4:1F:72': 'Dell',
            'A4:BA:DB': 'Dell',
            'A8:6D:AA': 'Dell',
            'AC:22:0B': 'Asus',
            'B0:83:FE': 'Dell',
            'B4:E1:0F': 'Dell',
            'B4:96:91': 'Dell',
            'B8:2A:72': 'Dell',
            'B8:CA:3A': 'Dell',
            'B8:E8:56': 'Dell',
            'BC:30:5B': 'Dell',
            'BC:54:36': 'Dell',
            'C8:1E:E7': 'Dell',
            'C8:F7:50': 'Dell',
            'CC:2F:71': 'Dell',
            'D0:67:E5': 'Dell',
            'D4:81:D7': 'Dell',
            'D4:AE:52': 'Dell',
            'D4:BE:D9': 'Dell',
            'D8:9D:67': 'HP',
            'DC:53:60': 'HP',
            'E0:DB:55': 'Dell',
            'E4:43:4B': 'Dell',
            'E8:B2:AC': 'Dell',
            'EC:0E:C4': 'Dell',
            'EC:F4:BB': 'Dell',
            'F0:1F:AF': 'Dell',
            'F0:4D:A2': 'Dell',
            'F4:8E:38': 'Dell',
            'F8:BC:12': 'HP',
            'F8:CA:B8': 'HP',
            'F8:DB:88': 'Dell',
            'F8:E6:1A': 'Dell',
            'F8:FC:AF': 'Dell',
            'FC:F8:AE': 'Dell',
            '00:09:5B': 'Netgear',
            '00:0F:B5': 'Netgear',
            '00:14:6C': 'Netgear',
            '00:1B:2F': 'Netgear',
            '00:1E:2A': 'Netgear',
            '00:1F:33': 'Netgear',
            '00:22:3F': 'Netgear',
            '00:24:B2': 'Netgear',
            '00:26:F2': 'Netgear',
            '08:36:C9': 'TP-Link',
            '10:FE:ED': 'TP-Link',
            '00:17:3F': 'Samsung',
            '00:1A:8A': 'Samsung',
            '00:1D:25': 'Samsung',
            '00:1E:7D': 'Samsung',
            '00:1F:CC': 'Samsung',
            '00:1F:CD': 'Samsung',
            '00:21:4C': 'Samsung',
            '00:21:D1': 'Samsung',
            '00:21:D2': 'Samsung',
            '00:23:39': 'Samsung',
            '00:23:3A': 'Samsung',
            '00:23:99': 'Samsung',
            '00:23:D6': 'Samsung',
            '00:23:D7': 'Samsung',
            '00:24:54': 'Samsung',
            '00:24:90': 'Samsung',
            '00:24:91': 'Samsung',
            '00:24:E5': 'Samsung',
            '00:24:E6': 'Samsung',
            '00:25:66': 'Samsung',
            '00:25:67': 'Samsung',
            '00:26:37': 'Samsung',
            '00:26:5D': 'Samsung',
            '00:26:5F': 'Samsung',
            '00:26:6D': 'Samsung',
            '00:26:75': 'Samsung',
            '00:26:7A': 'Samsung',
            '00:26:7D': 'Samsung',
            'B8:5A:73': 'Samsung',
            'B8:D9:CE': 'Samsung',
            'BC:20:A4': 'Samsung',
            'BC:79:AD': 'Samsung',
            'C0:BD:D1': 'Samsung',
            'C4:57:6E': 'Samsung',
            'C8:7E:75': 'Samsung',
            'CC:07:AB': 'Samsung',
            'D0:22:BE': 'Samsung',
            'D0:59:E4': 'Samsung',
            'D0:C1:B1': 'Samsung',
            'D4:87:D8': 'Samsung',
            'D8:90:E8': 'Samsung',
            'D8:C7:71': 'Samsung',
            'DC:66:72': 'Samsung',
            'E0:5F:45': 'Samsung',
            'E0:B9:4D': 'Samsung',
            'E4:12:1D': 'Samsung',
            'E4:58:B8': 'Samsung',
            'E4:7C:F9': 'Samsung',
            'E8:4E:CE': 'Samsung',
            'EC:1F:72': 'Samsung',
            'F0:25:B7': 'Samsung',
            'F4:09:D8': 'Samsung',
            'F4:42:8F': 'Samsung',
            'F8:77:B8': 'Samsung',
            'F8:77:C5': 'Samsung',
            '00:00:00': 'Unknown',
        }
        
        for oui, name in common_ouis.items():
            self._oui_cache[oui.upper()] = name
        
        for oui, name in common_ouis.items():
            oui_normalized = oui.replace(':', '-').upper()
            self._oui_cache[oui_normalized] = name
    
    def _get_manufacturer(self, mac: str) -> str:
        """Get manufacturer from MAC address OUI"""
        if not mac or ':' not in mac:
            return 'Unknown'
        
        mac_upper = mac.upper()
        oui = ':'.join(mac_upper.split(':')[:3])
        
        if oui in self._oui_cache:
            return self._oui_cache[oui]
        
        oui_dash = oui.replace(':', '-')
        if oui_dash in self._oui_cache:
            return self._oui_cache[oui_dash]
        
        return 'Unknown'
    
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
            
            networks_2g = [n for n in networks if '2.4' in str(n.get('band', ''))]
            networks_5g = [n for n in networks if '5' in str(n.get('band', '')) and '2.4' not in str(n.get('band', ''))]
            
            if networks_2g:
                print("\n   📶 2.4 GHz NETWORKS:")
                print(f"   {'SSID':<20} {'BSSID':<18} {'Ch':<4} {'RSSI':<6} {'Band':<6}")
                print(f"   {'-'*60}")
                for net in networks_2g[:10]:
                    bssid = net.get('bssid', 'N/A')
                    ch = net.get('channel', '?')
                    rssi = net.get('rssi', '?')
                    band = net.get('band', '2.4G')[:5]
                    
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
            
            if networks_5g:
                print("\n   📶 5 GHz NETWORKS:")
                print(f"   {'SSID':<20} {'BSSID':<18} {'Ch':<4} {'RSSI':<6} {'Band':<6}")
                print(f"   {'-'*60}")
                for net in networks_5g[:10]:
                    bssid = net.get('bssid', 'N/A')
                    ch = net.get('channel', '?')
                    rssi = net.get('rssi', '?')
                    band = net.get('band', '5G')[:5]
                    
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
        
        connected_devices = []
        searching_devices = []
        
        for item in probed:
            connected_bssid = item.get('connected_bssid', '')
            device_mac = item.get('device_mac', 'N/A')
            signal = item.get('signal', 'N/A')
            ssids = item.get('probed_ssids', [])
            manufacturer = self._get_manufacturer(device_mac)
            
            device_info = {
                'mac': device_mac,
                'manufacturer': manufacturer,
                'signal': signal
            }
            
            if connected_bssid and ':' in connected_bssid:
                device_info['connected_to'] = connected_bssid
                connected_devices.append(device_info)
            
            if ssids:
                device_info['searching'] = [s.strip() for s in ssids if s.strip()]
                searching_devices.append(device_info)
        
        if connected_devices:
            print("\n   📱 CONNECTED DEVICES:")
            print(f"   {'Device MAC':<18} {'RSSI':<6} {'Manufacturer':<15} {'Connected To':<19}")
            print(f"   {'-'*75}")
            seen_bssids = set()
            for item in connected_devices:
                device_mac = item.get('mac', 'Unknown')[:17]
                rssi = f"{item['signal']:<6}"
                mfg = f"{item['manufacturer']:<15}"
                bssid = item.get('connected_to', 'N/A')[:18]
                print(f"   {device_mac:<18} {rssi:<6} {mfg:<15} {bssid:<19}")
                if item['connected_to']:
                    seen_bssids.add(item['connected_to'])
            
            if seen_bssids:
                print(f"\n   📶 Networks: {len(seen_bssids)} active")
                for bssid in sorted(seen_bssids):
                    count = sum(1 for d in connected_devices if d.get('connected_to') == bssid)
                    print(f"      {bssid}: {count} device(s)")
        
        if searching_devices:
            print("\n   🔍 DEVICES SEARCHING FOR WI-FI:")
            print(f"   {'Device MAC':<18} {'RSSI':<6} {'Manufacturer':<15} {'Searching For':<25}")
            print(f"   {'-'*75}")
            seen_ssids = set()
            for item in searching_devices:
                device_mac = item.get('mac', 'Unknown')[:17]
                rssi = f"{item['signal']:<6}"
                mfg = f"{item['manufacturer']:<15}"
                for ssid in item.get('searching', []):
                    if ssid not in seen_ssids:
                        print(f"   {device_mac:<18} {rssi:<6} {mfg:<15} {ssid:<25}")
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
        
        print("\n" + "=" * 60)
        print("💡 RECOMMENDATIONS")
        print("=" * 60)
        
        networks = analysis['scan_data'].get('networks', [])
        congestion = analysis['interference_data'].get('channel_congestion', {})
        impact = analysis['correlation_data']['interference_impact']
        
        networks_2g = [n for n in networks if '2.4' in str(n.get('band', ''))]
        if networks_2g:
            print("\n📺 CHANNEL HEATMAP (2.4 GHz):")
            channel_counts = {}
            for net in networks_2g:
                ch = net.get('channel')
                if ch:
                    channel_counts[ch] = channel_counts.get(ch, 0) + 1
            
            print("   Channel: ", end="")
            for ch in range(1, 14):
                print(f"{ch:>3}", end="")
            print()
            print("   " + "-" * 39)
            print("   Networks: ", end="")
            for ch in range(1, 14):
                count = channel_counts.get(ch, 0)
                bars = min(count, 5)
                if bars > 0:
                    if count >= 3:
                        print(f"{'🔴' * bars:>6}", end="")
                    elif count >= 2:
                        print(f"{'🟠' * bars:>6}", end="")
                    else:
                        print(f"{'🟢' * bars:>6}", end="")
                else:
                    print(f"     ", end="")
            print()
        
        print("\n📊 CURRENT STATUS:")
        print(f"   • Interference Level: {impact['level']} (Score: {impact['score']}/15)")
        print(f"   • Total Networks Detected: {len(networks)}")
        if networks:
            channels_used = set(n.get('channel') for n in networks if n.get('channel'))
            print(f"   • Channels in Use: {', '.join(str(c) for c in sorted(channels_used))}")
        
        print("\n🔧 WHAT TO DO:")
        
        rec_24 = analysis['interference_data'].get('recommendations', {}).get('2.4GHz', {})
        rec_5 = analysis['interference_data'].get('recommendations', {}).get('5GHz', {})
        
        if rec_24.get('recommended'):
            ch = rec_24['recommended']
            networks_on_rec = [n for n in networks if n.get('channel') == ch]
            print(f"\n   1️⃣  SWITCH TO CHANNEL {ch} (2.4 GHz)")
            print(f"      WHY: This channel has fewer competing networks")
            if networks_on_rec:
                print(f"      CURRENT: {len(networks_on_rec)} network(s) on this channel")
            other_channels = [n for n in networks if n.get('channel') and n.get('channel') != ch]
            if other_channels:
                print(f"      OTHER CHANNELS: {len(other_channels)} network(s) competing")
            print(f"      ACTION: Go to your router settings → Wireless → Channel → Select {ch}")
        
        if rec_5.get('recommended'):
            ch = rec_5['recommended']
            print(f"\n   2️⃣  CONSIDER 5 GHz BAND")
            print(f"      WHY: 5 GHz has more channels and less interference")
            print(f"      RECOMMENDED: Channel {ch}")
            print(f"      BENEFITS: Faster speeds, less congestion, more channels")
            print(f"      ACTION: Enable 5 GHz on your router or connect to 5 GHz network")
        
        if impact['level'] in ['HIGH', 'CRITICAL']:
            print(f"\n   ⚠️  HIGH INTERFERENCE DETECTED")
            print(f"      IMPACT: Slow speeds, dropped connections, poor streaming")
            print(f"      SOLUTION: Change Wi-Fi channel or switch to 5 GHz")
        
        if networks:
            congested_chs = [ch for ch, data in congestion.items() if data.get('congestion_level') in ['HIGH', 'CRITICAL']]
            if congested_chs:
                print(f"\n   🚫 AVOID THESE CHANNELS:")
                for ch in congested_chs:
                    count = congestion[ch].get('network_count', 0)
                    print(f"      Channel {ch}: {count} network(s) overlapping")
        
        print("\n📋 INTERFERENCE SCALE (0-15):")
        print("   🟢 MINIMAL (0-2):   No interference")
        print("   🟡 LOW (3-5):      Minor interference")
        print("   🟠 MEDIUM (6-9):    Noticeable interference")
        print("   🔴 HIGH (10-14):    Significant interference")
        print("   ⚫ CRITICAL (15+):  Severe interference")
        
        print("\n📋 QUICK GUIDE:")
        print("   • Channel 1, 6, 11 are the only non-overlapping 2.4 GHz channels")
        print("   • Lower interference = Faster speeds = Better experience")
        print("   • 5 GHz is faster but has shorter range")
        
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
