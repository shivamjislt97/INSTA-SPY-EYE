# Instagram SPY EYE

Instagram DP Monitor with Telegram Notifications. Detects DP changes, bio changes, and sends instant alerts via Telegram bot.

---

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    INSTAGRAM SPY EYE                            │
│                   Workflow Diagram                              │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   START      │
│   (Cron/     │
│   Manual)    │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│              instagram_monitor_bot.py --once                 │
│              (Har ghante ya manually run hota hai)           │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 1: Load Stored Data                                    │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ instagram_monitor_data.json se load karo:              │  │
│  │ - Pehle ka DP hash                                     │  │
│  │ - Pehle ka Bio                                         │  │
│  │ - Last checked time                                    │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 2: Instagram Profile Check                             │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                                                        │  │
│  │  ┌─────────────┐     ┌──────────────┐                 │  │
│  │  │ indown.io   │────▶│ CSRF Token   │                 │  │
│  │  │ GET Request │     │ Extract      │                 │  │
│  │  └─────────────┘     └──────┬───────┘                 │  │
│  │                             │                          │  │
│  │                             ▼                          │  │
│  │  ┌─────────────┐     ┌──────────────┐                 │  │
│  │  │ POST with   │────▶│ CDN URL      │                 │  │
│  │  │ Instagram   │     │ Extract      │                 │  │
│  │  │ URL         │     └──────┬───────┘                 │  │
│  │  └─────────────┘            │                          │  │
│  │                             ▼                          │  │
│  │  ┌─────────────────────────────────────┐              │  │
│  │  │  DP Image Download (scontent.cdn..) │              │  │
│  │  └──────────────────┬──────────────────┘              │  │
│  │                     │                                 │  │
│  └─────────────────────┼─────────────────────────────────┘  │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 3: Hash Comparison                                      │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                                                        │  │
│  │  New DP ──▶ Calculate pHash ──▶ Compare with Old Hash  │  │
│  │                                                        │  │
│  │  ┌─────────────────────────────────────────────────┐   │  │
│  │  │ Same Hash?                                      │   │  │
│  │  │                                                 │   │  │
│  │  │  YES ──▶ DP Same (No notification)              │   │  │
│  │  │                                                 │   │  │
│  │  │  NO  ──▶ DP CHANGED! (Send Telegram Alert)     │   │  │
│  │  └─────────────────────────────────────────────────┘   │  │
│  │                                                        │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 4: Bio Check                                           │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                                                        │  │
│  │  Instagram Profile Page ──▶ Meta Tag Extract           │  │
│  │                                                        │  │
│  │  ┌─────────────────────────────────────────────────┐   │  │
│  │  │ Same Bio?                                       │   │  │
│  │  │                                                 │   │  │
│  │  │  YES ──▶ Bio Same (No notification)             │   │  │
│  │  │                                                 │   │  │
│  │  │  NO  ──▶ BIO CHANGED! (Send Telegram Alert)    │   │  │
│  │  └─────────────────────────────────────────────────┘   │  │
│  │                                                        │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 5: Telegram Notification                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                                                        │  │
│  │  ┌─────────────┐         ┌──────────────────────┐     │  │
│  │  │ DP Change?  │──YES───▶│ Send Photo + Caption │     │  │
│  │  └─────────────┘         └──────────────────────┘     │  │
│  │         │                                              │  │
│  │         NO                                             │  │
│  │         │                                              │  │
│  │  ┌──────▼──────┐         ┌──────────────────────┐     │  │
│  │  │ Bio Change? │──YES───▶│ Send Text Message    │     │  │
│  │  └─────────────┘         └──────────────────────┘     │  │
│  │                                                        │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 6: Save & Exit                                         │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ - Update data file with new hash/bio                   │  │
│  │ - Update last_checked timestamp                        │  │
│  │ - Exit (for --once mode)                               │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## How It Works (Simple Explanation)

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  HAR GHANTE KYA HOTA HAI:                                       │
│                                                                 │
│  1. Bot Instagram pe jata hai                                    │
│  2. DP download karta hai                                       │
│  3. DP ka fingerprint (hash) nikalta hai                        │
│  4. Pehle ke hash se compare karta hai                          │
│  5. Agar alag hai = DP badli hai!                               │
│  6. Telegram pe photo aur message bhejta hai                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Telegram Bot Kaise Banaye (Step-by-Step)

### Step 1: BotFather pe jao
1. Telegram app kholo
2. Search karo: **@BotFather**
3. Usko message karo: `/newbot`

### Step 2: Bot ka naam do
```
BotFather: Bot ka naam kya rakhega?
Aap: SPY EYE Bot

BotFather: Bot ka username kya rakhega? (bot suffix hona chahiye)
Aap: spy_eye_never_blink_bot
```

