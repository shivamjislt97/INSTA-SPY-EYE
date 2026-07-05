# Instagram DP Tracker Bot

A Telegram bot that monitors Instagram profile pictures and sends alerts when the DP changes.

## Features

- Monitors Instagram DP changes
- Telegram bot with interactive buttons
- Manual DP check via command or button
- Startup notification on Telegram
- SQLite database (no server needed)
- Auto-start on Lightning AI Studio startup

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

## Commands

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

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `INSTAGRAM_USERNAME` | Target Instagram username | Yes |
| `CHECK_INTERVAL_CRON` | Cron schedule (e.g., `0 */2 * * *`) | Yes |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | Yes |
| `TELEGRAM_CHAT_ID` | Telegram chat ID | Yes |

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
