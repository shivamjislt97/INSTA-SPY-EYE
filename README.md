# Instagram DP Tracker Bot

A Telegram bot that monitors Instagram profile pictures and sends alerts when the DP changes.

## Features

- Monitors Instagram DP changes
- Telegram bot with interactive buttons
- Manual DP check via command or button
- Startup notification on Telegram
- SQLite database (no server needed)
- Auto-start on Lightning AI Studio startup
- Auto-sleep after 10 minutes

## How It Works

### What Does This Bot Do?

This bot watches someone's Instagram profile picture (DP). When their DP changes, you get an alert on Telegram with the new DP photo.

### Step-by-Step Working

```
1. Bot starts → Sends "Bot Started!" to Telegram
2. Bot checks Instagram DP → Compares with last saved DP
3. If DP changed → Sends new DP photo to Telegram
4. If DP same → Waits for manual check
5. After 10 minutes → Bot goes to sleep automatically
```

### Detailed Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     HOW BOT WORKS                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. STARTUP                                                 │
│     Studio starts → Bot starts → Telegram: "Bot Started!"   │
│                                                             │
│  2. DP CHECK                                                │
│     Fetch DP from Instagram → Download image → Compute hash │
│                                                             │
│  3. COMPARE                                                 │
│     New hash vs Old hash → Same? or Different?              │
│                                                             │
│  4. RESULT                                                  │
│     Same → "No DP Change detected"                          │
│     Different → Send new DP photo to Telegram               │
│                                                             │
│  5. SLEEP                                                   │
│     After 10 minutes → "Bot going to sleep!" → Bot stops    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## How to Use Guide

### Method 1: Automatic (Recommended)

Just start the studio. The bot will:
1. Auto-start
2. Send "Bot Started!" to Telegram
3. Check DP once
4. Auto-sleep after 10 minutes

### Method 2: Manual Check via Telegram

1. Open Telegram
2. Find your bot
3. Send `/start`
4. Click "Check DP Now" button
5. Wait for result

### Method 3: Manual Check via Terminal

Run this command:
```bash
cd /teamspace/studios/this_studio/dp-tracker && node dist/manual-check.js
```

### Method 4: Manual Check via Shell Script

```bash
bash /teamspace/studios/this_studio/dp-tracker/check-dp.sh
```

## Telegram Bot Usage

### Starting the Bot

1. Open Telegram
2. Search for your bot username
3. Click "Start" or send `/start`
4. You'll see welcome message with buttons

### Available Commands

| Command | What It Does |
|---------|--------------|
| `/start` | Shows welcome message with buttons |
| `/check` | Checks DP and shows result |
| `/status` | Shows bot status |

### Available Buttons

| Button | What It Does |
|--------|--------------|
| **Check DP Now** | Checks DP immediately |
| **Status** | Shows bot status |

### Example Usage

```
You: /start
Bot: Hello! DP Tracker Bot.
     Tracking: taniii_ni
     
     Commands:
     /check - Manual DP check
     /status - Bot status
     
     Press button below:
     [Check DP Now] [Status]

You: Click "Check DP Now"
Bot: Checking DP... Please wait...
Bot: No DP Change detected.
     Username: taniii_ni
     Last checked: 6/7/2026, 4:38:41 am
```

## Architecture

```
dp-tracker/
├── src/
│   ├── index.ts          # Main entry point & check logic
│   ├── config.ts         # Environment variables loader
│   ├── instagram.ts      # Instagram DP fetcher
│   ├── notify.ts         # Telegram bot & notifications
│   ├── db.ts             # Database operations (SQLite)
│   ├── hash.ts           # Image hash computation
│   └── manual-check.ts   # Manual check script
├── prisma/
│   └── schema.prisma     # Database schema
├── storage/
│   └── dp-images/        # Saved DP images
├── dist/                 # Compiled JS files
├── .env                  # Environment variables
├── .env.example          # Example env file
├── check-dp.sh           # Shell script for manual check
├── MASTER_SETUP_PROMPT.md # AI agent setup prompt
└── package.json
```

### Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    STARTUP FLOW                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Studio Starts → on_start.sh → npm install              │
│       ↓                                                 │
│  prisma generate → tsc → pm2 start                      │
│       ↓                                                 │
│  Bot Started → Telegram Alert → DP Check (once)         │
│       ↓                                                 │
│  10 minutes → Auto Sleep                                │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    CHECK FLOW                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Manual Check (Button/Command)                          │
│       ↓                                                 │
│  Fetch Instagram DP → Compute Hash                      │
│       ↓                                                 │
│  Compare with Last Hash                                 │
│       ↓                                                 │
│  ┌─────────────┐    ┌─────────────┐                     │
│  │ No Change   │    │ Change      │                     │
│  │ → Text Msg  │    │ → Photo Msg │                     │
│  └─────────────┘    └─────────────┘                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Installation Guide

