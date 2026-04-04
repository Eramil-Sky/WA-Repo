# Wi-Fi Analyzer - Quick Reference Card

## Common Scenarios & Actions

### 🔧 PROBLEM: Wi-Fi Slow at Home
```
1. Run: sudo python3 analyzer.py -i wlan0
2. Check: Is "Impact" = HIGH or CRITICAL?
3. If YES → Note "Recommended channel" from output
4. Log into router → Change channel → Save
5. Re-run analyzer → Check if improved
```

### 🏢 PROBLEM: Office Wi-Fi Crowded
```
1. Run during peak hours (10am, 2pm)
2. Check which channel has MOST networks
3. Look at "Channel Congestion" section
4. Find channel with LOW congestion
5. Configure all APs to non-overlapping channels
   (1, 6, 11 for 2.4GHz)
```

### 📱 PROBLEM: IoT Devices Disconnecting
```
1. IoT devices use 2.4GHz only
2. Check 2.4GHz band channels only
3. Find least congested 2.4GHz channel
4. Switch router to that channel
5. Give IoT devices time to reconnect
```

### 🏭 PROBLEM: Industrial Interference
```
1. Walk the floor with Pi + antenna
2. Run: python3 app.py (for live dashboard)
3. Monitor noise floor levels
4. Identify spots with HIGH noise
5. Avoid placing APs in high-noise areas
```

---

## Reading the Dashboard

### Green = Good ✅
- Impact: LOW
- RSSI: > -60 dBm
- Latency: < 30ms
- Packet Loss: 0%

### Yellow = Warning ⚠️
- Impact: MEDIUM
- RSSI: -60 to -75 dBm
- Latency: 30-100ms
- Packet Loss: < 1%

### Red = Problem ❌
- Impact: HIGH/CRITICAL
- RSSI: < -75 dBm
- Latency: > 100ms
- Packet Loss: > 1%

---

## Decision Tree

```
Is Wi-Fi slow?
│
├─ YES → Run analyzer
│        │
│        ├─ Impact = HIGH/CRITICAL?
│        │   ├─ YES → Check recommendations
│        │   │        Switch to recommended channel
│        │   │
│        │   └─ NO → Check RSSI
│        │            ├─ RSSI < -75 → Move closer to AP
│        │            └─ RSSI > -75 → Other issue
│        │
│        └─ 2.4GHz all crowded?
│            └─ YES → Switch to 5GHz band
│
└─ NO → No action needed
```

---

## Channel Recommendations

### 2.4 GHz (Non-overlapping)
```
Channel 1  ──────●───────
Channel 6          ──────●───────
Channel 11                    ──────●───────
```

### 5 GHz (Best options)
```
36, 40, 44, 48  (UNII-1)
149, 153, 157, 161, 165  (UNII-3)
```

---

## When to Take Action

| Metric | Action Threshold |
|--------|----------------|
| RSSI | Below -75 dBm |
| Noise | Above -80 dBm |
| SNR | Below 20 dB |
| Latency | Above 100ms |
| Packet Loss | Above 1% |
| Channel Networks | More than 4 on same channel |

---

## Quick Commands

```bash
# Basic scan
sudo python3 analyzer.py -i wlan0

# Scan with JSON output
sudo python3 analyzer.py -i wlan0 --json

# Start web dashboard
python3 app.py

# Continuous monitoring (every 5 min)
watch -n 300 sudo python3 analyzer.py -i wlan0

# Check specific channel
iw dev wlan0 scan | grep -A5 "freq: 2437"
```
