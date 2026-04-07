#!/usr/bin/env python3
"""
WA-CPE Wi-Fi Analyzer Dashboard
Web-based dashboard for real-time Wi-Fi analysis
"""

from flask import Flask, render_template_string, jsonify, request, redirect, session, Response
import subprocess
import threading
import time
import os
import sys
import csv
import io
import signal
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.wifi_scanner import WiFiScanner
from modules.interference_detector import InterferenceDetector
from modules.performance_tester import PerformanceTester
from modules.correlation_engine import CorrelationEngine

app = Flask(__name__)
app.secret_key = 'wa-cpe-wifi-analyzer-secret-key-2026'

USERNAME = 'admin'
PASSWORD = 'Logmein@1'

_oui_database = {
    '00:00:00': 'Unknown',
    '00:00:F0': 'Samsung', '00:02:78': 'Samsung', '00:07:AB': 'Samsung', '00:09:18': 'Samsung',
    '00:0D:AE': 'Samsung', '00:0F:73': 'Samsung', '00:12:47': 'Samsung', '00:12:FB': 'Samsung',
    '00:13:77': 'Samsung', '00:15:99': 'Samsung', '00:16:32': 'Samsung', '00:16:6B': 'Samsung',
    '00:16:6C': 'Samsung', '00:17:C9': 'Samsung', '00:17:D5': 'Samsung', '00:18:AF': 'Samsung',
    '00:1A:8A': 'Samsung', '00:1B:98': 'Samsung', '00:1C:43': 'Samsung', '00:1D:25': 'Samsung',
    '00:1D:F6': 'Samsung', '00:1E:7D': 'Samsung', '00:1F:CC': 'Samsung', '00:1F:D1': 'Samsung',
    '00:21:19': 'Samsung', '00:21:4C': 'Samsung', '00:21:D1': 'Samsung', '00:21:D2': 'Samsung',
    '00:23:39': 'Samsung', '00:23:3A': 'Samsung', '00:23:99': 'Samsung', '00:23:D6': 'Samsung',
    '00:23:D7': 'Samsung', '00:24:54': 'Samsung', '00:24:90': 'Samsung', '00:24:91': 'Samsung',
    '00:24:E9': 'Samsung', '00:25:66': 'Samsung', '00:25:67': 'Samsung', '00:26:37': 'Samsung',
    '00:26:5D': 'Samsung', '00:26:5F': 'Samsung', '00:26:6D': 'Samsung', '00:26:AB': 'Samsung',
    '00:26:B7': 'Samsung', '78:25:AD': 'Samsung', '80:65:6D': 'Samsung', '8C:F5:A3': 'Samsung',
    '90:18:7C': 'Samsung', '94:35:0A': 'Samsung', '98:0C:82': 'Samsung', 'A0:07:98': 'Samsung',
    'A0:0B:BA': 'Samsung', 'A0:21:95': 'Samsung', 'A0:3E:FA': 'Samsung', 'A4:07:B6': 'Samsung',
    'A8:23:FE': 'Samsung', 'A8:6D:AA': 'Samsung', 'AC:36:13': 'Samsung', 'AC:5A:14': 'Samsung',
    'AC:5F:3E': 'Samsung', 'B0:47:BF': 'Samsung', 'B0:C5:CA': 'Samsung', 'B4:3A:28': 'Samsung',
    'B4:79:A7': 'Samsung', 'B8:5A:73': 'Samsung', 'B8:D9:CE': 'Samsung', 'BC:44:86': 'Samsung',
    'BC:79:AD': 'Samsung', 'C0:97:27': 'Samsung', 'C4:50:06': 'Samsung', 'C8:19:F7': 'Samsung',
    'C8:38:70': 'Samsung', 'C8:CD:72': 'Samsung', 'CC:07:AB': 'Samsung', 'D0:17:C2': 'Samsung',
    'D0:22:BE': 'Samsung', 'D0:5F:B8': 'Samsung', 'D0:66:7B': 'Samsung', 'D0:87:E2': 'Samsung',
    'D0:AE:5D': 'Samsung', 'D0:B1:FB': 'Samsung', 'D4:87:D8': 'Samsung', 'DC:66:72': 'Samsung',
    'E4:7C:F9': 'Samsung', 'E4:92:FB': 'Samsung', 'E8:03:9A': 'Samsung', 'E8:11:32': 'Samsung',
    'E8:4E:84': 'Samsung', 'EC:1F:72': 'Samsung', 'F0:25:B7': 'Samsung', 'F0:5A:09': 'Samsung',
    'F0:72:8C': 'Samsung', 'F4:09:D8': 'Samsung', 'F4:42:8F': 'Samsung', 'F4:7B:5E': 'Samsung',
    'F8:04:0E': 'Samsung', 'F8:77:B8': 'Samsung', 'F8:8B:37': 'Samsung', 'FC:19:10': 'Samsung',
    '00:03:93': 'Apple', '00:05:69': 'VMware', '00:0C:29': 'VMware', '00:0D:3A': 'Microsoft',
    '00:11:32': 'Synology', '00:13:3C': 'Belkin', '00:14:BF': 'Linksys', '00:17:88': 'Philips',
    '00:1A:22': 'Cisco', '00:1B:63': 'Apple', '00:1C:B3': 'Apple', '00:1D:4F': 'Apple',
    '00:1E:52': 'Apple', '00:1E:C2': 'Apple', '00:1F:5B': 'Apple', '00:1F:F3': 'Apple',
    '00:21:E9': 'Apple', '00:22:41': 'Apple', '00:23:12': 'Apple', '00:23:32': 'Apple',
    '00:23:6C': 'Apple', '00:23:DF': 'Apple', '00:24:36': 'Apple', '00:25:00': 'Apple',
    '00:25:4B': 'Apple', '00:25:BC': 'Apple', '00:26:08': 'Apple', '00:26:4A': 'Apple',
    '00:26:B0': 'Apple', '00:26:BB': 'Apple', '00:50:56': 'VMware', '00:E0:4C': 'Realtek',
    '00:E0:B8': 'AMD', '00:E0:ED': 'Cisco', '00:E1:69': 'Huawei', '00:50:BA': 'D-Link',
    '08:00:20': 'Oracle', '08:00:27': 'VirtualBox', '0C:47:C9': 'Honor', '10:02:B5': 'Intel',
    '14:7D:DA': 'Huawei', '14:FE:B5': 'Netgear', '18:31:BF': 'Huawei', '18:D6:C7': 'TP-Link',
    '1C:1B:0D': 'Giga-Byte', '1C:5A:6B': 'Giga-Byte', '1C:69:7A': 'TP-Link', '20:47:47': 'Dell',
    '24:0A:C4': 'Espressif', '28:6C:07': 'Xiaomi', '2C:33:61': 'Apple', '2C:56:DC': 'Asustek',
    '30:5F:33': 'Giga-Byte', '34:97:F6': 'Asus', '38:2C:4A': 'Asus', '3C:06:30': 'Apple',
    '3C:22:FB': 'Apple', '40:B0:34': 'Apple', '40:B3:95': 'Apple', '44:D8:84': 'Apple',
    '48:43:7C': 'Apple', '48:60:BC': 'Apple', '4C:32:75': 'Apple', '4C:57:CA': 'Asustek',
    '4C:74:BF': 'Apple', '50:32:75': 'Samsung', '50:9F:27': 'Huawei', '54:27:1E': 'Giga-Byte',
    '54:72:4F': 'Arris', '58:00:E3': 'Liteon', '5C:5F:67': 'Huawei', '5C:83:8F': 'Apple',
    '5C:96:9D': 'Apple', '5C:CF:7F': 'Espressif', '60:01:94': 'Espressif', '60:03:08': 'Apple',
    '60:33:0B': 'Giga-Byte', '60:A3:41': 'Apple', '60:F8:1D': 'Liteon', '64:20:0C': 'Apple',
    '64:66:B3': 'Samsung', '64:A2:F9': 'TP-Link', '68:1D:EF': 'Lenovo', '68:96:7B': 'Apple',
    '68:DF:DD': 'Apple', '6C:19:C0': 'Apple', '6C:3E:6D': 'Apple', '6C:40:08': 'Apple',
    '70:11:24': 'Apple', '70:3E:AC': 'Apple', '70:48:0F': 'Apple', '70:56:81': 'Apple',
    '70:73:CB': 'Apple', '70:A2:B3': 'Apple', '70:CD:60': 'Apple', '74:1B:B2': 'Apple',
    '74:70:FD': 'Apple', '78:31:C1': 'Apple', '78:4F:43': 'Apple', '78:88:6D': 'Samsung',
    '78:9F:70': 'Apple', '78:CA:39': 'Apple', '7C:01:91': 'Apple', '7C:04:D0': 'Apple',
    '7C:11:CB': 'Apple', '7C:50:49': 'Apple', '7C:6D:62': 'Apple',
    '80:00:6E': 'Apple', '80:92:9F': 'Apple', '80:B6:86': 'Apple', '80:BE:05': 'Apple',
    '80:E6:50': 'Apple', '84:29:99': 'Apple', '84:38:35': 'Apple', '84:78:8B': 'Apple',
    '84:89:AD': 'TP-Link', '84:8E:0C': 'Apple', '84:FC:AC': 'Apple', '88:53:95': 'Apple',
    '88:66:A5': 'Apple', '88:C3:97': 'Apple', '88:CB:87': 'Apple', '8C:00:6D': 'Apple',
    '8C:2D:AA': 'Apple', '8C:58:77': 'Apple', '8C:85:90': 'Apple', '8C:FA:BA': 'Apple',
    '90:3C:92': 'Apple', '90:72:40': 'Apple', '90:B0:ED': 'Apple', '90:B9:31': 'Apple',
    '94:94:26': 'Apple', '94:E9:79': 'Apple', '94:F6:A3': 'Apple', '98:01:A7': 'Apple',
    '98:03:D8': 'Apple', '98:10:E8': 'Apple', '98:D6:BB': 'Apple', '98:E0:D9': 'Apple',
    '98:F0:7B': 'Apple', '98:FE:94': 'Apple', '9C:04:EB': 'Apple', '9C:20:7B': 'Apple',
    '9C:29:3F': 'Apple', '9C:35:EB': 'Apple', '9C:4F:DA': 'Apple', '9C:84:BF': 'Apple',
    '9C:8B:A0': 'Samsung', '9C:E3:3F': 'Apple', 'A0:18:28': 'Apple', 'A0:D7:95': 'Apple',
    'A0:D8:7F': 'Apple', 'A4:5E:60': 'Apple', 'A4:67:06': 'Apple', 'A4:83:E7': 'Apple',
    'A4:B1:97': 'Apple', 'A4:C3:61': 'Apple', 'A4:D1:D2': 'Apple', 'A4:D1:8C': 'Apple',
    'A4:E9:75': 'Apple', 'A4:F1:E8': 'Apple', 'A8:20:66': 'Apple', 'A8:60:B6': 'Apple',
    'A8:8E:24': 'Apple', 'A8:BB:CF': 'Apple', 'AC:29:3A': 'Apple', 'AC:37:43': 'Apple',
    'AC:3C:0B': 'Apple', 'AC:61:EA': 'Apple', 'AC:7F:3E': 'Apple', 'AC:87:A3': 'Apple',
    'AC:BC:32': 'Apple', 'AC:CF:5C': 'Apple', 'AC:E4:B5': 'Apple', 'B0:34:95': 'Apple',
    'B0:48:1A': 'Apple', 'B0:65:BD': 'Apple', 'B4:18:D1': 'Apple', 'B4:9C:DF': 'Apple',
    'B4:F0:AB': 'Apple', 'B4:F6:1C': 'Apple', 'B8:08:CF': 'Apple', 'B8:17:C2': 'Apple',
    'B8:27:EB': 'Raspberry Pi', 'B8:44:D9': 'Apple', 'B8:5A:73': 'Apple', 'B8:63:4D': 'Apple',
    'B8:6B:23': 'Apple', 'B8:8D:12': 'Apple', 'B8:C1:11': 'Apple', 'B8:E8:56': 'Apple',
    'BC:3B:AF': 'Apple', 'BC:4C:C4': 'Apple', 'BC:52:B7': 'Apple', 'BC:54:36': 'Apple',
    'BC:67:78': 'Apple', 'BC:79:AD': 'Apple', 'BC:83:85': 'Apple', 'BC:92:6B': 'Apple',
    'BC:9F:EF': 'Apple', 'BC:A9:20': 'Apple', 'BC:D1:1F': 'Apple', 'BC:E1:43': 'Apple',
    'C0:84:7A': 'Apple', 'C0:9F:42': 'Apple', 'C0:A5:3E': 'Apple', 'C0:CC:F8': 'Apple',
    'C0:CE:CD': 'Apple', 'C0:D0:12': 'Apple', 'C4:2C:03': 'Apple', 'C4:B3:01': 'Apple',
    'C4:D9:87': 'Apple', 'C4:E9:84': 'Apple', 'C8:1E:E7': 'Apple', 'C8:2A:14': 'Apple',
    'C8:33:4B': 'Apple', 'C8:3C:85': 'Apple', 'C8:69:CD': 'Apple', 'C8:6F:1D': 'Apple',
    'C8:85:50': 'Apple', 'C8:B5:B7': 'Apple', 'CC:08:8D': 'Apple', 'CC:20:E8': 'Apple',
    'CC:25:EF': 'Apple', 'CC:29:F5': 'Apple', 'CC:44:63': 'Apple', 'CC:68:B8': 'Apple',
    'CC:78:5F': 'Apple', 'CC:8E:A2': 'Apple', 'CC:C7:60': 'Apple', 'D0:03:4B': 'Apple',
    'D0:23:DB': 'Apple', 'D0:25:98': 'Apple', 'D0:33:11': 'Apple', 'D0:4F:7E': 'Apple',
    'D0:A6:37': 'Apple', 'D0:C5:F3': 'Apple', 'D0:D2:B0': 'Apple', 'D4:61:9D': 'Apple',
    'D4:9A:20': 'Apple', 'D4:A3:3D': 'Apple', 'D4:DC:CD': 'Apple', 'D8:00:4D': 'Apple',
    'D8:1D:72': 'Apple', 'D8:30:62': 'Apple', 'D8:8F:76': 'Apple', 'DC:2B:2A': 'Apple',
    'DC:41:5F': 'Apple', 'DC:56:E7': 'Apple', 'DC:86:D8': 'Apple', 'DC:9B:9C': 'Apple',
    'DC:A4:CA': 'Apple', 'DC:A9:04': 'Apple', 'DC:CO:53': 'Samsung', 'E0:5F:45': 'Apple',
    'E0:66:78': 'Apple', 'E0:B9:BA': 'Apple', 'E0:C7:67': 'Apple', 'E0:C9:7A': 'Apple',
    'E0:F5:C6': 'Apple', 'E4:25:E7': 'Apple', 'E4:8B:5F': 'Apple', 'E4:9A:DC': 'Apple',
    'E4:C6:3D': 'Apple', 'E4:E4:AB': 'Apple', 'E8:04:0B': 'Apple', 'E8:80:2E': 'Apple',
    'E8:B2:AC': 'Apple', 'E8:BC:32': 'Apple', 'E8:BD:D2': 'Apple', 'E8:C7:7F': 'Apple',
    'EC:35:86': 'Apple', 'EC:85:2F': 'Apple', 'EC:9A:74': 'Apple', 'EC:9B:F3': 'Apple',
    'F0:24:75': 'Apple', 'F0:4D:A2': 'Apple', 'F0:72:8C': 'Apple', 'F0:79:60': 'Apple',
    'F0:99:BF': 'Apple', 'F0:B0:E7': 'Apple', 'F0:B4:79': 'Apple', 'F0:CB:A1': 'Apple',
    'F0:D1:A9': 'Apple', 'F0:DB:E2': 'Apple', 'F0:DC:E2': 'Apple', 'F4:0F:24': 'Apple',
    'F4:31:C3': 'Apple', 'F4:37:B7': 'Apple', 'F4:61:90': 'TP-Link', 'F4:F1:5A': 'Apple',
    'F4:F5:D8': 'Apple', 'F4:F9:51': 'Apple', 'F8:27:C2': 'Apple', 'F8:1E:DF': 'Apple',
    'F8:2D:7C': 'Samsung', 'F8:38:80': 'Apple', 'F8:62:14': 'Apple', 'F8:95:2A': 'Apple',
    'FC:18:3C': 'Apple', 'FC:25:3F': 'Apple', 'FC:2F:40': 'Apple', 'FC:3F:DB': 'Apple',
    'FC:A1:3E': 'Samsung', 'FC:CF:62': 'Apple', 'FC:D8:48': 'Apple', 'FC:E9:98': 'Apple',
    '18:FE:34': 'Espressif', '24:0A:C4': 'Espressif', '2C:3A:E8': 'Espressif', '24:62:AB': 'Espressif',
    '5C:CF:7F': 'Espressif', '60:01:94': 'Espressif', '84:0D:8E': 'Espressif', '84:CC:A8': 'Espressif',
    '84:CF:BF': 'Espressif', '84:F3:EB': 'Espressif', '8C:AA:B5': 'Espressif', '90:97:D5': 'Espressif',
    '98:CD:AC': 'Espressif', 'A4:7B:9D': 'Espressif', 'AC:67:B2': 'Espressif', 'AC:D0:74': 'Espressif',
    'B4:E6:2D': 'Espressif', 'C4:4F:33': 'Espressif', 'C8:2B:96': 'Espressif', 'CC:50:E3': 'Espressif',
    'D8:A0:1D': 'Espressif', 'D8:BF:C0': 'Espressif', 'DC:4F:22': 'Espressif', 'EC:FA:BC': 'Espressif',
    'F4:CF:A2': 'Espressif', 'F8:F0:05': 'Espressif', '30:AE:A4': 'Espressif', '24:6F:28': 'Espressif',
    '00:17:88': 'Philips Hue', 'DC:1564': 'Philips Hue', 'EC:B5:FA': 'Philips Hue', '001CF5': 'Philips Hue',
    'A4C138': 'Philips Hue', 'ECB5FA': 'Philips Hue', 'EC1565': 'Philips Hue', 'D0:73:D5': 'Broadcom',
    '94:10:3E': 'Dell', '18:A9:9B': 'Dell', '00:14:22': 'Dell', '14:18:77': 'Dell', '34:E6:D7': 'Dell',
    '74:86:7A': 'Dell', '00:1E:4F': 'Dell', '18:03:73': 'Dell', '00:21:70': 'Dell', '14:B3:1F': 'Dell',
    '14:FE:B5': 'Netgear', 'C0:FF:D4': 'Netgear', '20:4E:7F': 'Netgear', 'B0:7F:B9': 'Netgear',
    '00:14:6C': 'Netgear', '00:1B:2F': 'Netgear', '2C:B0:5D': 'Netgear', '30:46:9A': 'Netgear',
    '2C:56:DC': 'Asus', '00:1E:8C': 'Asus', '00:1F:C6': 'Asus', '00:22:15': 'Asus', '00:24:8C': 'Asus',
    '00:26:18': 'Asus', '08:60:6E': 'Asus', '10:BF:48': 'Asus', '14:DA:E9': 'Asus', '1C:87:2C': 'Asus',
    '20:CF:30': 'Asus', '2C:4D:70': 'Asus', '2C:5A:11': 'Asus', '30:5A:3A': 'Asus', '34:97:F6': 'Asus',
    '38:2C:4A': 'Asus', '3C:97:0E': 'Asus', '40:16:7E': 'Asus', '40:B0:76': 'Asus', '48:5B:39': 'Asus',
    '4C:ED:FB': 'Asus', '50:46:5D': 'Asus', '54:04:A6': 'Asus', '60:A4:4C': 'Asus', '60:E3:27': 'Asus',
    '74:D4:35': 'Asus', '78:24:AF': 'Asus', '88:D7:F6': 'Asus', '90:E6:BA': 'Asus', '9C:5C:8E': 'Asus',
    'A8:5E:45': 'Asus', 'AC:22:0B': 'Asus', 'AC:9E:17': 'Asus', 'B0:6E:BF': 'Asus', 'BC:AE:C5': 'Asus',
    'C8:60:00': 'Asus', 'D8:50:E6': 'Asus', 'E0:3F:49': 'Asus', 'E0:CB:1D': 'Asus', 'F4:6D:04': 'Asus',
    'F8:32:E4': 'Asus', 'FC:C2:DE': 'Asus', '00:24:01': 'D-Link', '00:1B:11': 'D-Link', '00:22:B0': 'D-Link',
    '00:1E:58': 'D-Link', '1C:AF:05': 'D-Link', '28:10:7B': 'D-Link', '34:08:04': 'D-Link', '5C:D9:98': 'D-Link',
    '78:32:3B': 'D-Link', '84:C9:B2': 'D-Link', '90:94:E4': 'D-Link', '9C:D6:43': 'D-Link', '00:17:3F': 'D-Link',
    '00:1F:F3': 'Wistron', '04:4B:ED': 'Apple', '04:D3:CF': 'Apple', '04:E5:36': 'Apple', '04:F1:3E': 'Apple',
    '08:66:98': 'Apple', '08:6D:41': 'Apple', '0C:15:39': 'Apple', '0C:3E:9F': 'Apple', '0C:77:1A': 'Apple',
    '0C:BD:83': 'Apple', '10:40:F3': 'Apple', '10:68:3F': 'Apple', '10:9A:DD': 'Apple', '10:DD:B1': 'Apple',
    '14:10:9F': 'Apple', '14:99:E2': 'Apple', '14:A5:1A': 'Apple', '14:CC:20': 'Apple', '14:DD:A9': 'Apple',
    '18:20:FF': 'Apple', '18:34:51': 'Apple', '18:65:90': 'Apple', '18:81:0E': 'Apple', '18:9E:FC': 'Apple',
    '18:AF:61': 'Apple', '18:AF:8F': 'Apple', '18:E7:F4': 'Apple', '18:EE:69': 'Apple', '18:F6:43': 'Apple',
    '1C:1A:C0': 'Apple', '1C:36:BB': 'Apple', '1C:5C:F2': 'Apple', '1C:91:48': 'Apple', '1C:9E:46': 'Apple',
    '1C:AB:A7': 'Apple', '1C:E6:2B': 'Apple', '20:7D:74': 'Apple', '20:AB:37': 'Apple', '20:C9:D0': 'Apple',
    '24:A0:74': 'Apple', '24:AB:81': 'Apple', '24:E3:14': 'Apple', '24:F0:94': 'Apple', '24:F6:77': 'Apple',
    '28:0B:5C': 'Apple', '28:37:37': 'Apple', '28:3F:69': 'Apple', '28:5A:BA': 'Apple', '28:6A:B8': 'Apple',
    '28:A0:2B': 'Apple', '28:E1:4C': 'Apple', '28:E7:CF': 'Apple', '28:ED:6A': 'Apple', '28:FD:89': 'Apple',
    '2C:1F:23': 'Apple', '2C:20:0B': 'Apple', '2C:33:61': 'Apple', '2C:36:A0': 'Apple', '2C:3A:E8': 'Apple',
    '2C:61:F6': 'Apple', '2C:BE:08': 'Apple', '2C:D0:2A': 'Apple', '30:63:6B': 'Apple', '30:90:AB': 'Apple',
    '30:C8:2A': 'Apple', '30:F7:C5': 'Apple', '34:08:BC': 'Apple', '34:15:9E': 'Apple', '34:36:3B': 'Apple',
    '34:51:C9': 'Apple', '34:73:5A': 'Apple', '34:A3:95': 'Apple', '34:AB:37': 'Apple', '34:C0:59': 'Apple',
    '34:CE:00': 'Apple', '38:0F:4A': 'Apple', '38:53:9C': 'Apple', '38:71:DE': 'Apple', '38:79:BC': 'Apple',
    '38:C9:86': 'Apple', '38:CA:8A': 'Apple', '38:ED:18': 'Apple', '38:F9:4E': 'Apple', '3C:06:30': 'Apple',
    '3C:15:C2': 'Apple', '3C:2E:F9': 'Apple', '3C:2E:FF': 'Apple', '3C:5A:37': 'Apple', '3C:7A:B0': 'Apple',
    '3C:7D:63': 'Apple', '3C:D0:F8': 'Apple', '3C:D9:1B': 'Apple', '3C:E1:A6': 'Apple', '3C:E9:43': 'Apple',
    '40:30:04': 'Apple', '40:33:1A': 'Apple', '40:3C:FC': 'Apple', '40:4D:8E': 'Apple', '40:50:7D': 'Apple',
    '40:6A:AB': 'Apple', '40:88:05': 'Apple', '40:B0:34': 'Apple', '40:B0:FA': 'Apple', '40:D3:2D': 'Apple',
    '44:00:10': 'Apple', '44:2A:60': 'Apple', '44:74:6C': 'Apple', '44:D8:84': 'Apple', '44:E8:42': 'Apple',
    '44:FB:42': 'Apple', '48:43:7C': 'Apple', '48:53:DD': 'Apple', '48:5D:60': 'Apple', '48:60:BC': 'Apple',
    '48:63:R1': 'Samsung', '48:BF:6B': 'Samsung', '4C:8D:79': 'Samsung', '4C:32:75': 'Apple', '4C:3C:16': 'Apple',
    '4C:57:CA': 'Asus', '4C:74:BF': 'Apple', '4C:B1:6C': 'Apple', '4C:D2:46': 'Apple', '4C:E9:84': 'Apple',
    '50:01:BB': 'Apple', '50:06:04': 'Apple', '50:32:75': 'Samsung', '50:3E:AA': 'Apple', '50:9F:27': 'Huawei',
    '54:26:96': 'Apple', '54:27:1E': 'Giga-Byte', '54:4E:90': 'Apple', '54:72:4F': 'Arris', '54:89:98': 'Apple',
    '54:9F:13': 'Apple', '54:AA:0D': 'Apple', '54:E4:3A': 'Apple', '58:00:E3': 'Liteon', '58:55:CA': 'Apple',
    '58:B0:35': 'Apple', '5C:5F:67': 'Huawei', '5C:59:48': 'Apple', '5C:70:73': 'Apple', '5C:83:8F': 'Apple',
    '5C:8D:4E': 'Apple', '5C:8F:73': 'Apple', '5C:96:9D': 'Apple', '5C:AD:CF': 'Apple', '5C:EE:1E': 'Apple',
    '5C:F5:DA': 'Apple', '5C:F7:E6': 'Apple', '5D:10:CF': 'Apple', '60:03:08': 'Apple', '60:33:0B': 'Giga-Byte',
    '60:44:F8': 'Apple', '60:69:44': 'Apple', '60:6C:66': 'Apple', '60:7B:BB': 'Apple', '60:8A:10': 'Apple',
    '60:9A:7C': 'Apple', '60:A3:41': 'Apple', '60:D9:C7': 'Apple', '60:F8:1D': 'Liteon', '64:20:0C': 'Apple',
    '64:66:B3': 'Samsung', '64:76:BA': 'Apple', '64:88:FF': 'Apple', '64:94:F8': 'Apple', '64:9A:8C': 'Apple',
    '64:A2:F9': 'TP-Link', '64:B7:08': 'Apple', '64:D9:12': 'Apple', '64:E6:82': 'Apple', '64:F7:23': 'Apple',
    '68:1D:EF': 'Lenovo', '68:5B:35': 'Apple', '68:64:4B': 'Apple', '68:78:48': 'Apple', '68:84:70': 'Apple',
    '68:88:09': 'Apple', '68:96:7B': 'Apple', '68:A8:28': 'Apple', '68:AB:1E': 'Apple', '68:C0:0F': 'Apple',
    '68:DF:DD': 'Apple', '6C:19:C0': 'Apple', '6C:3E:6D': 'Apple', '6C:40:08': 'Apple', '6C:4D:73': 'Apple',
    '6C:5A:B0': 'Apple', '6C:72:E7': 'Apple', '6C:86:86': 'Apple', '6C:89:7F': 'Apple', '6C:8D:C1': 'Apple',
    '6C:94:F8': 'Apple', '6C:96:CF': 'Apple', '6C:9B:02': 'Apple', '6C:9D:47': 'Apple', '70:11:24': 'Apple',
    '70:3E:AC': 'Apple', '70:48:0F': 'Apple', '70:56:81': 'Apple', '70:73:CB': 'Apple', '70:8A:09': 'Apple',
    '70:8D:92': 'Apple', '70:99:1C': 'Apple', '70:A2:B3': 'Apple', '70:CD:60': 'Apple', '70:E7:67': 'Apple',
    '74:E1:B6': 'Apple', '74:E5:43': 'Apple', '74:EF:C4': 'Apple', '74:F0:6D': 'Apple', '78:31:C1': 'Apple',
    '78:4F:43': 'Apple', '78:6F:49': 'Apple', '78:7B:8A': 'Apple', '78:88:6D': 'Samsung', '78:9F:70': 'Apple',
    '78:9E:D0': 'Apple', '78:A3:E4': 'Apple', '78:CA:39': 'Apple', '78:FD:DE': 'Apple', '7C:01:91': 'Apple',
    '7C:04:D0': 'Apple', '7C:11:CB': 'Apple', '7C:19:9F': 'Apple', '7C:50:49': 'Apple', '7C:6D:62': 'Apple',
    '7C:7A:91': 'Apple', '7C:D1:90': 'Apple', '7C:D3:0A': 'Apple', '80:00:6E': 'Apple', '80:49:71': 'Apple',
    '80:5E:0C': 'Apple', '80:61:5F': 'Apple', '80:6C:9A': 'Apple', '80:92:9F': 'Apple', '80:9B:20': 'Apple',
    '80:A5:1F': 'Apple', '80:B6:86': 'Apple', '80:BE:05': 'Apple', '80:E6:50': 'Apple', '80:EA:96': 'Apple',
    '84:29:99': 'Apple', '84:38:35': 'Apple', '84:78:8B': 'Apple', '84:89:AD': 'TP-Link', '84:8E:0C': 'Apple',
    '84:9F:03': 'Apple', '84:B1:53': 'Apple', '84:B5:41': 'Apple', '84:FC:AC': 'Apple', '88:19:08': 'Apple',
    '88:53:95': 'Apple', '88:66:A5': 'Apple', '88:C3:97': 'Apple', '88:CB:87': 'Apple', '88:E8:7F': 'Apple',
    '88:FA:48': 'Apple', '8C:00:6D': 'Apple', '8C:29:37': 'Apple', '8C:2D:AA': 'Apple', '8C:58:77': 'Apple',
    '8C:7B:9D': 'Apple', '8C:85:90': 'Apple', '8C:8B:6D': 'Apple', '8C:8E:F2': 'Apple', '8C:96:CF': 'Apple',
    '8C:A9:82': 'Apple', '8C:FA:BA': 'Apple', '8C:FC:AF': 'Apple', '90:3C:92': 'Apple', '90:72:40': 'Apple',
    '90:79:70': 'Apple', '90:B0:ED': 'Apple', '90:B9:31': 'Apple', '90:BD:91': 'Apple', '90:C7:1D': 'Apple',
    '90:D7:4F': 'Apple', '90:DB:2E': 'Apple', '94:94:26': 'Apple', '94:E9:6A': 'Apple', '94:E9:79': 'Apple',
    '94:F6:A3': 'Apple', '94:FA:E8': 'Apple', '98:01:A7': 'Apple', '98:03:D8': 'Apple', '98:10:E8': 'Apple',
    '98:3F:51': 'Apple', '98:D6:BB': 'Apple', '98:D9:E3': 'Apple', '98:E0:D9': 'Apple', '98:F0:7B': 'Apple',
    '98:FE:94': 'Apple', '9C:04:EB': 'Apple', '9C:20:7B': 'Apple', '9C:29:3F': 'Apple', '9C:35:EB': 'Apple',
    '9C:4F:DA': 'Apple', '9C:5C:8E': 'Asus', '9C:84:BF': 'Apple', '9C:88:1C': 'Apple', '9C:8B:A0': 'Samsung',
    '9C:E3:3F': 'Apple', 'A0:18:28': 'Apple', 'A0:D7:95': 'Apple', 'A0:D8:7F': 'Apple', 'A0:ED:CD': 'Apple',
    'A4:3B:18': 'Apple', 'A4:5E:60': 'Apple', 'A4:67:06': 'Apple', 'A4:83:E7': 'Apple', 'A4:B1:97': 'Apple',
    'A4:C3:61': 'Apple', 'A4:D1:D2': 'Apple', 'A4:D1:8C': 'Apple', 'A4:D9:A6': 'Apple', 'A4:E9:75': 'Apple',
    'A4:F1:E8': 'Apple', 'A8:20:66': 'Apple', 'A8:5E:45': 'Asus', 'A8:60:B6': 'Apple', 'A8:8E:24': 'Apple',
    'A8:8F:D9': 'Apple', 'A8:BB:CF': 'Apple', 'A8:BE:27': 'Apple', 'AC:29:3A': 'Apple', 'AC:37:43': 'Apple',
    'AC:3C:0B': 'Apple', 'AC:51:F4': 'Apple', 'AC:61:EA': 'Apple', 'AC:7F:3E': 'Apple', 'AC:87:A3': 'Apple',
    'AC:8B:A9': 'Apple', 'AC:8E:4C': 'Apple', 'AC:9E:17': 'Asus', 'AC:BC:32': 'Apple', 'AC:CF:5C': 'Apple',
    'AC:E4:B5': 'Apple', 'AC:E5:D9': 'Apple', 'AC:FD:CE': 'Apple', 'AC:FF:BC': 'Apple', 'B0:19:C6': 'Apple',
    'B0:34:95': 'Apple', 'B0:48:1A': 'Apple', 'B0:65:BD': 'Apple', 'B0:6E:BF': 'Asus', 'B0:7F:B9': 'Netgear',
    'B4:18:D1': 'Apple', 'B4:2A:2E': 'Apple', 'B4:9C:DF': 'Apple', 'B4:E9:4A': 'Apple', 'B4:F0:AB': 'Apple',
    'B4:F6:1C': 'Apple', 'B4:FE:5F': 'Apple', 'B8:08:CF': 'Apple', 'B8:17:C2': 'Apple', 'B8:27:EB': 'Raspberry Pi',
    'B8:44:D9': 'Apple', 'B8:5A:73': 'Apple', 'B8:63:4D': 'Apple', 'B8:6B:23': 'Apple', 'B8:7C:01': 'Apple',
    'B8:8D:12': 'Apple', 'B8:C1:11': 'Apple', 'B8:E8:56': 'Apple', 'B8:EC:0E': 'Apple', 'B8:FE:5F': 'Apple',
    'BC:3B:AF': 'Apple', 'BC:4C:C4': 'Apple', 'BC:52:B7': 'Apple', 'BC:54:36': 'Apple', 'BC:67:78': 'Apple',
    'BC:79:AD': 'Apple', 'BC:83:85': 'Apple', 'BC:92:6B': 'Apple', 'BC:9F:EF': 'Apple', 'BC:A9:20': 'Apple',
    'BC:D1:1F': 'Apple', 'BC:E1:43': 'Apple', 'BC:E5:9A': 'Apple', 'BC:E9:1F': 'Apple', 'C0:84:7A': 'Apple',
    'C0:9F:42': 'Apple', 'C0:A5:3E': 'Apple', 'C0:CC:F8': 'Apple', 'C0:CE:CD': 'Apple', 'C0:D0:12': 'Apple',
    'C0:E4:E0': 'Apple', 'C4:2C:03': 'Apple', 'C4:9D:AD': 'Apple', 'C4:B3:01': 'Apple', 'C4:D9:87': 'Apple',
    'C4:E9:84': 'Apple', 'C4:F4:23': 'Apple', 'C8:1E:E7': 'Apple', 'C8:2A:14': 'Apple', 'C8:33:4B': 'Apple',
    'C8:3C:85': 'Apple', 'C8:69:CD': 'Apple', 'C8:6F:1D': 'Apple', 'C8:85:50': 'Apple', 'C8:8E:2D': 'Apple',
    'C8:8F:1C': 'Apple', 'C8:95:4B': 'Apple', 'C8:B5:B7': 'Apple', 'C8:E0:81': 'Apple', 'C8:E2:8A': 'Apple',
    'C8:E5:14': 'Apple', 'C8:FC:38': 'Apple', 'CC:08:8D': 'Apple', 'CC:20:E8': 'Apple', 'CC:25:EF': 'Apple',
    'CC:29:F5': 'Apple', 'CC:44:63': 'Apple', 'CC:68:B8': 'Apple', 'CC:78:5F': 'Apple', 'CC:7A:30': 'Apple',
    'CC:8E:A2': 'Apple', 'CC:89:FD': 'Apple', 'CC:8A:FE': 'Apple', 'CC:C7:60': 'Apple', 'CC:D2:21': 'Apple',
    'D0:03:4B': 'Apple', 'D0:23:DB': 'Apple', 'D0:25:98': 'Apple', 'D0:33:11': 'Apple', 'D0:4F:7E': 'Apple',
    'D0:5F:2A': 'Apple', 'D0:A6:37': 'Apple', 'D0:C5:F3': 'Apple', 'D0:D2:B0': 'Apple', 'D0:E1:40': 'Apple',
    'D0:E7:7D': 'Apple', 'D4:25:8B': 'Apple', 'D4:46:3E': 'Apple', 'D4:61:9D': 'Apple', 'D4:9A:20': 'Apple',
    'D4:9C:72': 'Apple', 'D4:A3:3D': 'Apple', 'D4:DC:CD': 'Apple', 'D4:F4:6F': 'Apple', 'D8:00:4D': 'Apple',
    'D8:1D:72': 'Apple', 'D8:30:62': 'Apple', 'D8:8F:76': 'Apple', 'D8:9C:67': 'Apple', 'D8:BB:2C': 'Apple',
    'D8:CF:9C': 'Apple', 'D8:D1:0A': 'Apple', 'DC:2B:2A': 'Apple', 'DC:41:5F': 'Apple', 'DC:56:E7': 'Apple',
    'DC:86:D8': 'Apple', 'DC:9B:9C': 'Apple', 'DC:A4:CA': 'Apple', 'DC:A9:04': 'Apple', 'DC:A9:1C': 'Apple',
    'DC:AB:8D': 'Apple', 'DC:CO:53': 'Samsung', 'DC:D3:A2': 'Apple', 'DC:E5:5B': 'Apple', 'DC:FF:09': 'Apple',
    'E0:5F:45': 'Apple', 'E0:66:78': 'Apple', 'E0:B9:BA': 'Apple', 'E0:C7:67': 'Apple', 'E0:C9:7A': 'Apple',
    'E0:F5:C6': 'Apple', 'E4:25:E7': 'Apple', 'E4:8B:5F': 'Apple', 'E4:9A:DC': 'Apple', 'E4:C6:3D': 'Apple',
    'E4:E4:AB': 'Apple', 'E4:F4:D6': 'Apple', 'E4:FB:94': 'Apple', 'E8:04:0B': 'Apple', 'E8:1C:84': 'Apple',
    'E8:80:2E': 'Apple', 'E8:8D:28': 'Apple', 'E8:A7:C5': 'Apple', 'E8:B2:AC': 'Apple', 'E8:BC:32': 'Apple',
    'E8:BD:D2': 'Apple', 'E8:C7:7F': 'Apple', 'E8:D7:65': 'Apple', 'E8:F7:24': 'Apple', 'E8:FC:AF': 'Apple',
    'EC:35:86': 'Apple', 'EC:85:2F': 'Apple', 'EC:9A:74': 'Apple', 'EC:9B:F3': 'Apple', 'EC:A2:6C': 'Apple',
    'F0:24:75': 'Apple', 'F0:4D:A2': 'Apple', 'F0:72:8C': 'Apple', 'F0:79:60': 'Apple', 'F0:81:73': 'Apple',
    'F0:99:BF': 'Apple', 'F0:B0:E7': 'Apple', 'F0:B4:79': 'Apple', 'F0:CB:A1': 'Apple', 'F0:CF:65': 'Apple',
    'F0:D1:A9': 'Apple', 'F0:DB:E2': 'Apple', 'F0:DC:E2': 'Apple', 'F0:DC:FE': 'Apple', 'F0:F6:1C': 'Apple',
    'F4:0F:24': 'Apple', 'F4:31:C3': 'Apple', 'F4:37:B7': 'Apple', 'F4:5C:55': 'Apple', 'F4:61:90': 'TP-Link',
    'F4:F1:5A': 'Apple', 'F4:F5:D8': 'Apple', 'F4:F9:51': 'Apple', 'F4:FF:8A': 'Apple', 'F8:27:C2': 'Apple',
    'F8:32:E4': 'Asus', 'F8:1E:DF': 'Apple', 'F8:2D:7C': 'Samsung', 'F8:38:80': 'Apple', 'F8:62:14': 'Apple',
    'F8:68:C2': 'Apple', 'F8:7B:8A': 'Apple', 'F8:95:2A': 'Apple', 'F8:B5:14': 'Apple', 'FC:18:3C': 'Apple',
    'FC:25:3F': 'Apple', 'FC:2F:40': 'Apple', 'FC:3F:DB': 'Apple', 'FC:3F:E4': 'Apple', 'FC:4F:42': 'Apple',
    'FC:A1:3E': 'Samsung', 'FC:C2:DE': 'Asus', 'FC:CF:62': 'Apple', 'FC:D8:48': 'Apple', 'FC:E9:98': 'Apple',
    'FC:FF:FF': 'Intel', '34:02:86': 'Intel', '3C:A9:F4': 'Intel', '00:1E:64': 'Intel', '00:1F:3B': 'Intel',
    '00:20:E0': 'Intel', '00:22:FA': 'Intel', '00:24:D6': 'Intel', '00:24:D7': 'Intel', '00:26:C6': 'Intel',
    '00:26:C7': 'Intel', '00:27:10': 'Intel', '00:7E:56': 'Intel', '08:D4:2C': 'Intel', '18:1D:EA': 'Intel',
    '18:3D:A2': 'Intel', '18:67:B0': 'Intel', '1C:1B:0D': 'Giga-Byte', '1C:5A:6B': 'Giga-Byte',
    '34:13:E8': 'Intel', '40:25:C2': 'Intel', '40:A6:B7': 'Intel', '48:45:20': 'Intel', '4C:34:88': 'Intel',
    '4C:79:BA': 'Intel', '50:E0:85': 'Intel', '58:91:CF': 'Intel', '58:94:6B': 'Intel', '58:A8:39': 'Intel',
    '5C:51:4F': 'Intel', '5C:C3:07': 'Intel', '60:57:18': 'Intel', '64:80:99': 'Intel', '68:05:CA': 'Intel',
    '6C:88:2A': 'Intel', '6C:B0:CE': 'Intel', '70:1C:E7': 'Intel', '74:E5:43': 'Intel', '78:0C:B8': 'Intel',
    '78:92:9C': 'Intel', '78:DD:08': 'Intel', '7C:5C:F8': 'Intel', '80:00:6E': 'Intel', '80:86:F2': 'Intel',
    '80:9B:20': 'Intel', '84:3A:4B': 'Intel', '88:53:95': 'Intel', '8C:70:5A': 'Intel', '90:48:9A': 'Intel',
    '90:4C:E5': 'Intel', '94:65:9C': 'Intel', '98:4F:EE': 'Intel', '9C:4F:DA': 'Intel', '9C:B6:54': 'Intel',
    'A0:36:9F': 'Intel', 'A0:88:5F': 'Intel', 'A4:02:B9': 'Intel', 'A4:34:D9': 'Intel', 'A4:77:33': 'Intel',
    'A4:C4:94': 'Intel', 'A8:6D:AA': 'Intel', 'AC:7B:A1': 'Intel', 'B4:6B:FC': 'Intel', 'B4:B6:76': 'Intel',
    'B4:D5:BD': 'Intel', 'B8:03:05': 'Intel', 'B8:27:EB': 'Raspberry Pi', 'B8:8D:12': 'Intel',
    'BC:0F:64': 'Intel', 'BC:77:37': 'Intel', 'BC:85:1F': 'Intel', 'C8:1E:E7': 'Intel', 'C8:F7:50': 'Intel',
    'CC:2F:71': 'Intel', 'D0:50:99': 'Intel', 'D4:3D:7E': 'Intel', 'D4:3P:7E': 'Samsung',
    'DC:1B:A1': 'Intel', 'DC:53:60': 'Intel', 'DC:71:96': 'Intel', 'E8:B1:FC': 'Intel', 'EC:0E:C4': 'Intel',
    'F8:16:54': 'Intel', 'F8:63:3F': 'Intel', 'F8:94:C2': 'Intel', 'FC:F8:AE': 'Intel', '00:04:23': 'Intel',
    '00:07:E9': 'Intel', '00:0C:F1': 'Intel', '00:0E:35': 'Intel', '00:11:11': 'Intel', '00:12:F0': 'Intel',
    '00:13:02': 'Intel', '00:13:20': 'Intel', '00:13:CE': 'Intel', '00:13:D3': 'Intel', '00:15:00': 'Intel',
    '00:15:17': 'Intel', '00:16:6F': 'Intel', '00:16:76': 'Intel', '00:16:EA': 'Intel', '00:16:EB': 'Intel',
    '00:18:DE': 'Intel', '00:19:D1': 'Intel', '00:19:D2': 'Intel', '00:1B:21': 'Intel', '00:1B:77': 'Intel',
    '00:1C:BF': 'Intel', '00:1D:E0': 'Intel', '00:1D:E1': 'Intel', '00:1E:64': 'Intel', '00:1E:65': 'Intel',
    '00:1F:3B': 'Intel', '00:20:E0': 'Intel', '00:21:5C': 'Intel', '00:21:5D': 'Intel', '00:21:6A': 'Intel',
    '00:21:6B': 'Intel', '00:21:6C': 'Intel', '00:21:6D': 'Intel', '00:22:FA': 'Intel', '00:23:14': 'Intel',
    '00:24:D6': 'Intel', '00:24:D7': 'Intel', '00:25:00': 'Intel', '00:26:C6': 'Intel', '00:26:C7': 'Intel',
    '00:27:10': 'Intel', '00:7E:56': 'Intel', '08:D4:2C': 'Intel', '00:0D:56': 'Dell', '00:12:3F': 'Dell',
    '00:14:22': 'Dell', '00:15:C5': 'Dell', '00:18:8B': 'Dell', '00:19:B9': 'Dell', '00:1A:A0': 'Dell',
    '00:1C:23': 'Dell', '00:1D:09': 'Dell', '00:1E:4F': 'Dell', '00:1E:C9': 'Dell', '00:21:70': 'Dell',
    '00:21:9B': 'Dell', '00:22:19': 'Dell', '00:23:AE': 'Dell', '00:24:E8': 'Dell', '00:25:64': 'Dell',
    '00:26:B9': 'Dell', '00:04:23': 'Intel', '00:07:E9': 'Intel', '00:0C:F1': 'Intel', '00:0E:35': 'Intel',
    '00:11:11': 'Intel', '00:12:F0': 'Intel', '00:13:02': 'Intel', '00:13:20': 'Intel', '00:13:CE': 'Intel',
    '00:13:D3': 'Intel', '00:15:00': 'Intel', '00:15:17': 'Intel', '00:16:6F': 'Intel', '00:16:76': 'Intel',
    '00:16:EA': 'Intel', '00:16:EB': 'Intel', '00:18:DE': 'Intel', '00:19:D1': 'Intel', '00:19:D2': 'Intel',
    '00:1B:21': 'Intel', '00:1B:77': 'Intel', '00:1C:BF': 'Intel', '00:1D:E0': 'Intel', '00:1D:E1': 'Intel',
    '00:1E:64': 'Intel', '00:1E:65': 'Intel', '00:1F:3B': 'Intel', '00:20:E0': 'Intel', '00:21:5C': 'Intel',
    '00:21:5D': 'Intel', '00:21:6A': 'Intel', '00:21:6B': 'Intel', '00:21:6C': 'Intel', '00:21:6D': 'Intel',
    '00:22:FA': 'Intel', '00:23:14': 'Intel', '00:24:D6': 'Intel', '00:24:D7': 'Intel', '00:25:00': 'Intel',
    '00:26:C6': 'Intel', '00:26:C7': 'Intel', '00:27:10': 'Intel', '00:7E:56': 'Intel', '08:D4:2C': 'Intel',
    '18:1D:EA': 'Intel', '18:3D:A2': 'Intel', '18:67:B0': 'Intel', '1C:1B:0D': 'Giga-Byte', '1C:5A:6B': 'Giga-Byte',
    '34:13:E8': 'Intel', '40:25:C2': 'Intel', '40:A6:B7': 'Intel', '48:45:20': 'Intel', '4C:34:88': 'Intel',
    '4C:79:BA': 'Intel', '50:E0:85': 'Intel', '58:91:CF': 'Intel', '58:94:6B': 'Intel', '58:A8:39': 'Intel',
    '5C:51:4F': 'Intel', '5C:C3:07': 'Intel', '60:57:18': 'Intel', '64:80:99': 'Intel', '68:05:CA': 'Intel',
    '6C:88:2A': 'Intel', '6C:B0:CE': 'Intel', '70:1C:E7': 'Intel', '74:E5:43': 'Intel', '78:0C:B8': 'Intel',
    '78:92:9C': 'Intel', '78:DD:08': 'Intel', '7C:5C:F8': 'Intel', '80:00:6E': 'Intel', '80:86:F2': 'Intel',
    '80:9B:20': 'Intel', '84:3A:4B': 'Intel', '88:53:95': 'Intel', '8C:70:5A': 'Intel', '90:48:9A': 'Intel',
    '90:4C:E5': 'Intel', '94:65:9C': 'Intel', '98:4F:EE': 'Intel', '9C:4F:DA': 'Intel', '9C:B6:54': 'Intel',
    'A0:36:9F': 'Intel', 'A0:88:5F': 'Intel', 'A4:02:B9': 'Intel', 'A4:34:D9': 'Intel', 'A4:77:33': 'Intel',
    'A4:C4:94': 'Intel', 'A8:6D:AA': 'Intel', 'AC:7B:A1': 'Intel', 'B4:6B:FC': 'Intel', 'B4:B6:76': 'Intel',
    'B4:D5:BD': 'Intel', 'B8:03:05': 'Intel', 'B8:8D:12': 'Intel', 'BC:0F:64': 'Intel', 'BC:77:37': 'Intel',
    'BC:85:1F': 'Intel', 'C8:1E:E7': 'Intel', 'C8:F7:50': 'Intel', 'CC:2F:71': 'Intel', 'D0:50:99': 'Intel',
    'D4:3D:7E': 'Intel', 'DC:1B:A1': 'Intel', 'DC:53:60': 'Intel', 'DC:71:96': 'Intel', 'E8:B1:FC': 'Intel',
    'EC:0E:C4': 'Intel', 'F8:16:54': 'Intel', 'F8:63:3F': 'Intel', 'F8:94:C2': 'Intel', 'FC:F8:AE': 'Intel',
    '00:0D:56': 'Dell', '00:12:3F': 'Dell', '00:14:22': 'Dell', '00:15:C5': 'Dell', '00:18:8B': 'Dell',
    '00:19:B9': 'Dell', '00:1A:A0': 'Dell', '00:1C:23': 'Dell', '00:1D:09': 'Dell', '00:1E:4F': 'Dell',
    '00:1E:C9': 'Dell', '00:21:70': 'Dell', '00:21:9B': 'Dell', '00:22:19': 'Dell', '00:23:AE': 'Dell',
    '00:24:E8': 'Dell', '00:25:64': 'Dell', '00:26:B9': 'Dell', '18:D6:C7': 'TP-Link', '1C:69:7A': 'TP-Link',
    '64:A2:F9': 'TP-Link', '84:89:AD': 'TP-Link', '90:F6:52': 'TP-Link', 'C0:25:E9': 'TP-Link',
    'C4:6E:1F': 'TP-Link', 'D8:07:B6': 'TP-Link', 'E8:94:F6': 'TP-Link', 'F4:61:90': 'TP-Link',
    'F8:1A:67': 'TP-Link', '64:9A:8C': 'TP-Link', '00:27:19': 'TP-Link', '10:FE:ED': 'TP-Link',
    '14:CC:20': 'TP-Link', '14:CF:E2': 'TP-Link', '18:A6:F7': 'TP-Link', '1C:3B:F3': 'TP-Link',
    '30:B5:C2': 'TP-Link', '50:C7:BF': 'TP-Link', '54:C8:0F': 'TP-Link', '5C:63:BF': 'TP-Link',
    '5C:89:9A': 'TP-Link', '60:E3:27': 'Asus', '88:C3:97': 'Apple', '08:60:6E': 'Asus', '10:BF:48': 'Asus',
    '14:DA:E9': 'Asus', '1C:87:2C': 'Asus', '20:CF:30': 'Asus', '2C:4D:70': 'Asus', '2C:5A:11': 'Asus',
    '30:5A:3A': 'Asus', '34:97:F6': 'Asus', '38:2C:4A': 'Asus', '3C:97:0E': 'Asus', '40:16:7E': 'Asus',
    '40:B0:76': 'Asus', '48:5B:39': 'Asus', '4C:ED:FB': 'Asus', '50:46:5D': 'Asus', '54:04:A6': 'Asus',
    '60:A4:4C': 'Asus', '74:D4:35': 'Asus', '78:24:AF': 'Asus', '88:D7:F6': 'Asus', '90:E6:BA': 'Asus',
    '9C:5C:8E': 'Asus', 'A8:5E:45': 'Asus', 'AC:22:0B': 'Asus', 'AC:9E:17': 'Asus', 'B0:6E:BF': 'Asus',
    'BC:AE:C5': 'Asus', 'C8:60:00': 'Asus', 'D8:50:E6': 'Asus', 'E0:3F:49': 'Asus', 'E0:CB:1D': 'Asus',
    'F4:6D:04': 'Asus', 'F8:32:E4': 'Asus', 'FC:C2:DE': 'Asus', '20:4E:7F': 'Netgear', 'B0:7F:B9': 'Netgear',
    '00:14:6C': 'Netgear', '00:1B:2F': 'Netgear', '2C:B0:5D': 'Netgear', '30:46:9A': 'Netgear',
    '14:FE:B5': 'Netgear', 'C0:FF:D4': 'Netgear', '00:24:01': 'D-Link', '00:1B:11': 'D-Link', '00:22:B0': 'D-Link',
    '00:1E:58': 'D-Link', '1C:AF:05': 'D-Link', '28:10:7B': 'D-Link', '34:08:04': 'D-Link', '5C:D9:98': 'D-Link',
    '78:32:3B': 'D-Link', '84:C9:B2': 'D-Link', '90:94:E4': 'D-Link', '9C:D6:43': 'D-Link',
    '00:24:01': 'D-Link', '00:1B:11': 'D-Link', '00:22:B0': 'D-Link', '00:1E:58': 'D-Link', '1C:AF:05': 'D-Link',
    '28:10:7B': 'D-Link', '34:08:04': 'D-Link', '5C:D9:98': 'D-Link', '78:32:3B': 'D-Link', '84:C9:B2': 'D-Link',
    '90:94:E4': 'D-Link', '9C:D6:43': 'D-Link', '00:17:3F': 'D-Link', '00:1F:F3': 'Wistron',
    '04:4B:ED': 'Apple', '04:D3:CF': 'Apple', '04:E5:36': 'Apple', '04:F1:3E': 'Apple', '08:66:98': 'Apple',
    '08:6D:41': 'Apple', '0C:15:39': 'Apple', '0C:3E:9F': 'Apple', '0C:77:1A': 'Apple', '0C:BD:83': 'Apple',
    '10:40:F3': 'Apple', '10:68:3F': 'Apple', '10:9A:DD': 'Apple', '10:DD:B1': 'Apple', '14:10:9F': 'Apple',
    '14:99:E2': 'Apple', '14:A5:1A': 'Apple', '14:CC:20': 'Apple', '14:DD:A9': 'Apple', '18:20:FF': 'Apple',
    '18:34:51': 'Apple', '18:65:90': 'Apple', '18:81:0E': 'Apple', '18:9E:FC': 'Apple', '18:AF:61': 'Apple',
    '18:AF:8F': 'Apple', '18:E7:F4': 'Apple', '18:EE:69': 'Apple', '18:F6:43': 'Apple', '1C:1A:C0': 'Apple',
    '1C:36:BB': 'Apple', '1C:5C:F2': 'Apple', '1C:91:48': 'Apple', '1C:9E:46': 'Apple', '1C:AB:A7': 'Apple',
    '1C:E6:2B': 'Apple', '20:7D:74': 'Apple', '20:AB:37': 'Apple', '20:C9:D0': 'Apple', '24:A0:74': 'Apple',
    '24:AB:81': 'Apple', '24:E3:14': 'Apple', '24:F0:94': 'Apple', '24:F6:77': 'Apple', '28:0B:5C': 'Apple',
    '28:37:37': 'Apple', '28:3F:69': 'Apple', '28:5A:BA': 'Apple', '28:6A:B8': 'Apple', '28:A0:2B': 'Apple',
    '28:E1:4C': 'Apple', '28:E7:CF': 'Apple', '28:ED:6A': 'Apple', '28:FD:89': 'Apple', '2C:1F:23': 'Apple',
    '2C:20:0B': 'Apple', '2C:33:61': 'Apple', '2C:36:A0': 'Apple', '2C:3A:E8': 'Apple', '2C:61:F6': 'Apple',
    '2C:BE:08': 'Apple', '2C:D0:2A': 'Apple', '30:63:6B': 'Apple', '30:90:AB': 'Apple', '30:C8:2A': 'Apple',
    '30:F7:C5': 'Apple', '34:08:BC': 'Apple', '34:15:9E': 'Apple', '34:36:3B': 'Apple', '34:51:C9': 'Apple',
    '34:73:5A': 'Apple', '34:A3:95': 'Apple', '34:AB:37': 'Apple', '34:C0:59': 'Apple', '34:CE:00': 'Apple',
    '38:0F:4A': 'Apple', '38:53:9C': 'Apple', '38:71:DE': 'Apple', '38:79:BC': 'Apple', '38:C9:86': 'Apple',
    '38:CA:8A': 'Apple', '38:ED:18': 'Apple', '38:F9:4E': 'Apple', '3C:06:30': 'Apple', '3C:15:C2': 'Apple',
    '3C:2E:F9': 'Apple', '3C:2E:FF': 'Apple', '3C:5A:37': 'Apple', '3C:7A:B0': 'Apple', '3C:7D:63': 'Apple',
    '3C:D0:F8': 'Apple', '3C:D9:1B': 'Apple', '3C:E1:A6': 'Apple', '3C:E9:43': 'Apple', '40:30:04': 'Apple',
    '40:33:1A': 'Apple', '40:3C:FC': 'Apple', '40:4D:8E': 'Apple', '40:50:7D': 'Apple', '40:6A:AB': 'Apple',
    '40:88:05': 'Apple', '40:B0:34': 'Apple', '40:B0:FA': 'Apple', '40:D3:2D': 'Apple', '44:00:10': 'Apple',
    '44:2A:60': 'Apple', '44:74:6C': 'Apple', '44:D8:84': 'Apple', '44:E8:42': 'Apple', '44:FB:42': 'Apple',
    '48:43:7C': 'Apple', '48:53:DD': 'Apple', '48:5D:60': 'Apple', '48:60:BC': 'Apple', '50:01:BB': 'Apple',
    '50:06:04': 'Apple', '50:32:75': 'Samsung', '50:3E:AA': 'Apple', '50:9F:27': 'Huawei', '54:26:96': 'Apple',
    '54:27:1E': 'Giga-Byte', '54:4E:90': 'Apple', '54:72:4F': 'Arris', '54:89:98': 'Apple', '54:9F:13': 'Apple',
    '54:AA:0D': 'Apple', '54:E4:3A': 'Apple', '58:00:E3': 'Liteon', '58:55:CA': 'Apple', '58:B0:35': 'Apple',
    '5C:5F:67': 'Huawei', '5C:59:48': 'Apple', '5C:70:73': 'Apple', '5C:83:8F': 'Apple', '5C:8D:4E': 'Apple',
    '5C:8F:73': 'Apple', '5C:96:9D': 'Apple', '5C:AD:CF': 'Apple', '5C:EE:1E': 'Apple', '5C:F5:DA': 'Apple',
    '5C:F7:E6': 'Apple', '5D:10:CF': 'Apple', '60:03:08': 'Apple', '60:33:0B': 'Giga-Byte', '60:44:F8': 'Apple',
    '60:69:44': 'Apple', '60:6C:66': 'Apple', '60:7B:BB': 'Apple', '60:8A:10': 'Apple', '60:9A:7C': 'Apple',
    '60:A3:41': 'Apple', '60:D9:C7': 'Apple', '60:F8:1D': 'Liteon', '64:20:0C': 'Apple', '64:66:B3': 'Samsung',
    '64:76:BA': 'Apple', '64:88:FF': 'Apple', '64:94:F8': 'Apple', '64:9A:8C': 'Apple', '64:A2:F9': 'TP-Link',
    '64:B7:08': 'Apple', '64:D9:12': 'Apple', '64:E6:82': 'Apple', '64:F7:23': 'Apple', '68:1D:EF': 'Lenovo',
    '68:5B:35': 'Apple', '68:64:4B': 'Apple', '68:78:48': 'Apple', '68:84:70': 'Apple', '68:88:09': 'Apple',
    '68:96:7B': 'Apple', '68:A8:28': 'Apple', '68:AB:1E': 'Apple', '68:C0:0F': 'Apple', '68:DF:DD': 'Apple',
    '6C:19:C0': 'Apple', '6C:3E:6D': 'Apple', '6C:40:08': 'Apple', '6C:4D:73': 'Apple', '6C:5A:B0': 'Apple',
    '6C:72:E7': 'Apple', '6C:86:86': 'Apple', '6C:89:7F': 'Apple', '6C:8D:C1': 'Apple', '6C:94:F8': 'Apple',
    '6C:96:CF': 'Apple', '6C:9B:02': 'Apple', '6C:9D:47': 'Apple', '70:11:24': 'Apple', '70:3E:AC': 'Apple',
    '70:48:0F': 'Apple', '70:56:81': 'Apple', '70:73:CB': 'Apple', '70:8A:09': 'Apple', '70:8D:92': 'Apple',
    '70:99:1C': 'Apple', '70:A2:B3': 'Apple', '70:CD:60': 'Apple', '70:E7:67': 'Apple', '74:E1:B6': 'Apple',
    '74:E5:43': 'Apple', '74:EF:C4': 'Apple', '74:F0:6D': 'Apple', '78:31:C1': 'Apple', '78:4F:43': 'Apple',
    '78:6F:49': 'Apple', '78:7B:8A': 'Apple', '78:88:6D': 'Samsung', '78:9F:70': 'Apple', '78:9E:D0': 'Apple',
    '78:A3:E4': 'Apple', '78:CA:39': 'Apple', '78:FD:DE': 'Apple', '7C:01:91': 'Apple', '7C:04:D0': 'Apple',
    '7C:11:CB': 'Apple', '7C:19:9F': 'Apple', '7C:50:49': 'Apple', '7C:6D:62': 'Apple', '7C:7A:91': 'Apple',
    '7C:D1:90': 'Apple', '7C:D3:0A': 'Apple', '80:00:6E': 'Apple', '80:49:71': 'Apple', '80:5E:0C': 'Apple',
    '80:61:5F': 'Apple', '80:6C:9A': 'Apple', '80:92:9F': 'Apple', '80:9B:20': 'Apple', '80:A5:1F': 'Apple',
    '80:B6:86': 'Apple', '80:BE:05': 'Apple', '80:E6:50': 'Apple', '80:EA:96': 'Apple', '84:29:99': 'Apple',
    '84:38:35': 'Apple', '84:78:8B': 'Apple', '84:89:AD': 'TP-Link', '84:8E:0C': 'Apple', '84:9F:03': 'Apple',
    '84:B1:53': 'Apple', '84:B5:41': 'Apple', '84:FC:AC': 'Apple', '88:19:08': 'Apple', '88:53:95': 'Apple',
    '88:66:A5': 'Apple', '88:C3:97': 'Apple', '88:CB:87': 'Apple', '88:E8:7F': 'Apple', '88:FA:48': 'Apple',
    '8C:00:6D': 'Apple', '8C:29:37': 'Apple', '8C:2D:AA': 'Apple', '8C:58:77': 'Apple', '8C:7B:9D': 'Apple',
    '8C:85:90': 'Apple', '8C:8B:6D': 'Apple', '8C:8E:F2': 'Apple', '8C:96:CF': 'Apple', '8C:A9:82': 'Apple',
    '8C:FA:BA': 'Apple', '8C:FC:AF': 'Apple', '90:3C:92': 'Apple', '90:72:40': 'Apple', '90:79:70': 'Apple',
    '90:B0:ED': 'Apple', '90:B9:31': 'Apple', '90:BD:91': 'Apple', '90:C7:1D': 'Apple', '90:D7:4F': 'Apple',
    '90:DB:2E': 'Apple', '94:94:26': 'Apple', '94:E9:6A': 'Apple', '94:E9:79': 'Apple', '94:F6:A3': 'Apple',
    '94:FA:E8': 'Apple', '98:01:A7': 'Apple', '98:03:D8': 'Apple', '98:10:E8': 'Apple', '98:3F:51': 'Apple',
    '98:D6:BB': 'Apple', '98:D9:E3': 'Apple', '98:E0:D9': 'Apple', '98:F0:7B': 'Apple', '98:FE:94': 'Apple',
    '9C:04:EB': 'Apple', '9C:20:7B': 'Apple', '9C:29:3F': 'Apple', '9C:35:EB': 'Apple', '9C:4F:DA': 'Apple',
    '9C:84:BF': 'Apple', '9C:88:1C': 'Apple', '9C:8B:A0': 'Samsung', '9C:E3:3F': 'Apple', 'A0:18:28': 'Apple',
    'A0:D7:95': 'Apple', 'A0:D8:7F': 'Apple', 'A0:ED:CD': 'Apple', 'A4:3B:18': 'Apple', 'A4:5E:60': 'Apple',
    'A4:67:06': 'Apple', 'A4:83:E7': 'Apple', 'A4:B1:97': 'Apple', 'A4:C3:61': 'Apple', 'A4:D1:D2': 'Apple',
    'A4:D1:8C': 'Apple', 'A4:D9:A6': 'Apple', 'A4:E9:75': 'Apple', 'A4:F1:E8': 'Apple', 'A8:20:66': 'Apple',
    'A8:60:B6': 'Apple', 'A8:8E:24': 'Apple', 'A8:8F:D9': 'Apple', 'A8:BB:CF': 'Apple', 'A8:BE:27': 'Apple',
    'AC:29:3A': 'Apple', 'AC:37:43': 'Apple', 'AC:3C:0B': 'Apple', 'AC:51:F4': 'Apple', 'AC:61:EA': 'Apple',
    'AC:7F:3E': 'Apple', 'AC:87:A3': 'Apple', 'AC:8B:A9': 'Apple', 'AC:8E:4C': 'Apple', 'AC:9E:17': 'Asus',
    'AC:BC:32': 'Apple', 'AC:CF:5C': 'Apple', 'AC:E4:B5': 'Apple', 'AC:E5:D9': 'Apple', 'AC:FD:CE': 'Apple',
    'AC:FF:BC': 'Apple', 'B0:19:C6': 'Apple', 'B0:34:95': 'Apple', 'B0:48:1A': 'Apple', 'B0:65:BD': 'Apple',
    'B0:6E:BF': 'Asus', 'B4:18:D1': 'Apple', 'B4:2A:2E': 'Apple', 'B4:9C:DF': 'Apple', 'B4:E9:4A': 'Apple',
    'B4:F0:AB': 'Apple', 'B4:F6:1C': 'Apple', 'B4:FE:5F': 'Apple', 'B8:08:CF': 'Apple', 'B8:17:C2': 'Apple',
    'B8:27:EB': 'Raspberry Pi', 'B8:44:D9': 'Apple', 'B8:5A:73': 'Apple', 'B8:63:4D': 'Apple', 'B8:6B:23': 'Apple',
    'B8:7C:01': 'Apple', 'B8:8D:12': 'Apple', 'B8:C1:11': 'Apple', 'B8:E8:56': 'Apple', 'B8:EC:0E': 'Apple',
    'B8:FE:5F': 'Apple', 'BC:3B:AF': 'Apple', 'BC:4C:C4': 'Apple', 'BC:52:B7': 'Apple', 'BC:54:36': 'Apple',
    'BC:67:78': 'Apple', 'BC:79:AD': 'Apple', 'BC:83:85': 'Apple', 'BC:92:6B': 'Apple', 'BC:9F:EF': 'Apple',
    'BC:A9:20': 'Apple', 'BC:D1:1F': 'Apple', 'BC:E1:43': 'Apple', 'BC:E5:9A': 'Apple', 'BC:E9:1F': 'Apple',
    'C0:84:7A': 'Apple', 'C0:9F:42': 'Apple', 'C0:A5:3E': 'Apple', 'C0:CC:F8': 'Apple', 'C0:CE:CD': 'Apple',
    'C0:D0:12': 'Apple', 'C0:E4:E0': 'Apple', 'C4:2C:03': 'Apple', 'C4:9D:AD': 'Apple', 'C4:B3:01': 'Apple',
    'C4:D9:87': 'Apple', 'C4:E9:84': 'Apple', 'C4:F4:23': 'Apple', 'C8:1E:E7': 'Apple', 'C8:2A:14': 'Apple',
    'C8:33:4B': 'Apple', 'C8:3C:85': 'Apple', 'C8:69:CD': 'Apple', 'C8:6F:1D': 'Apple', 'C8:85:50': 'Apple',
    'C8:8E:2D': 'Apple', 'C8:8F:1C': 'Apple', 'C8:95:4B': 'Apple', 'C8:B5:B7': 'Apple', 'C8:E0:81': 'Apple',
    'C8:E2:8A': 'Apple', 'C8:E5:14': 'Apple', 'C8:FC:38': 'Apple', 'CC:08:8D': 'Apple', 'CC:20:E8': 'Apple',
    'CC:25:EF': 'Apple', 'CC:29:F5': 'Apple', 'CC:44:63': 'Apple', 'CC:68:B8': 'Apple', 'CC:78:5F': 'Apple',
    'CC:7A:30': 'Apple', 'CC:8E:A2': 'Apple', 'CC:89:FD': 'Apple', 'CC:8A:FE': 'Apple', 'CC:C7:60': 'Apple',
    'CC:D2:21': 'Apple', 'D0:03:4B': 'Apple', 'D0:23:DB': 'Apple', 'D0:25:98': 'Apple', 'D0:33:11': 'Apple',
    'D0:4F:7E': 'Apple', 'D0:5F:2A': 'Apple', 'D0:A6:37': 'Apple', 'D0:C5:F3': 'Apple', 'D0:D2:B0': 'Apple',
    'D0:E1:40': 'Apple', 'D0:E7:7D': 'Apple', 'D4:25:8B': 'Apple', 'D4:46:3E': 'Apple', 'D4:61:9D': 'Apple',
    'D4:9A:20': 'Apple', 'D4:9C:72': 'Apple', 'D4:A3:3D': 'Apple', 'D4:DC:CD': 'Apple', 'D4:F4:6F': 'Apple',
    'D8:00:4D': 'Apple', 'D8:1D:72': 'Apple', 'D8:30:62': 'Apple', 'D8:8F:76': 'Apple', 'D8:9C:67': 'Apple',
    'D8:BB:2C': 'Apple', 'D8:CF:9C': 'Apple', 'D8:D1:0A': 'Apple', 'DC:2B:2A': 'Apple', 'DC:41:5F': 'Apple',
    'DC:56:E7': 'Apple', 'DC:86:D8': 'Apple', 'DC:9B:9C': 'Apple', 'DC:A4:CA': 'Apple', 'DC:A9:04': 'Apple',
    'DC:A9:1C': 'Apple', 'DC:AB:8D': 'Apple', 'DC:CO:53': 'Samsung', 'DC:D3:A2': 'Apple', 'DC:E5:5B': 'Apple',
    'DC:FF:09': 'Apple', 'E0:5F:45': 'Apple', 'E0:66:78': 'Apple', 'E0:B9:BA': 'Apple', 'E0:C7:67': 'Apple',
    'E0:C9:7A': 'Apple', 'E0:F5:C6': 'Apple', 'E4:25:E7': 'Apple', 'E4:8B:5F': 'Apple', 'E4:9A:DC': 'Apple',
    'E4:C6:3D': 'Apple', 'E4:E4:AB': 'Apple', 'E4:F4:D6': 'Apple', 'E4:FB:94': 'Apple', 'E8:04:0B': 'Apple',
    'E8:1C:84': 'Apple', 'E8:80:2E': 'Apple', 'E8:8D:28': 'Apple', 'E8:A7:C5': 'Apple', 'E8:B2:AC': 'Apple',
    'E8:BC:32': 'Apple', 'E8:BD:D2': 'Apple', 'E8:C7:7F': 'Apple', 'E8:D7:65': 'Apple', 'E8:F7:24': 'Apple',
    'E8:FC:AF': 'Apple', 'EC:35:86': 'Apple', 'EC:85:2F': 'Apple', 'EC:9A:74': 'Apple', 'EC:9B:F3': 'Apple',
    'EC:A2:6C': 'Apple', 'F0:24:75': 'Apple', 'F0:4D:A2': 'Apple', 'F0:72:8C': 'Apple', 'F0:79:60': 'Apple',
    'F0:81:73': 'Apple', 'F0:99:BF': 'Apple', 'F0:B0:E7': 'Apple', 'F0:B4:79': 'Apple', 'F0:CB:A1': 'Apple',
    'F0:CF:65': 'Apple', 'F0:D1:A9': 'Apple', 'F0:DB:E2': 'Apple', 'F0:DC:E2': 'Apple', 'F0:DC:FE': 'Apple',
    'F0:F6:1C': 'Apple', 'F4:0F:24': 'Apple', 'F4:31:C3': 'Apple', 'F4:37:B7': 'Apple', 'F4:5C:55': 'Apple',
    'F4:61:90': 'TP-Link', 'F4:F1:5A': 'Apple', 'F4:F5:D8': 'Apple', 'F4:F9:51': 'Apple', 'F4:FF:8A': 'Apple',
    'F8:27:C2': 'Apple', 'F8:1E:DF': 'Apple', 'F8:2D:7C': 'Samsung', 'F8:38:80': 'Apple', 'F8:62:14': 'Apple',
    'F8:68:C2': 'Apple', 'F8:7B:8A': 'Apple', 'F8:95:2A': 'Apple', 'F8:B5:14': 'Apple', 'FC:18:3C': 'Apple',
    'FC:25:3F': 'Apple', 'FC:2F:40': 'Apple', 'FC:3F:DB': 'Apple', 'FC:3F:E4': 'Apple', 'FC:4F:42': 'Apple',
    'FC:A1:3E': 'Samsung', 'FC:CF:62': 'Apple', 'FC:D8:48': 'Apple', 'FC:E9:98': 'Apple',
}

