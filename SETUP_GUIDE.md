# Wi-Fi Analyzer - Complete Hardware & Setup Guide

## Required Hardware

### Option A: Budget Setup (~ $75)
```
ITEM                          COST     PURPOSE
─────────────────────────────────────────────────
Raspberry Pi 4 (4GB)          $55      Main computer
16GB MicroSD Card             $7       Operating system
USB Wi-Fi Adapter (RTL8812AU) $12      Monitor mode support
5V 3A USB-C Power Supply     $8       Power
TOTAL:                        ~$82
```

### Option B: Recommended Setup (~ $120)
```
ITEM                          COST     PURPOSE
─────────────────────────────────────────────────
Raspberry Pi 4 (4GB)          $55      Main computer
32GB MicroSD Card             $10      More storage
Alfa AWUS036NHA               $35      Best monitor mode adapter
9dBi Antenna                  $10      Extended range
5V 3A USB-C Power Supply      $8       Power
Case (optional)               $7       Protection
TOTAL:                        ~$125
```

---

## Recommended Wi-Fi Adapters

### ✅ Works with Monitor Mode
| Adapter | Chipset | Price | Notes |
|---------|---------|-------|-------|
| Alfa AWUS036NHA | Atheros AR9271 | ~$35 | Best range, most reliable |
| Alfa AWUS036ACH | Realtek RTL8812AU | ~$40 | Dual band, fast |
| TP-Link TL-WN722N v2 | Atheros ATH9K | ~$12 | Budget option |
| Panda PAU09 | Ralink RT5572 | ~$25 | Dual band |

### ❌ Won't Work (Monitor Mode)
- Most laptop built-in Wi-Fi
- Intel Wi-Fi adapters
- Standard USB Wi-Fi sticks

---

## Step-by-Step Setup

### Step 1: Flash Raspberry Pi OS

```bash
# 1. Download Raspberry Pi Imager
# https://www.raspberrypi.com/software/

# 2. Flash Raspberry Pi OS Lite (no desktop)
#    Settings:
#    - Hostname: wifi-analyzer
#    - Enable SSH
#    - Set username/password
#    - Connect to your Wi-Fi (for SSH access)

# 3. Insert SD card and boot
```

### Step 2: Initial SSH Connection

```bash
# From your computer (not Pi)
ssh pi@wifi-analyzer.local
# Or use IP: ssh pi@192.168.1.100

# Enter password you set
```

### Step 3: Update System

```bash
# Update everything
sudo apt update
sudo apt upgrade -y

# Install required packages
sudo apt install -y iw iperf3 python3-pip git
```

### Step 4: Get the Analyzer

```bash
# Option A: Clone from repo (if you have one)
git clone <your-repo-url>
cd wa-analyzer

# Option B: Copy files from Windows
# Use WinSCP or USB drive to transfer files
```

### Step 5: Test Monitor Mode

```bash
# Check if adapter is recognized
iw dev

# Should show your Wi-Fi interface (wlan0)

# Set monitor mode
sudo ip link set wlan0 down
sudo iw dev wlan0 set type monitor
sudo ip link set wlan0 up

# Verify monitor mode
iw dev wlan0 info

# Should show: "type monitor"
```

### Step 6: Test the Analyzer

```bash
# Test basic scan (without sudo first to check)
python3 analyzer.py -i wlan0

# If error about permissions, use sudo
sudo python3 analyzer.py -i wlan0

# You should see detected networks!
```

---

## Troubleshooting Setup

### Problem: "iw dev" shows nothing
```
SOLUTION:
- Check if USB adapter is plugged in
- Try: lsusb (should show adapter)
- Try: dmesg | tail (check for errors)
- Try different USB port
```

### Problem: "Operation not supported"
```
SOLUTION:
- Your adapter doesn't support monitor mode
- Buy one from the "Works" list above
```

### Problem: "Permission denied"
```
SOLUTION:
- Use sudo: sudo python3 analyzer.py -i wlan0
```