### Step 3: Bot Token lo
```
BotFather: Bot ban gaya! Ye hai token:
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

⚠️ Ye token kisi ko mat do!
```

### Step 4: Chat ID nikalo
1. Apne naye bot ko `/start` bhejo
2. Browser mein jao: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
3. JSON mein `"chat":{"id":123456789}` dikhega - ye tumhara Chat ID hai

### Step 5: Bot mein set karo
```python
# instagram_monitor_bot.py mein:
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
CHAT_ID = "YOUR_CHAT_ID_HERE"
```

---

## Instagram URL Kaise Change Kare

### Method 1: Interactive Menu
```bash
python instagram_monitor_bot.py
```
Menu mein:
- **Option 1**: Add profile (naya username dalo)
- **Option 2**: Remove profile (purana username hatao)
- **Option 3**: List profiles (dekhlo kaun se track ho rahe hain)

### Method 2: Direct Data Edit
`instagram_monitor_data.json` file kholo:
```json
{
  "profiles": {
    "old_username": {                    // ← Ye hatao
      "dp_hash": "...",
      "bio": "..."
    },
    "new_username": {}                   // ← Ye dalo
  }
}
```

### Method 3: Fresh Start
```bash
# Data file delete karo
rm instagram_monitor_data.json

# Bot run karo - naya profile add karo
python instagram_monitor_bot.py
```

### Example: @taniii_ni hatake @cristiano add karna
```bash
python instagram_monitor_bot.py
# Option 2: taniii_ni remove
# Option 1: cristiano add
# Option 6: Start monitoring
```

---

## All Commands Reference

### Installation
```bash
# Clone repo
git clone https://github.com/shivamjislt97/INSTA-SPY-EYE.git
cd INSTA-SPY-EYE

# Install dependencies
pip install -r requirements.txt

# Or manually
pip install requests Pillow imagehash
```

### Bot Commands
```bash
# Interactive menu (recommended for beginners)
python instagram_monitor_bot.py

# Single check mode (for cron/scheduling)
python instagram_monitor_bot.py --once

# Continuous monitoring (terminal must stay open)
python instagram_monitor_bot.py --monitor

# Monitor specific profiles
python instagram_monitor_bot.py --monitor taniii_ni cristiano
```

### DP Downloader (Standalone)
```bash
# Download single DP
python instagram_dp_downloader.py https://www.instagram.com/username/

# Or run interactively
python instagram_dp_downloader.py
# Enter URL when prompted
```

### Docker Commands
```bash
# Build
docker build -t insta-spy-eye .

# Run
docker run insta-spy-eye

# Run with volume (persistent data)
docker run -v ./data:/app insta-spy-eye
```

### Scheduling (Cron)
```bash
# Edit crontab
crontab -e

# Add this line (har ghante):
0 * * * * cd /path/to/INSTA-SPY-EYE && python instagram_monitor_bot.py --once

# Every 30 minutes:
*/30 * * * * cd /path/to/INSTA-SPY-EYE && python instagram_monitor_bot.py --once

# Save and exit
```

### Cloud Deploy Commands
```bash
# Lightning.ai
python instagram_monitor_bot.py --once

# Render (build command)
pip install -r requirements.txt

# Render (start command)
python instagram_monitor_bot.py --once

# Heroku
heroku create insta-spy-eye
git push heroku main
```

---

## Telegram Notification Examples

### DP Change Notification
```
🔔 DP Change Detected!

Profile: @taniii_ni
Change: Profile Picture Updated
Time: 2026-07-17 21:30:00

[Profile Picture Attached]
```

### Bio Change Notification
```
🔔 Bio Change Detected!

Profile: @taniii_ni
Change: Bio Updated

Previous Bio: Living my best life
New Bio: New journey begins

Time: 2026-07-17 21:30:05
```

---

## File Structure

```
INSTA-SPY-EYE/
├── instagram_monitor_bot.py    # Main bot (monitor + notifications)
├── instagram_dp_downloader.py  # Standalone DP downloader
├── instagram_monitor_data.json # Stored data (auto-generated)
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker config
├── README.md                   # This file
└── .gitignore                  # Git ignore rules
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "CSRF token nahi mila" | Website structure change hua hai, wait karo |
| "Koi DP image nahi mili" | Private account hai ya URL galat hai |
| "Telegram message nahi ja raha" | Bot token aur chat ID check karo |
| "Bio nahi mili" | Instagram ne blocking lagayi hai, kuch der baad try karo |
| "Image hash match nahi ho raha" | Normal hai - agar DP same hai toh same hash aayega |

---

## License

MIT