def get_manufacturer(mac):
    """Get manufacturer from MAC address"""
    if not mac:
        return 'Unknown'
    mac_prefix = mac.upper().replace('-', ':')
    prefix = ':'.join(mac_prefix.split(':')[:3])
    return _oui_database.get(prefix, 'Unknown')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect('/')
        else:
            return render_template_string(LOGIN_HTML, error='Invalid credentials')
    
    return render_template_string(LOGIN_HTML)

@app.route('/logout')
def logout():
    """Logout"""
    session.pop('logged_in', None)
    return redirect('/login')

def require_auth(f):
    """Decorator to require authentication"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@require_auth
def dashboard():
    """Main dashboard page"""
    return render_template_string(DASHBOARD_HTML)

latest_analysis = {
    'timestamp': None,
    'networks': [],
    'connected_devices': [],
    'searching_devices': [],
    'interference': {'level': 'N/A', 'score': 0},
    'recommendations': [],
    'channel_congestion': {}
}

analyzer_running = False
analyzer_paused = False
analyzer_interface = 'wlan0'
scan_counter = 0

def get_interface_info(interface):
    """Get detailed interface information for verification"""
    info = {'interface': interface, 'adapter': 'TP-Link Archer T2U Plus'}
    
    try:
        mac_path = f'/sys/class/net/{interface}/address'
        with open(mac_path, 'r') as f:
            info['mac_address'] = f.read().strip()
    except:
        info['mac_address'] = 'Unknown'
    
    try:
        driver_path = f'/sys/class/net/{interface}/device/driver'
        driver = os.path.basename(os.readlink(driver_path))
        info['driver'] = driver
    except:
        info['driver'] = 'Unknown'
    
    try:
        result = subprocess.run(['iw', 'dev', interface, 'info'], capture_output=True, text=True, timeout=5)
        info['iw_info'] = result.stdout
    except:
        info['iw_info'] = ''
    
    return info

def get_system_info():
    """Get system information including storage"""
    info = {}
    
    try:
        result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True, timeout=5)
        lines = result.stdout.strip().split('\n')
        if len(lines) >= 2:
            parts = lines[1].split()
            if len(parts) >= 4:
                info['storage_total'] = parts[1]
                info['storage_used'] = parts[2]
                info['storage_free'] = parts[3]
                info['storage_percent'] = parts[4]
    except:
        info['storage_total'] = 'N/A'
        info['storage_used'] = 'N/A'
        info['storage_free'] = 'N/A'
        info['storage_percent'] = 'N/A'
    
    try:
        result = subprocess.run(['free', '-h'], capture_output=True, text=True, timeout=5)
        lines = result.stdout.strip().split('\n')
        for line in lines:
            if line.startswith('Mem:'):
                parts = line.split()
                if len(parts) >= 3:
                    info['memory_total'] = parts[1]
                    info['memory_used'] = parts[2]
                    info['memory_free'] = parts[3] if len(parts) > 3 else 'N/A'
    except:
        info['memory_total'] = 'N/A'
        info['memory_used'] = 'N/A'
        info['memory_free'] = 'N/A'
    
    try:
        result = subprocess.run(['cat', '/proc/loadavg'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            load = result.stdout.strip().split()
            info['load_average'] = f"{load[0]} {load[1]} {load[2]}"
    except:
        info['load_average'] = 'N/A'
    
    return info

def run_analysis():
    """Run continuous analysis in background"""
    global latest_analysis, analyzer_running, analyzer_paused, scan_counter
    
    scanner = WiFiScanner(analyzer_interface)
    detector = InterferenceDetector()
    tester = PerformanceTester(analyzer_interface)
    correlator = CorrelationEngine()
    scan_counter = 0
    
    while analyzer_running:
        scan_counter += 1
        
        if scan_counter % 20 == 0:
            import subprocess
            subprocess.run(['sudo', 'killall', 'airodump-ng'], stderr=subprocess.DEVNULL)
            subprocess.run(['sudo', 'modprobe', '-r', '88XXau'], stderr=subprocess.DEVNULL)
            import time
            time.sleep(2)
            subprocess.run(['sudo', 'modprobe', '88XXau'], stderr=subprocess.DEVNULL)
            time.sleep(3)
            scanner = WiFiScanner(analyzer_interface)
            print(f"Driver reset complete, scan #{scan_counter}")
        
        try:
            if not analyzer_paused:
                scan_result = scanner.scan_networks()
                
                networks = scan_result.get('networks', [])
                probed = scan_result.get('probed_networks', [])
                
                connected = []
                searching = []
                for item in probed:
                    item['manufacturer'] = get_manufacturer(item.get('device_mac', ''))
                    conn_bssid = item.get('connected_bssid', '')
                    if conn_bssid and ':' in conn_bssid:
                        connected.append(item)
                    else:
                        searching.append(item)
                
                interference_data = detector.analyze(networks)
                performance_data = tester.run_all_tests()
                
                correlation = correlator.correlate(
                    {'networks': networks, 'network_count': len(networks)},
                    performance_data,
                    interference_data
                )
                
                print(f"Scan #{scan_counter}: Found {len(networks)} networks, {len(connected)} connected, {len(searching)} searching")
                
                latest_analysis = {
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'networks': networks,
                    'connected_devices': connected,
                    'searching_devices': searching,
                    'interference': correlation.get('interference_impact', {}),
                    'recommendations': interference_data.get('recommendations', {}),
                    'channel_congestion': interference_data.get('channel_congestion', {}),
                    'paused': False
                }
            else:
                latest_analysis['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
                latest_analysis['paused'] = True
                
        except Exception as e:
            import sys
            print(f"Scan error: {e}", file=sys.stderr)
            latest_analysis['error'] = str(e)
            latest_analysis['networks'] = latest_analysis.get('networks', [])
            latest_analysis['connected_devices'] = latest_analysis.get('connected_devices', [])
            latest_analysis['searching_devices'] = latest_analysis.get('searching_devices', [])
        
        time.sleep(2)

@app.route('/api/data')
@require_auth
def get_data():
    """API endpoint for real-time data"""
    data = latest_analysis.copy()
    if not data.get('networks'):
        data['networks'] = []
    if not data.get('connected_devices'):
        data['connected_devices'] = []
    if not data.get('searching_devices'):
        data['searching_devices'] = []
    data['interface_info'] = get_interface_info(analyzer_interface)
    data['system_info'] = get_system_info()
    return jsonify(data)

@app.route('/api/interface-info')
@require_auth
def get_interface_info_api():
    """API endpoint for interface details"""
    return jsonify(get_interface_info(analyzer_interface))

@app.route('/api/networks')
@require_auth
def get_networks():
    """API endpoint for networks only"""
    return jsonify({
        'networks': latest_analysis.get('networks', []),
        'connected': latest_analysis.get('connected_devices', []),
        'searching': latest_analysis.get('searching_devices', [])
    })

@app.route('/api/interference')
@require_auth
def get_interference():
    """API endpoint for interference data"""
    return jsonify({
        'interference': latest_analysis.get('interference', {}),
        'congestion': latest_analysis.get('channel_congestion', {}),
        'recommendations': latest_analysis.get('recommendations', {})
    })

@app.route('/api/pause', methods=['POST'])
@require_auth
def pause_monitoring():
    """Pause live monitoring"""
    global analyzer_paused
    analyzer_paused = True
    return jsonify({'status': 'paused', 'message': 'Monitoring paused'})

@app.route('/api/resume', methods=['POST'])
@require_auth
def resume_monitoring():
    """Resume live monitoring"""
    global analyzer_paused
    analyzer_paused = False
    return jsonify({'status': 'running', 'message': 'Monitoring resumed'})

@app.route('/api/status')
@require_auth
def get_status():
    """Get monitoring status"""
    return jsonify({
        'running': analyzer_running,
        'paused': analyzer_paused
    })

@app.route('/api/export/csv')
@require_auth
def export_csv():
    """Export data as CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Wi-Fi Analyzer Export - ' + (latest_analysis.get('timestamp') or datetime.now().strftime('%Y-%m-%d %H:%M:%S'))])
    writer.writerow([])
    
    writer.writerow(['=== NETWORKS ==='])
    writer.writerow(['SSID', 'BSSID', 'Channel', 'Band', 'RSSI (dBm)', 'Encryption'])
    for net in latest_analysis.get('networks', []):
        writer.writerow([
            net.get('ssid', 'Hidden'),
            net.get('bssid', ''),
            net.get('channel', ''),
            net.get('band', ''),
            net.get('rssi', ''),
            net.get('encryption', '')
        ])
    
    writer.writerow([])
    writer.writerow(['=== CONNECTED DEVICES ==='])
    writer.writerow(['MAC Address', 'Manufacturer', 'Connected BSSID', 'Signal (dBm)', 'Probed SSIDs'])
    for dev in latest_analysis.get('connected_devices', []):
        writer.writerow([
            dev.get('device_mac', ''),
            dev.get('manufacturer', ''),
            dev.get('connected_bssid', ''),
            dev.get('signal', ''),
            ', '.join(dev.get('probed_ssids', []))
        ])
    
    writer.writerow([])
    writer.writerow(['=== SEARCHING DEVICES ==='])
    writer.writerow(['MAC Address', 'Manufacturer', 'Signal (dBm)', 'Probed SSIDs'])
    for dev in latest_analysis.get('searching_devices', []):
        writer.writerow([
            dev.get('device_mac', ''),
            dev.get('manufacturer', ''),
            dev.get('signal', ''),
            ', '.join(dev.get('probed_ssids', []))
        ])
    
    writer.writerow([])
    writer.writerow(['=== INTERFERENCE DATA ==='])
    interf = latest_analysis.get('interference', {})
    writer.writerow(['Level', 'Score'])
    writer.writerow([interf.get('level', 'N/A'), interf.get('score', 0)])
    
    writer.writerow([])
    writer.writerow(['=== CHANNEL CONGESTION (2.4 GHz) ==='])
    writer.writerow(['Channel', 'Network Count', 'Congestion Level'])
    for ch, data in latest_analysis.get('channel_congestion', {}).items():
        if isinstance(data, dict):
            writer.writerow([ch, data.get('network_count', 0), data.get('congestion_level', 'N/A')])
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=wifi_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
    )

