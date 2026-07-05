# Master Setup Prompt for AI Agent

## Copy and paste this prompt to any AI agent to auto-setup the entire system

---

## PROMPT START

You are an expert DevOps engineer. Your task is to set up the Instagram DP Tracker Bot from scratch. Follow ALL steps below EXACTLY. Do NOT skip any step. Do NOT ask questions. Execute every command.

### STEP 1: Clone Repository

```bash
cd /teamspace/studios/this_studio
git clone https://github.com/shivamjislt97/INSTA-SPY-EYE.git dp-tracker
cd dp-tracker
```

### STEP 2: Install Dependencies

```bash
npm install
```

### STEP 3: Setup Database (SQLite)

```bash
npx prisma generate
npx prisma db push
```

### STEP 4: Configure Environment Variables

Create `.env` file with the following content:

```bash
cat > .env << 'EOF'
INSTAGRAM_USERNAME=taniii_ni
CHECK_INTERVAL_CRON=0 */2 * * *
TELEGRAM_BOT_TOKEN=8980206929:AAHP4JiHlgBCBb_dfYEaeo3fdWKqBtwZhZA
TELEGRAM_CHAT_ID=6267031612
EOF
```

### STEP 5: Build TypeScript

```bash
npx tsc
```

### STEP 6: Install PM2 (if not installed)

```bash
npm install -g pm2
```

### STEP 7: Start Bot with PM2

```bash
pm2 start dist/index.js --name dp-tracker
pm2 save
```

### STEP 8: Verify Bot is Running

```bash
pm2 status
pm2 logs dp-tracker --lines 10 --nostream
```

### STEP 9: Setup Auto-Start on Studio Launch

Update `.lightning_studio/on_start.sh` with:

```bash
cat > /teamspace/studios/this_studio/.lightning_studio/on_start.sh << 'EOF'
#!/bin/bash

# This script runs every time your Studio starts

# Auto-start DP Tracker Bot
cd /teamspace/studios/this_studio/dp-tracker
npm install
npx prisma generate
npx tsc
pm2 start dist/index.js --name dp-tracker
pm2 save
EOF
chmod +x /teamspace/studios/this_studio/.lightning_studio/on_start.sh
```

### STEP 10: Test Manual Check

```bash
cd /teamspace/studios/this_studio/dp-tracker && node dist/manual-check.js
```

### STEP 11: Final Verification

Run these commands and confirm output:

```bash
# Check PM2 status
pm2 status

# Check bot logs
pm2 logs dp-tracker --lines 5 --nostream

# Check database exists
ls -la /teamspace/studios/this_studio/dp-tracker/prisma/dev.db

# Check compiled files exist
ls -la /teamspace/studios/this_studio/dp-tracker/dist/

# Check on_start.sh exists
cat /teamspace/studios/this_studio/.lightning_studio/on_start.sh
```

### EXPECTED RESULTS

After completing all steps:

1. Bot status should be "online" in PM2
2. Telegram should receive "Bot Started!" notification
3. Manual check should return "No DP Change detected" or "New DP detected"
4. `dist/` folder should contain compiled JS files
5. `prisma/dev.db` should exist
6. `.lightning_studio/on_start.sh` should have auto-start commands

### TROUBLESHOOTING

If bot fails to start:

```bash
# Check error logs
pm2 logs dp-tracker --err --lines 20 --nostream

# Restart bot
pm2 restart dp-tracker

# If database error, regenerate
cd /teamspace/studios/this_studio/dp-tracker
npx prisma generate
npx prisma db push
pm2 restart dp-tracker
```

### MANUAL CHECK COMMAND

To manually check DP anytime:

```bash
cd /teamspace/studios/this_studio/dp-tracker && node dist/manual-check.js
```

### TELEGRAM BOT COMMANDS

- `/start` - Welcome message with buttons
- `/check` - Manual DP check
- `/status` - Bot status

### PM2 COMMANDS

```bash
pm2 status              # Check bot status
pm2 logs dp-tracker     # View live logs
pm2 restart dp-tracker  # Restart bot
pm2 stop dp-tracker     # Stop bot
pm2 save                # Save process list
```

---

## PROMPT END

---

## How to Use

1. Copy everything between "PROMPT START" and "PROMPT END"
2. Paste it in any AI agent (ChatGPT, Claude, etc.)
3. The AI agent will execute all commands automatically
4. Wait for completion
5. Check Telegram for "Bot Started!" notification

## Verification Checklist

After running the prompt, verify:

- [ ] Bot is running (`pm2 status` shows online)
- [ ] Telegram received startup notification
- [ ] Manual check works (`node dist/manual-check.js`)
- [ ] Database file exists (`prisma/dev.db`)
- [ ] Auto-start script configured (`on_start.sh`)
