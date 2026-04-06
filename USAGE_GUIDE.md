# Wi-Fi Analyzer - Practical Usage Guide

## Scenario 1: Home Network Troubleshooting

**Problem:** Your Wi-Fi is slow at home

### Steps:

```bash
# 1. Boot up Raspberry Pi with monitor-mode adapter
# 2. SSH into your Pi
ssh pi@192.168.1.100

# 3. Run the analyzer
cd wa-analyzer
sudo python3 analyzer.py -i wlan0

# 4. Check the output - look for:
#    - Is Channel 6, 11, or 1 congested?
#    - What's your RSSI? (should be > -70 dBm)
#    - What's the interference level?
```

**What to look for:**

| Indicator | Good | Bad |
|-----------|------|-----|
| RSSI | > -60 dBm | < -80 dBm |
| Latency | < 30ms | > 100ms |
| Channel Congestion | LOW | HIGH/CRITICAL |
| Interference Level | LOW/MEDIUM | HIGH/CRITICAL |

---

## Scenario 2: Office Wi-Fi Optimization

**Problem:** Multiple users complaining about slow Wi-Fi

### Steps:

```bash
# 1. Set up analyzer in central location
# 2. Run analysis during peak hours (10am, 2pm)
cd wa-analyzer
sudo python3 analyzer.py -i wlan0 --json > office_morning.json

# 3. Analyze the output
# Look for:
#    - Which channel has MOST networks?
#    - Are neighboring channels overlapping?
#    - What's the recommended channel?

# 4. Generate report
python3 analyzer.py -i wlan0
```

**Decision Matrix:**

```
If Channel 6 has 5+ networks:
  → Switch your AP to Channel 1 or 11

If all 2.4GHz channels are crowded:
  → Move to 5GHz band

If many hidden SSIDs on your channel:
  → Switch to non-overlapping channel
```

---

## Scenario 3: Industrial Environment

**Problem:** Factory floor has interference from machinery

### Steps:

```bash
# 1. Walk the floor with Pi + antenna
# 2. Run continuous monitoring
cd wa-analyzer
sudo python3 analyzer.py -i wlan0 --json > location_1.json

# 3. Move to different spots and repeat
# 4. Compare noise levels

# 5. Start web dashboard for real-time monitoring
python3 app.py
# Access at http://<pi-ip>:5000
```

**What affects industrial Wi-Fi:**

| Source | Frequency | Effect |
|--------|-----------|--------|
| Motors | 2.4GHz | High noise floor |
| Microwaves | 2.45GHz | Intermittent bursts |
| Fluorescent lights | Broadband | Constant noise |
| Bluetooth | 2.4GHz | Channel interference |

---

## Scenario 4: Smart Home Optimization

**Problem:** IoT devices keep disconnecting

### Steps:

```bash
# 1. Identify which band your IoT devices use
# Most IoT = 2.4GHz only

# 2. Check 2.4GHz channel congestion
cd wa-analyzer
sudo python3 analyzer.py -i wlan0

# 3. Find least congested 2.4GHz channel
# The output will show: "Recommended: Channel X"

# 4. Configure your router to use that channel
# (Do this via router admin panel)

# 5. Re-run analysis after changes
```

---

## Scenario 5: Event/Wi-Fi Party

**Problem:** Conference with 100+ devices, everyone slow

### Steps:

```bash
# 1. Survey venue BEFORE event
cd wa-analyzer
sudo python3 analyzer.py -i wlan0 > venue_survey.txt

# 2. Identify existing Wi-Fi sources
# 3. Plan your AP channels avoiding interference

# 4. During event - monitor in real-time
python3 app.py
# Dashboard shows live metrics

# 5. If issues arise, check:
#    - Which channels are now congested?
#    - Has noise floor increased?
#    - Adjust AP channels as needed
```

---

## Scenario 6: Continuous Monitoring

**Problem:** Want to track Wi-Fi health over time

### Steps:

```bash
# 1. Create monitoring script
cat > monitor.sh << 'EOF'
#!/bin/bash
while true; do
    DATE=$(date +"%Y%m%d_%H%M%S")
    echo "Scanning at $DATE..."
    sudo python3 analyzer.py -i wlan0 --json > "scans/scan_$DATE.json"
    sleep 300  # Every 5 minutes
done
EOF

chmod +x monitor.sh

# 2. Create scans directory
mkdir -p scans

# 3. Start monitoring (runs in background)
nohup ./monitor.sh > monitor.log &

# 4. View historical data
python3 app.py
# Dashboard shows trends over time
```

---

## Scenario 7: ISP Router Issues

**Problem:** Is the slow Wi-Fi your ISP's fault?

### Steps:

```bash
# 1. Test wired connection first
# Connect laptop directly to router
# Run: speedtest-cli

# 2. If wired is fast but Wi-Fi is slow:
#    → Problem is Wi-Fi, not ISP

# 3. If wired is also slow:
#    → Contact ISP, problem is upstream

# 4. Run Wi-Fi analyzer
cd wa-analyzer
sudo python3 analyzer.py -i wlan0

# 5. Interpret results:
#    - Wired good + Wi-Fi bad = Interference issue
#    - Both bad = ISP/router hardware issue
```

---

## Reading the Output

### Quick Health Check

```
📡 Networks: 8 detected
📶 RSSI: -55 dBm        ✅ Good
📊 Noise: -90 dBm       ✅ Good  
🎯 Impact: LOW          ✅ Good

→ Diagnosis: Wi-Fi is healthy
→ Action: None needed
```

### Problem Detected

```
📡 Networks: 12 detected
📶 RSSI: -72 dBm        ⚠️ Fair
📊 Noise: -75 dBm       ⚠️ High noise
🎯 Impact: HIGH          ❌ Problem

→ Diagnosis: High co-channel interference on Channel 6
→ Action: Switch to Channel 11
```

### Critical Situation

```
📡 Networks: 18 detected
📶 RSSI: -85 dBm        ❌ Weak
📊 Noise: -70 dBm       ❌ Very noisy
🎯 Impact: CRITICAL      ❌ Critical

→ Diagnosis: Channel overcrowded, severe interference
→ Action: 
   1. Move to 5GHz band immediately
   2. Get access point closer to devices
   3. Consider Wi-Fi 6E router
```

---

## Making Changes

### After Analysis:

1. **Write down recommendations** from output
2. **Log into your router** admin panel
3. **Change Wi-Fi channel** to recommended one
4. **Save settings** and wait 30 seconds
5. **Re-run analysis** to verify improvement
6. **Document results** in scans folder

### What to Adjust:

| Problem | Solution |
|---------|----------|
| 2.4GHz congestion | Switch to 5GHz |
| Weak signal | Move AP or use range extender |
| High latency | Change channel, reduce devices |
| Packet loss | Check for interference sources |

---

## Hardware Setup Checklist

```
□ Raspberry Pi 4/5
□ 16GB+ SD card with Raspberry Pi OS
□ Monitor-mode Wi-Fi adapter (Alfa AWUS036NHA)
□ Power supply (USB-C, 3A)
□ SSH enabled on Pi
□ Wi-Fi adapter connected to Pi USB port
□ External antenna (optional but recommended)
```

### First-Time Setup:

```bash
# 1. Update Pi
sudo apt update && sudo apt upgrade -y

# 2. Install tools
sudo apt install iw iperf3 python3-pip -y

# 3. Install Python packages
pip3 install flask

# 4. Clone/download analyzer
cd ~
git clone <your-repo-url>
cd wa-analyzer

# 5. Test it works
sudo python3 analyzer.py -i wlan0

# 6. Start dashboard
python3 app.py
```