@app.route('/api/export/html')
@require_auth
def export_html():
    """Export data as HTML report"""
    timestamp = latest_analysis.get('timestamp') or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    interf = latest_analysis.get('interference', {})
    
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wi-Fi Analysis Report - {timestamp}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #00d9ff; border-bottom: 2px solid #0f3460; padding-bottom: 10px; }}
        h2 {{ color: #0f3460; margin-top: 30px; }}
        .timestamp {{ color: #888; font-size: 14px; margin-bottom: 20px; }}
        .stat-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0; }}
        .stat-box {{ background: #f0f9ff; padding: 20px; border-radius: 10px; text-align: center; }}
        .stat-value {{ font-size: 28px; font-weight: bold; color: #00d9ff; }}
        .stat-label {{ font-size: 12px; color: #666; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th {{ background: #0f3460; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #eee; }}
        tr:hover {{ background: #f5f5f5; }}
        .interference-bar {{ height: 30px; border-radius: 15px; margin: 15px 0; }}
        .level-minimal {{ background: linear-gradient(90deg, #00ff00, #00cc00); }}
        .level-low {{ background: linear-gradient(90deg, #88ff00, #66cc00); }}
        .level-medium {{ background: linear-gradient(90deg, #ffcc00, #ff9900); }}
        .level-high {{ background: linear-gradient(90deg, #ff6600, #ff3300); }}
        .level-critical {{ background: linear-gradient(90deg, #ff0000, #cc0000); }}
        .level-minimal-bg {{ background: #d4edda; }}
        .level-low-bg {{ background: #c3e6cb; }}
        .level-medium-bg {{ background: #fff3cd; }}
        .level-high-bg {{ background: #ffe5d0; }}
        .level-critical-bg {{ background: #f8d7da; }}
        .recommendation {{ background: #e7f3ff; border-left: 4px solid #00d9ff; padding: 15px; margin: 10px 0; border-radius: 0 5px 5px 0; }}
        .footer {{ margin-top: 30px; text-align: center; color: #888; font-size: 12px; }}
        @media print {{ body {{ background: white; }} .container {{ box-shadow: none; }} }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Wi-Fi Analysis Report</h1>
        <p class="timestamp">Generated: {timestamp}</p>
        
        <div class="stat-grid">
            <div class="stat-box">
                <div class="stat-value">{len(latest_analysis.get('networks', []))}</div>
                <div class="stat-label">Networks</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{len(latest_analysis.get('connected_devices', []))}</div>
                <div class="stat-label">Connected Devices</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{len(latest_analysis.get('searching_devices', []))}</div>
                <div class="stat-label">Searching Devices</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{interf.get('score', 0)}</div>
                <div class="stat-label">Interference Score</div>
            </div>
        </div>
        
        <h2>Interference Level: {interf.get('level', 'N/A')}</h2>
        <div class="interference-bar level-{interf.get('level', 'medium').lower()}" style="width: {min(interf.get('score', 50), 100)}%;"></div>
        
        <h2>Detected Networks ({len(latest_analysis.get('networks', []))})</h2>
        <table>
            <tr>
                <th>SSID</th>
                <th>BSSID</th>
                <th>Channel</th>
                <th>Band</th>
                <th>RSSI</th>
                <th>Encryption</th>
            </tr>'''
    
    for net in latest_analysis.get('networks', []):
        html_content += f'''
            <tr>
                <td>{net.get('ssid', '<Hidden>')}</td>
                <td>{net.get('bssid', '')}</td>
                <td>{net.get('channel', '')}</td>
                <td>{net.get('band', '')}</td>
                <td>{net.get('rssi', '')} dBm</td>
                <td>{net.get('encryption', '')}</td>
            </tr>'''
    
    html_content += '''
        </table>
        
        <h2>Connected Devices</h2>
        <table>
            <tr>
                <th>MAC Address</th>
                <th>Manufacturer</th>
                <th>Connected To</th>
                <th>Signal</th>
                <th>Probed Networks</th>
            </tr>'''
    
    for dev in latest_analysis.get('connected_devices', []):
        html_content += f'''
            <tr>
                <td>{dev.get('device_mac', '')}</td>
                <td>{dev.get('manufacturer', 'Unknown')}</td>
                <td>{dev.get('connected_bssid', '')}</td>
                <td>{dev.get('signal', '')} dBm</td>
                <td>{', '.join(dev.get('probed_ssids', []))}</td>
            </tr>'''
    
    html_content += '''
        </table>
        
        <h2>Devices Searching for Wi-Fi</h2>
        <table>
            <tr>
                <th>MAC Address</th>
                <th>Manufacturer</th>
                <th>Signal</th>
                <th>Probed Networks</th>
            </tr>'''
    
    for dev in latest_analysis.get('searching_devices', []):
        html_content += f'''
            <tr>
                <td>{dev.get('device_mac', '')}</td>
                <td>{dev.get('manufacturer', 'Unknown')}</td>
                <td>{dev.get('signal', '')} dBm</td>
                <td>{', '.join(dev.get('probed_ssids', []))}</td>
            </tr>'''
    
    html_content += '''
        </table>
        
        <h2>Channel Congestion (2.4 GHz)</h2>
        <table>
            <tr>
                <th>Channel</th>
                <th>Network Count</th>
                <th>Congestion Level</th>
            </tr>'''
    
    congestion = latest_analysis.get('channel_congestion', {})
    for ch in sorted([c for c in congestion.keys() if str(c).isdigit()], key=lambda x: int(x)):
        data = congestion[ch]
        if isinstance(data, dict):
            level = data.get('congestion_level', 'N/A')
            html_content += f'''
            <tr class="level-{level.lower()}-bg">
                <td>{ch}</td>
                <td>{data.get('network_count', 0)}</td>
                <td>{level}</td>
            </tr>'''
    
    html_content += '''
        </table>
        
        <h2>Recommendations</h2>'''
    
    recs = latest_analysis.get('recommendations', {})
    if recs:
        for band, rec in recs.items():
            if isinstance(rec, dict) and rec.get('recommended'):
                html_content += f'''
        <div class="recommendation">
            <strong>{band}:</strong> Recommended channel {rec.get('recommended')}
            {f"({rec.get('reason', '')})" if rec.get('reason') else ""}
        </div>'''
    else:
        html_content += '<p>No recommendations available</p>'
    
    html_content += f'''
        <div class="footer">
            <p>Generated by WA-CPE Wi-Fi Analyzer on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>'''
    
    return Response(
        html_content,
        mimetype='text/html',
        headers={'Content-Disposition': f'attachment; filename=wifi_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'}
    )

@app.route('/api/export/txt')
@require_auth
def export_txt():
    """Export data as TXT report"""
    timestamp = latest_analysis.get('timestamp') or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    interf = latest_analysis.get('interference', {})
    networks = latest_analysis.get('networks', [])
    connected = latest_analysis.get('connected_devices', [])
    searching = latest_analysis.get('searching_devices', [])
    
    txt = f'''
================================================================================
                    WA-CPE WI-FI ANALYZER REPORT
================================================================================
Generated: {timestamp}
Interface: {analyzer_interface} (TP-Link Archer T2U Plus)
================================================================================

INTERFERENCE SUMMARY
-------------------
Level: {interf.get('level', 'N/A')}
Score: {interf.get('score', 0)}/15

STATISTICS
----------
Total Networks Detected: {len(networks)}
Connected Devices: {len(connected)}
Searching Devices: {len(searching)}

'''
    
    txt += 'DETECTED NETWORKS\n'
    txt += '-' * 80 + '\n'
    txt += f"{'SSID':<25} {'BSSID':<18} {'Ch':<4} {'Band':<8} {'RSSI':<8}\n"
    txt += '-' * 80 + '\n'
    for net in networks:
        ssid = (net.get('ssid') or '<Hidden>')[:24]
        bssid = net.get('bssid', '')[:17]
        ch = str(net.get('channel', '?'))
        band = net.get('band', '')[:7]
        rssi = str(net.get('rssi', '?'))
        txt += f"{ssid:<25} {bssid:<18} {ch:<4} {band:<8} {rssi:<8}\n"
    
    txt += '''
CONNECTED DEVICES
'''
    txt += '-' * 80 + '\n'
    for dev in connected:
        txt += f"MAC: {dev.get('device_mac', 'N/A')}\n"
        txt += f"  Manufacturer: {dev.get('manufacturer', 'Unknown')}\n"
        txt += f"  Connected to: {dev.get('connected_bssid', 'N/A')}\n"
        txt += f"  Signal: {dev.get('signal', 'N/A')} dBm\n"
        txt += '\n'
    
    txt += 'SEARCHING DEVICES\n'
    txt += '-' * 80 + '\n'
    for dev in searching:
        txt += f"MAC: {dev.get('device_mac', 'N/A')}\n"
        txt += f"  Manufacturer: {dev.get('manufacturer', 'Unknown')}\n"
        txt += f"  Signal: {dev.get('signal', 'N/A')} dBm\n"
        txt += f"  Searching for: {', '.join(dev.get('probed_ssids', []))}\n"
        txt += '\n'
    
    txt += f'''
================================================================================
                           END OF REPORT
================================================================================
'''
    
    return Response(
        txt,
        mimetype='text/plain',
        headers={'Content-Disposition': f'attachment; filename=wifi_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'}
    )

LOGIN_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WA-CPE Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .login-box {
            background: rgba(255,255,255,0.1);
            padding: 40px;
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.1);
            width: 350px;
            text-align: center;
        }
        .login-box h1 { color: #00d9ff; margin-bottom: 10px; font-size: 24px; }
        .login-box p { color: #888; margin-bottom: 30px; font-size: 14px; }
        .input-group { margin-bottom: 20px; text-align: left; }
        .input-group label { display: block; color: #888; font-size: 12px; margin-bottom: 5px; }
        .input-group input {
            width: 100%; padding: 12px;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            background: rgba(255,255,255,0.05);
            color: #fff; font-size: 14px;
        }
        .input-group input:focus { outline: none; border-color: #00d9ff; }
        .btn {
            width: 100%; padding: 12px;
            background: #00d9ff; color: #1a1a2e;
            border: none; border-radius: 8px;
            font-size: 14px; font-weight: bold; cursor: pointer;
        }
        .btn:hover { background: #00b8d9; }
        .error {
            background: rgba(255,0,0,0.2); color: #ff6666;
            padding: 10px; border-radius: 8px;
            margin-bottom: 20px; font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="login-box">
        <h1>📡 WA-CPE Wi-Fi Analyzer</h1>
        <p>Please login to access the dashboard</p>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        <form method="POST">
            <div class="input-group">
                <label>Username</label>
                <input type="text" name="username" placeholder="Enter username" required>
            </div>
            <div class="input-group">
                <label>Password</label>
                <input type="password" name="password" placeholder="Enter password" required>
            </div>
            <button type="submit" class="btn">Login</button>
        </form>
    </div>
</body>
</html>
'''

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WA-CPE Wi-Fi Analyzer Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
        }
        
        .header {
            background: rgba(0,0,0,0.3);
            padding: 20px 40px;
            border-bottom: 2px solid #0f3460;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header-left h1 {
            color: #00d9ff;
            font-size: 28px;
        }
        
        .header-left .subtitle {
            color: #888;
            font-size: 14px;
            margin-top: 5px;
        }
        
        .header-right {
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .header-sys-info {
            display: flex;
            gap: 20px;
            justify-content: flex-end;
            padding: 8px 20px 12px;
            background: rgba(0,0,0,0.3);
            border-top: 1px solid #0f3460;
        }
        
        .sys-item {
            font-size: 12px;
            color: #00d9ff;
        }
        
        .control-btn {
            background: #0f3460;
            color: #00d9ff;
            border: 1px solid #00d9ff;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s;
        }
        
        .control-btn:hover {
            background: #00d9ff;
            color: #1a1a2e;
        }
        
        .control-btn.pause-btn {
            background: #ff9800;
            border-color: #ff9800;
            color: #fff;
        }
        
        .control-btn.pause-btn:hover {
            background: #f57c00;
            border-color: #f57c00;
        }
        
        .control-btn.resume-btn {
            background: #4caf50;
            border-color: #4caf50;
            color: #fff;
        }
        
        .control-btn.resume-btn:hover {
            background: #388e3c;
            border-color: #388e3c;
        }
        
        .control-btn.logout-btn {
            background: #f44336;
            border-color: #f44336;
            color: #fff;
        }
        
        .control-btn.logout-btn:hover {
            background: #d32f2f;
            border-color: #d32f2f;
        }
        
        .status-bar {
            background: rgba(0,217,255,0.1);
            padding: 10px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #0f3460;
        }
        
        .status-left {
            display: flex;
            gap: 20px;
            align-items: center;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #00d9ff;
            animation: pulse 2s infinite;
        }
        
        .status-dot.paused {
            background: #ff9800;
            animation: none;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .status-label {
            font-size: 14px;
        }
        
        .status-label.paused {
            color: #ff9800;
        }
        
        .export-buttons {
            display: flex;
            gap: 10px;
        }
        
        .export-btn {
            background: #0f3460;
            color: #00d9ff;
            border: 1px solid #00d9ff;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12px;
            display: flex;
            align-items: center;
            gap: 5px;
            transition: all 0.3s;
        }
        
        .export-btn:hover {
            background: #00d9ff;
            color: #1a1a2e;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            padding: 20px 40px;
        }
        
        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .card-title {
            font-size: 18px;
            color: #00d9ff;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .card-title .icon {
            font-size: 24px;
        }
        
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .stat-box {
            background: rgba(0,217,255,0.1);
            border-radius: 10px;
            padding: 15px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: #00d9ff;
        }
        
        .stat-label {
            font-size: 12px;
            color: #888;
            margin-top: 5px;
        }
        
        .network-list {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .network-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            margin-bottom: 8px;
        }
        
        .network-info {
            flex: 1;
        }
        
        .network-name {
            font-weight: bold;
            margin-bottom: 4px;
        }
        
        .network-details {
            font-size: 12px;
            color: #888;
        }
        
        .network-signal {
            text-align: right;
        }
        
        .signal-strength {
            font-size: 24px;
            font-weight: bold;
        }
        
        .signal-label {
            font-size: 10px;
            color: #888;
        }
        
        .heatmap {
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
            margin-top: 15px;
        }
        
        .channel-bar {
            width: 40px;
            text-align: center;
        }
        
        .channel-number {
            font-size: 14px;
            font-weight: bold;
            color: #00d9ff;
            margin-bottom: 5px;
        }
        
        .channel-fill {
            background: #00d9ff;
            border-radius: 5px;
            transition: height 0.3s ease;
        }
        
        .recommendation-box {
            background: rgba(0,217,255,0.1);
            border-left: 4px solid #00d9ff;
            padding: 15px;
            border-radius: 0 10px 10px 0;
            margin-bottom: 15px;
        }
        
        .recommendation-title {
            font-weight: bold;
            color: #00d9ff;
            margin-bottom: 8px;
        }
        
        .device-list {
            max-height: 200px;
            overflow-y: auto;
        }
        
        .device-item {
            display: flex;
            justify-content: space-between;
            padding: 10px;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            margin-bottom: 8px;
        }
        
        .full-width {
            grid-column: 1 / -1;
        }
        
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(255,255,255,0.05);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #00d9ff;
            border-radius: 4px;
        }
        
        .loading {
            text-align: center;
            padding: 50px;
            color: #888;
        }
        
        .paused-banner {
            background: rgba(255,152,0,0.2);
            border: 2px solid #ff9800;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            text-align: center;
            display: none;
        }
        
        .paused-banner.visible {
            display: block;
        }
        
        .paused-banner h3 {
            color: #ff9800;
            margin-bottom: 5px;
        }
        
        .paused-banner p {
            color: #888;
            font-size: 12px;
        }
        
        .system-info {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            justify-content: space-around;
            padding: 10px 0;
        }
        
        .sys-box {
            text-align: center;
            min-width: 150px;
        }
        
        .sys-label {
            font-size: 12px;
            color: #888;
            margin-bottom: 5px;
            text-transform: uppercase;
        }
        
        .sys-value {
            font-size: 16px;
            font-weight: bold;
            color: #00d9ff;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-left">
            <h1>📡 WA-CPE Wi-Fi Analyzer</h1>
            <div class="subtitle">Real-time Wi-Fi Interference Analysis</div>
        </div>
        <div class="header-right">
            <button class="control-btn" onclick="exportData('csv')">
                📥 Export CSV
            </button>
            <button class="control-btn" onclick="exportData('html')">
                📄 Export HTML
            </button>
            <button class="control-btn" onclick="exportData('txt')">
                📝 Export TXT
            </button>
            <button class="control-btn pause-btn" id="pauseBtn" onclick="togglePause()">
                ⏸️ Pause
            </button>
            <button class="control-btn logout-btn" onclick="window.location.href='/logout'">
                🚪 Logout
            </button>
        </div>
        <div class="header-sys-info">
            <span class="sys-item">💾 <span id="sysStorage">Loading...</span></span>
            <span class="sys-item">🧠 <span id="sysMemory">Loading...</span></span>
            <span class="sys-item">📊 <span id="sysLoad">Loading...</span></span>
        </div>
    </div>
    
    <div class="status-bar">
        <div class="status-left">
            <div class="status-item">
                <div class="status-dot" id="statusDot"></div>
                <span class="status-label" id="statusLabel">Live Monitoring Active</span>
            </div>
            <div class="status-item">
                <span>Last Update: <span id="lastUpdate">--:--:--</span></span>
            </div>
            <div class="status-item adapter-info" id="adapterInfo">
                <span>🔍 Detecting adapter...</span>
            </div>
        </div>
    </div>
    
    <div class="main-content">
        <div class="card full-width">
            <div class="paused-banner" id="pausedBanner">
                <h3>⏸️ Monitoring Paused</h3>
                <p>Data is frozen. Click Resume to continue live updates.</p>
            </div>
            <div class="card-title">
                <span class="icon">📊</span>
                Network Statistics
            </div>
            <div class="stat-grid">
                <div class="stat-box">
                    <div class="stat-value" id="networkCount">0</div>
                    <div class="stat-label">Networks</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value" id="connectedCount">0</div>
                    <div class="stat-label">Connected</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value" id="searchingCount">0</div>
                    <div class="stat-label">Searching</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value" id="interferenceScore">0</div>
                    <div class="stat-label">Interference</div>
                </div>
            </div>
            
            <div class="card-title">
                <span class="icon">📺</span>
                Channel Heatmap (2.4 GHz)
            </div>
            <div class="heatmap" id="heatmap"></div>
        </div>
        
        <div class="card">
            <div class="card-title">
                <span class="icon">📶</span>
                Detected Networks
            </div>
            <div class="network-list" id="networkList">
                <div class="loading">Loading data</div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-title">
                <span class="icon">💡</span>
                Recommendations
            </div>
            <div id="recommendations">
                <div class="loading">Loading recommendations</div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-title">
                <span class="icon">📱</span>
                Connected Devices
            </div>
            <div class="device-list" id="connectedList">
                <div class="loading">Loading devices</div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-title">
                <span class="icon">🔍</span>
                Devices Searching for Wi-Fi
            </div>
            <div class="device-list" id="searchingList">
                <div class="loading">Loading devices</div>
            </div>
        </div>
    </div>
    
    <script>
        let isPaused = false;
        let updateInterval = null;
        
        function togglePause() {
            const endpoint = isPaused ? '/api/resume' : '/api/pause';
            fetch(endpoint, { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    isPaused = !isPaused;
                    updatePauseUI();
                })
                .catch(error => {
                    console.error('Error toggling pause:', error);
                });
        }
        
        function updatePauseUI() {
            const pauseBtn = document.getElementById('pauseBtn');
            const statusDot = document.getElementById('statusDot');
            const statusLabel = document.getElementById('statusLabel');
            const pausedBanner = document.getElementById('pausedBanner');
            
            if (isPaused) {
                pauseBtn.innerHTML = '▶️ Resume';
                pauseBtn.classList.remove('pause-btn');
                pauseBtn.classList.add('resume-btn');
                statusDot.classList.add('paused');
                statusLabel.textContent = 'Monitoring Paused';
                statusLabel.classList.add('paused');
                pausedBanner.classList.add('visible');
                if (updateInterval) {
                    clearInterval(updateInterval);
                    updateInterval = null;
                }
            } else {
                pauseBtn.innerHTML = '⏸️ Pause';
                pauseBtn.classList.remove('resume-btn');
                pauseBtn.classList.add('pause-btn');
                statusDot.classList.remove('paused');
                statusLabel.textContent = 'Live Monitoring Active';
                statusLabel.classList.remove('paused');
                pausedBanner.classList.remove('visible');
                updateDashboard();
                updateInterval = setInterval(updateDashboard, 5000);
            }
        }
        
        function updateDashboard() {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    if (data.paused === undefined) {
                        data.paused = false;
                    }
                    
                    document.getElementById('lastUpdate').textContent = data.timestamp || '--:--:--';
                    document.getElementById('networkCount').textContent = data.networks ? data.networks.length : 0;
                    document.getElementById('connectedCount').textContent = data.connected_devices ? data.connected_devices.length : 0;
                    document.getElementById('searchingCount').textContent = data.searching_devices ? data.searching_devices.length : 0;
                    
                    const ifaceInfo = data.interface_info || {};
                    const adapterText = ifaceInfo.adapter ? 
                        `📡 ${ifaceInfo.interface} | ${ifaceInfo.adapter} | MAC: ${ifaceInfo.mac_address || 'N/A'} | Driver: ${ifaceInfo.driver || 'N/A'}` :
                        'Interface: wlan0 (TP-Link Archer T2U Plus)';
                    document.getElementById('adapterInfo').innerHTML = `<span>${adapterText}</span>`;
                    
                    const sysInfo = data.system_info || {};
                    document.getElementById('sysStorage').textContent = sysInfo.storage_used + ' / ' + sysInfo.storage_total + ' (' + sysInfo.storage_free + ' free)';
                    document.getElementById('sysMemory').textContent = sysInfo.memory_used + ' / ' + sysInfo.memory_total;
                    document.getElementById('sysLoad').textContent = 'Load: ' + (sysInfo.load_average || 'N/A');
                    
                    const interference = data.interference || {};
                    document.getElementById('interferenceScore').textContent = interference.score || 0;
                    
                    updateNetworkList(data.networks || []);
                    updateConnectedList(data.connected_devices || []);
                    updateSearchingList(data.searching_devices || []);
                    updateHeatmap(data.networks || []);
                    updateRecommendations(data);
                })
                .catch(error => {
                    console.error('Error fetching data:', error);
                });
        }
        
        function updateNetworkList(networks) {
            const container = document.getElementById('networkList');
            if (networks.length === 0) {
                container.innerHTML = '<div class="loading">No networks detected</div>';
                return;
            }
            
            container.innerHTML = networks.map(net => `
                <div class="network-item">
                    <div class="network-info">
                        <div class="network-name">${net.ssid || '<Hidden>'}</div>
                        <div class="network-details">${net.bssid} | Ch ${net.channel || '?'} | ${net.band || ''}</div>
                    </div>
                    <div class="network-signal">
                        <div class="signal-strength">${net.rssi || '?'}</div>
                        <div class="signal-label">dBm</div>
                    </div>
                </div>
            `).join('');
        }
        
        function updateConnectedList(devices) {
            const container = document.getElementById('connectedList');
            if (devices.length === 0) {
                container.innerHTML = '<div class="loading">No connected devices</div>';
                return;
            }
            
            container.innerHTML = devices.map(dev => `
                <div class="device-item">
                    <div>
                        <strong>${dev.device_mac || 'Unknown'}</strong>
                        <div style="font-size:11px;color:#888">${dev.manufacturer || 'Unknown'}</div>
                    </div>
                    <div style="text-align:right">
                        <div>${dev.connected_bssid || 'N/A'}</div>
                        <div style="font-size:11px;color:#888">RSSI: ${dev.signal || '?'} dBm</div>
                    </div>
                </div>
            `).join('');
        }
        
        function updateSearchingList(devices) {
            const container = document.getElementById('searchingList');
            if (devices.length === 0) {
                container.innerHTML = '<div class="loading">No searching devices</div>';
                return;
            }
            
            container.innerHTML = devices.map(dev => `
                <div class="device-item">
                    <div>
                        <strong>${dev.device_mac || 'Unknown'}</strong>
                        <div style="font-size:11px;color:#888">${dev.manufacturer || 'Unknown'}</div>
                    </div>
                    <div style="text-align:right">
                        <div>${(dev.probed_ssids || []).join(', ') || 'Hidden SSIDs'}</div>
                        <div style="font-size:11px;color:#888">RSSI: ${dev.signal || '?'} dBm</div>
                    </div>
                </div>
            `).join('');
        }
        
        function updateHeatmap(networks) {
            const container = document.getElementById('heatmap');
            const channelCounts = {};
            
            for (let ch = 1; ch <= 13; ch++) {
                channelCounts[ch] = 0;
            }
            
            networks.forEach(net => {
                if (net.band && net.band.includes('2.4') && net.channel) {
                    const rssi = parseInt(net.rssi) || -100;
                    if (rssi > -90 && rssi < 0) {
                        channelCounts[net.channel] = (channelCounts[net.channel] || 0) + 1;
                    }
                }
            });
            
            let html = '';
            for (let ch = 1; ch <= 13; ch++) {
                const count = channelCounts[ch];
                const height = Math.min(count * 20, 80);
                const color = count >= 3 ? '#ff4444' : count >= 2 ? '#ffaa00' : count >= 1 ? '#00d9ff' : '#1a5a6e';
                html += `
                    <div class="channel-bar">
                        <div class="channel-number">${ch}</div>
                        <div class="channel-fill" style="height:${height}px;background:${color}"></div>
                    </div>
                `;
            }
            container.innerHTML = html;
        }
        
        function updateRecommendations(data) {
            const container = document.getElementById('recommendations');
            const rec24 = data.recommendations && data.recommendations['2.4GHz'];
            const rec5 = data.recommendations && data.recommendations['5GHz'];
            
            if (!rec24 && !rec5) {
                container.innerHTML = '<div class="loading">No recommendations</div>';
                return;
            }
            
            let html = '';
            
            if (rec24 && rec24.recommended) {
                html += `
                    <div class="recommendation-box">
                        <div class="recommendation-title">📶 Switch to 2.4 GHz Channel ${rec24.recommended}</div>
                        <p>Recommended for less interference in 2.4 GHz band</p>
                    </div>
                `;
            }
            
            if (rec5 && rec5.recommended) {
                html += `
                    <div class="recommendation-box">
                        <div class="recommendation-title">🚀 Consider 5 GHz (Channel ${rec5.recommended})</div>
                        <p>5 GHz has more channels and less interference</p>
                    </div>
                `;
            }
            
            container.innerHTML = html;
        }
        
        function exportData(format) {
            let endpoint;
            if (format === 'csv') endpoint = '/api/export/csv';
            else if (format === 'html') endpoint = '/api/export/html';
            else endpoint = '/api/export/txt';
            
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
            let filename;
            if (format === 'csv') filename = `wifi_analysis_${timestamp}.csv`;
            else if (format === 'html') filename = `wifi_analysis_${timestamp}.html`;
            else filename = `wifi_analysis_${timestamp}.txt`;
            
            const link = document.createElement('a');
            link.href = endpoint;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
        
        updateInterval = setInterval(updateDashboard, 5000);
        updateDashboard();
    </script>
</body>
</html>
'''

def start_dashboard(interface='wlan1', host='0.0.0.0', port=5000):
    """Start the web dashboard"""
    global analyzer_interface, analyzer_running, analyzer_paused
    
    analyzer_interface = interface
    analyzer_running = True
    analyzer_paused = False
    
    analysis_thread = threading.Thread(target=run_analysis, daemon=True)
    analysis_thread.start()
    
    print(f"Starting WA-CPE Dashboard on http://{host}:{port}")
    print("Access from any device on your network!")
    print("Press Ctrl+C to stop")
    
    app.run(host=host, port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='WA-CPE Wi-Fi Analyzer Dashboard')
    parser.add_argument('-i', '--interface', default='wlan1', help='Wi-Fi interface')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind')
    parser.add_argument('-p', '--port', type=int, default=5000, help='Port to listen')
    
    args = parser.parse_args()
    
    start_dashboard(interface=args.interface, host=args.host, port=args.port)
