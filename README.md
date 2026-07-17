# Instagram SPY EYE

Instagram DP Monitor with Telegram Notifications. Detects DP changes, bio changes, and sends instant alerts via Telegram bot.

## Features

- DP Change Detection (Perceptual Hash)
- Bio Change Detection
- Telegram Notifications with Image
- Automatic Monitoring (every hour)
- Single Check Mode (for cron/scheduling)

## Files

| File | Description |
|------|-------------|
| `instagram_monitor_bot.py` | Main bot - monitor + notifications |
| `instagram_dp_downloader.py` | Standalone DP downloader tool |
| `instagram_monitor_data.json` | Stored hashes & profile data |
| `requirements.txt` | Python dependencies |
| `Dockerfile` | Docker deployment config |

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Config
Edit `instagram_monitor_bot.py`:
```python
BOT_TOKEN = "your_telegram_bot_token"
CHAT_ID = "your_telegram_chat_id"
```

### 3. Add Profile
```bash
python instagram_monitor_bot.py
# Select option 1: Add profile
# Enter username (e.g., taniii_ni)
```

### 4. Start Monitoring
```bash
# Continuous (terminal must stay open)
python instagram_monitor_bot.py --monitor

# Single check (for cron/scheduling)
python instagram_monitor_bot.py --once
```

## Commands

| Command | Description |
|---------|-------------|
| `python instagram_monitor_bot.py` | Interactive menu |
| `python instagram_monitor_bot.py --once` | Single check & exit |
| `python instagram_monitor_bot.py --monitor` | Continuous monitoring |
| `python instagram_dp_downloader.py <url>` | Download single DP |

## Deploy on Cloud

### GitHub Actions (Free - every hour)
```yaml
on:
  schedule:
    - cron: '0 * * * *'
```

### Lightning.ai / Render / Railway
```bash
python instagram_monitor_bot.py --once
```

### Docker
```bash
docker build -t insta-spy-eye .
docker run insta-spy-eye
```

## How It Works

1. Downloads Instagram DP via indown.io
2. Calculates perceptual hash (pHash)
3. Compares with stored hash
4. If different -> sends Telegram notification with new DP
5. Same for bio changes (meta tag scraping)

## Telegram Bot Setup

1. Message `@BotFather` on Telegram
2. Send `/newbot` and follow instructions
3. Get your bot token
4. Start your bot, then visit:
   `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
5. Find your `chat.id` in the response

## License

MIT