### Problem: No networks found
```
SOLUTION:
- Wait 30 seconds after setting monitor mode
- Check if nearby Wi-Fi exists (phone, neighbor's Wi-Fi)
- Try moving closer to Wi-Fi sources
```

---

## Network Configuration

### For SSH Access (Headless Mode)

```bash
# Create SSH file on boot partition
touch /boot/ssh

# For Wi-Fi, create wpa_supplicant.conf in boot:
cat > /boot/wpa_supplicant.conf << 'EOF'
ctrl_interface=DIR=/var/run/wpa_supplicant
update_config=1
country=US

network={
    ssid="YourWiFiName"
    psk="YourWiFiPassword"
}
EOF
```

### For Static IP (Optional)

```bash
sudo nano /etc/dhcpcd.conf
# Add at end:
interface wlan0
    static ip_address=192.168.1.200/24
    static routers=192.168.1.1
    static domain_name_servers=8.8.8.8
```

---

## Running as Service (Auto-start)

```bash
# Create systemd service
sudo nano /etc/systemd/system/wifi-analyzer.service

[Unit]
Description=Wi-Fi Interference Analyzer
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/wa-analyzer
ExecStart=/usr/bin/python3 /home/pi/wa-analyzer/analyzer.py -i wlan0
Restart=on-failure

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable wifi-analyzer
sudo systemctl start wifi-analyzer

# Check status
sudo systemctl status wifi-analyzer
```

---

## Remote Access

### From Windows (Putty/WinSCP)

```
Putty:
  Host: wifi-analyzer.local
  Port: 22
  Connection type: SSH

WinSCP:
  Protocol: SFTP
  Host: wifi-analyzer.local
  Port: 22
```

### For Web Dashboard Access

```bash
# Start dashboard
python3 app.py

# Access from any browser:
# http://<pi-ip>:5000
# Example: http://192.168.1.200:5000
```

---

## Physical Placement Tips

```
┌─────────────────────────────────────────┐
│          BEST PLACEMENT                 │
├─────────────────────────────────────────┤
│                                         │
│   • Central location                    │
│   • Elevated position (high shelf)     │
│   • Away from walls and obstacles       │
│   • Away from microwave, cordless phone │
│                                         │
│   ❌ BAD PLACEMENT                      │
│   • On the floor                        │
│   • Near microwave                      │
│   • Inside cabinet                      │
│   • Near motor/machinery               │
│                                         │
└─────────────────────────────────────────┘
```

---

## Complete Setup Checklist

```
□ Raspberry Pi 4/5
□ SD Card (16GB+)
□ Wi-Fi Adapter (monitor mode capable)
□ Power Supply (3A, USB-C)
□ SSH enabled
□ System updated
□ iw, iperf3 installed
□ Analyzer files transferred
□ Monitor mode works
□ Analyzer runs successfully
□ Web dashboard accessible
□ Can access from browser
```

---

## Next Steps After Setup

1. **First Run**: Execute `sudo python3 analyzer.py -i wlan0`
2. **Record Baseline**: Note current channel congestion
3. **Identify Issues**: Look for HIGH/CRITICAL impacts
4. **Make Changes**: Adjust router channel
5. **Re-test**: Run analyzer again
6. **Document**: Save good configurations

---

## Quick Command Reference

```bash
# Start analyzer (one-time scan)
sudo python3 analyzer.py -i wlan0

# Start dashboard (web interface)
python3 app.py

# Check monitor mode status
iw dev wlan0 info

# Set monitor mode
sudo ip link set wlan0 down
sudo iw dev wlan0 set type monitor
sudo ip link set wlan0 up

# Back to managed mode (normal Wi-Fi)
sudo ip link set wlan0 down
sudo iw dev wlan0 set type managed
sudo ip link set wlan0 up

# View real-time traffic
sudo tcpdump -i wlan0 -n

# Scan for networks (basic)
sudo iw dev wlan0 scan | grep -E "SSID|signal|freq"
```
