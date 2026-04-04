<<<<<<< HEAD
# Wi-Fi Interference Analyzer

A tool to measure and visualize how Wi-Fi interference affects your network performance.

## Quick Start

### 1. Windows (Demo Mode)
```bash
cd wa-analyzer
python demo.py
```
This simulates scanner output - no special hardware needed.

### 2. Linux/Raspberry Pi (Full Mode)

**Hardware Needed:**
- Raspberry Pi 4/5
- USB Wi-Fi adapter with monitor mode (e.g., Alfa AWUS036NHA)
- External antenna (optional)

**Setup:**
```bash
# Install dependencies
sudo apt update
sudo apt install iw iperf3 python3-pip

# Install Python packages
pip3 install flask

# Set Wi-Fi interface to monitor mode
sudo ip link set wlan0 down
sudo iw dev wlan0 set type monitor
sudo ip link set wlan0 up

# Run the analyzer
sudo python3 analyzer.py -i wlan0
```

### 3. Web Dashboard (Linux Only)

```bash
cd wa-analyzer
pip3 install flask
python3 app.py
# Open http://localhost:5000
```

## What It Does

| Feature | Description |
|---------|-------------|
| **Network Scanner** | Detects all Wi-Fi networks nearby |
| **Interference Detection** | Finds co-channel & adjacent channel overlap |
| **Performance Test** | Measures latency, throughput, packet loss |
| **Impact Score** | Rates interference as LOW/MEDIUM/HIGH/CRITICAL |
| **Recommendations** | Suggests best channels to use |

## Example Output

```
📊 CHANNEL CONGESTION
  Channel 1: 2 networks 🟢 LOW
  Channel 6: 5 networks 🔴 HIGH  
  Channel 11: 1 networks 🟢 LOW

🎯 INTERFERENCE IMPACT
  Level: MEDIUM
  Score: 3.2

💡 RECOMMENDATIONS
  → Switch to 2.4GHz Channel 11
  → Consider 5GHz for less interference
```

## Key Metrics

- **RSSI**: Signal strength (-30 to -90 dBm)
- **SNR**: Signal-to-Noise Ratio (>20 dB is good)
- **Latency**: Response time (<50ms is good)
- **Packet Loss**: Failed packets (0% is ideal)

## Project Structure

```
wa-analyzer/
├── demo.py              # Windows demo (no hardware)
├── analyzer.py          # CLI tool (Linux)
├── app.py               # Web dashboard (Linux)
├── modules/
│   ├── wifi_scanner.py
│   ├── interference_detector.py
│   ├── performance_tester.py
│   ├── correlation_engine.py
│   └── database.py
└── templates/
    └── dashboard.html
```

## Requirements

- Linux kernel with `iw` tools
- Python 3.7+
- Root access for monitor mode
- USB Wi-Fi adapter with monitor mode support

## Next Steps

1. Run `demo.py` to see the output
2. Set up Raspberry Pi with monitor mode adapter
3. Deploy `analyzer.py` for CLI monitoring
4. Set up `app.py` for web dashboard
5. Configure cron jobs for continuous monitoring

## Troubleshooting

**"Operation not permitted" error:**
- Need root: `sudo python3 analyzer.py`

**No networks found:**
- Check Wi-Fi adapter supports monitor mode
- Try: `sudo iw dev wlan0 scan`

**Module import errors:**
- Run from wa-analyzer directory
- Check Python path
=======
# WA-Repo
>>>>>>> f0254703dbb720752cff0cfe9c12a47f03215707