### Prerequisites

- Node.js 18+
- npm
- Instagram session cookie
- Telegram bot token

### Step-by-Step Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/shivamjislt97/INSTA-SPY-EYE.git
cd INSTA-SPY-EYE
```

#### 2. Install Dependencies

```bash
npm install
```

#### 3. Setup Database

```bash
npx prisma generate
npx prisma db push
```

#### 4. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` file:

```env
INSTAGRAM_USERNAME=your_target_username
CHECK_INTERVAL_CRON=0 */2 * * *
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

#### 5. Build the Project

```bash
npx tsc
```

#### 6. Start the Bot

```bash
pm2 start dist/index.js --name dp-tracker
pm2 save
```

## Getting Telegram Bot Token

1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Enter a name for your bot
4. Enter a username (must end with `bot`)
5. Copy the token provided

## Getting Telegram Chat ID

1. Send any message to your bot
2. Open this URL in browser:
   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   ```
3. Find `chat.id` in the response

## Commands Reference

### Manual Check (Terminal)

```bash
cd /teamspace/studios/this_studio/dp-tracker && node dist/manual-check.js
```

Or use the shell script:

```bash
bash /teamspace/studios/this_studio/dp-tracker/check-dp.sh
```

### Telegram Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message with buttons |
| `/check` | Manual DP check |
| `/status` | Bot status |

### Telegram Buttons

| Button | Description |
|--------|-------------|
| **Check DP Now** | Triggers manual DP check |
| **Status** | Shows bot status |

## Auto-Start Configuration

The bot auto-starts when Lightning AI Studio starts via `.lightning_studio/on_start.sh`:

```bash
#!/bin/bash
cd /teamspace/studios/this_studio/dp-tracker
npm install
npx prisma generate
npx tsc
pm2 start dist/index.js --name dp-tracker
pm2 save
```

## Auto-Sleep Feature

The bot automatically goes to sleep after 10 minutes:

1. Bot starts → Sends "Bot Started!" to Telegram
2. Checks DP once
3. After 10 minutes → Sends "Bot going to sleep!" to Telegram
4. Bot stops automatically

To restart the bot:
```bash
pm2 start dp-tracker
```

## PM2 Commands

```bash
# Check status
pm2 status

# View logs
pm2 logs dp-tracker

# Restart bot
pm2 restart dp-tracker

# Stop bot
pm2 stop dp-tracker

# Save process list
pm2 save
```

## Checklist

- [ ] Node.js installed
- [ ] npm installed
- [ ] Repository cloned
- [ ] Dependencies installed (`npm install`)
- [ ] Database setup (`npx prisma generate && npx prisma db push`)
- [ ] `.env` file configured
- [ ] Telegram bot created
- [ ] Chat ID obtained
- [ ] Project built (`npx tsc`)
- [ ] Bot started (`pm2 start dist/index.js --name dp-tracker`)
- [ ] Process saved (`pm2 save`)
- [ ] Auto-start configured (`on_start.sh`)
- [ ] Telegram startup notification received
- [ ] Auto-sleep working (after 10 minutes)

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `INSTAGRAM_USERNAME` | Target Instagram username | Yes |
| `CHECK_INTERVAL_CRON` | Cron schedule (e.g., `0 */2 * * *`) | Yes |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | Yes |
| `TELEGRAM_CHAT_ID` | Telegram chat ID | Yes |

## Quick Start Guide

### For First-Time Users

1. **Clone and setup:**
   ```bash
   git clone https://github.com/shivamjislt97/INSTA-SPY-EYE.git
   cd INSTA-SPY-EYE
   npm install
   npx prisma generate
   npx prisma db push
   ```

2. **Configure:**
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

3. **Build and run:**
   ```bash
   npx tsc
   pm2 start dist/index.js --name dp-tracker
   ```

4. **Check Telegram for "Bot Started!" message**

### For AI Agent Setup

Use the `MASTER_SETUP_PROMPT.md` file:
1. Copy the prompt from the file
2. Paste in any AI agent
3. Let it run all commands automatically

## Troubleshooting

### Bot not starting

```bash
pm2 logs dp-tracker
```

### Instagram fetch error

- Check if session cookie is expired
- Update `SESSION_COOKIE` in `src/instagram.ts`

### Telegram not responding

- Verify bot token is correct
- Verify chat ID is correct
- Check if bot is blocked by user

### Database errors

```bash
npx prisma generate
npx prisma db push
pm2 restart dp-tracker
```

## License

MIT
