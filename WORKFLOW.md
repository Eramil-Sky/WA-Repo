# Wi-Fi Analyzer - Visual Workflow

## Main Decision Flow

```
┌─────────────────────────────────┐
│     START: Wi-Fi Problem?       │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│   Run Analyzer                  │
│   sudo python3 analyzer.py -i wlan0
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│   Check "Interference Impact"   │
│   Level: LOW / MEDIUM / HIGH / CRITICAL
└──────────────┬──────────────────┘
               │
       ┌───────┴───────┐
       │               │
       ▼               ▼
   LOW/MEDIUM      HIGH/CRITICAL
       │               │
       ▼               ▼
┌──────────────┐  ┌─────────────────────────────────┐
│ RSSI OK?     │  │ Identify Problem Type:          │
│ (> -70 dBm)  │  │                                 │
└──────┬───────┘  │ • Co-channel interference?     │
        │          │ • Adjacent channel overlap?     │
   ┌────┴────┐    │ • Channel congestion?          │
   │          │    │ • High noise floor?             │
   ▼          ▼    └───────────────┬─────────────────┘
  YES         NO                   │
   │           │                   ▼
   │           ▼        ┌─────────────────────────────────┐
   │   ┌───────────────│ Check "Recommendations"        │
   │   │               │ Output will say:                 │
   │   │               │ "Switch to Channel X"          │
   │   │               └───────────────┬─────────────────┘
   │   │                               │
   │   ▼                               ▼
   │   ┌─────────────────────────────────────────┐
   │   │ ACTION: Configure Router                │
   │   │ 1. Login to router admin panel         │
   │   │ 2. Find Wi-Fi channel setting          │
   │   │ 3. Set to recommended channel          │
   │   │ 4. Save and wait 30 seconds           │
   │   └─────────────┬───────────────────────────┘
   │                 │
   │                 ▼
   │   ┌─────────────────────────────────────────┐
   │   │ RE-TEST: Run analyzer again            │
   │   │ Check if problem improved               │
   │   └─────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────┐
│   Network OK?                  │
│   (RSSI good, latency low)     │
└──────────────┬──────────────────┘
               │
        ┌──────┴──────┐
        │             │
        ▼             ▼
       YES            NO
        │             │
        ▼             ▼
   ┌─────────┐  ┌─────────────────────┐
   │ Done!   │  │ Check Other Causes: │
   │ Wi-Fi   │  │ • Too many devices │
   │ Healthy │  │ • Router capacity   │
   └─────────┘  │ • ISP issue        │
                │ • Need 5GHz band   │
                └─────────────────────┘
```

---

## Channel Selection Flow

```
┌─────────────────────────────────┐
│   Need to choose channel?       │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│   Using 2.4GHz or 5GHz?        │
└──────────────┬──────────────────┘
               │
       ┌───────┴───────┐
       │               │
       ▼               ▼
    2.4 GHz         5 GHz
       │               │
       ▼               ▼
┌─────────────┐  ┌─────────────────┐
│ Best: 1,6,11│  │ Best: 36,44,149 │
│             │  │ (least crowded) │
└──────┬──────┘  └────────┬────────┘
       │                    │
       ▼                    ▼
┌─────────────────────┐  ┌─────────────────┐
│ Check congestion for │  │ Check analyzer  │
│   1, 6, and 11      │  │ output for      │
└──────┬──────────────┘  │ recommended     │
       │                  └────────┬────────┘
       ▼                          │
┌─────────────────────┐           ▼
│ Channel with FEWEST │  ┌─────────────────┐
│ networks = BEST     │  │ Pick channel    │
└─────────────────────┘  │ with lowest     │
                         │ network count   │
                         └─────────────────┘
```

---

## Troubleshooting Flow

```
Problem: Slow Wi-Fi
│
├─► Step 1: Run analyzer
│          └─► Is "Impact" = HIGH/CRITICAL?
│                │
│                ├─► YES: Go to Step 2
│                └─► NO:  Go to Step 3
│
├─► Step 2: Check "Recommendations"
│          └─► "Switch to Channel X"
│                │
│                ├─► Make change to router
│                └─► Re-run analyzer
│
├─► Step 3: Check RSSI
│          └─► Is RSSI < -75 dBm?
│                │
│                ├─► YES: Move closer to AP
│                │     or get range extender
│                └─► NO:  Go to Step 4
│
├─► Step 4: Check Noise Floor
│          └─► Is Noise > -80 dBm?
│                │
│                ├─► YES: Find interference source
│                │     (microwave, motors, etc.)
│                └─► NO:  Go to Step 5
│
└─► Step 5: Test Wired Connection
           └─► Is wired also slow?
                 │
                 ├─► YES: Contact ISP
                 └─► NO:  Wi-Fi specific issue
                       Consider 5GHz band
```

---

## Quick Diagnosis Chart

| Your Output Shows | Problem | Solution |
|-------------------|---------|----------|
| Channel 6: 8 networks | Too crowded | Switch to 1 or 11 |
| RSSI: -85 dBm | Weak signal | Move AP or use extender |
| Noise: -70 dBm | High noise | Find & remove source |
| All channels HIGH | Overcrowded | Switch to 5GHz |
| Latency: 200ms | Congestion | Change channel |

---

## Success Criteria

```
✅ After optimization, you should see:

📶 RSSI: > -60 dBm (strong signal)
📊 Noise: < -85 dBm (quiet)
🎯 Impact: LOW or MEDIUM
⚡ Latency: < 50ms
📡 Congestion: LOW on your channel
