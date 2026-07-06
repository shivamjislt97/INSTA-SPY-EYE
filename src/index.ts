import fs from 'fs';
import path from 'path';
import { config } from './config';
import { fetchProfilePicture } from './instagram';
import { computeHash } from './hash';
import { getBotState, updateBotState, insertDpHistory } from './db';
import { sendTelegramMessage, sendTelegramPhoto, initTelegramBot, setCheckFunction } from './notify';

const STORAGE_DIR = path.resolve(__dirname, '..', 'storage', 'dp-images');

function ensureStorageDir(): void {
  if (!fs.existsSync(STORAGE_DIR)) {
    fs.mkdirSync(STORAGE_DIR, { recursive: true });
  }
}

function formatTimestamp(date: Date): string {
  return date.toISOString().replace(/[:.]/g, '-');
}

export async function runCheckCycle(chatId?: number): Promise<string> {
  ensureStorageDir();
  const username = config.INSTAGRAM_USERNAME;
  const now = new Date();
  let result = '';

  console.log(`\n[${now.toISOString()}] Starting DP check cycle for ${username}...`);

  try {
    console.log('  Fetching profile picture...');
    const { imageUrl, imageBuffer } = await fetchProfilePicture();
    console.log(`  Image size: ${(imageBuffer.length / 1024).toFixed(1)} KB`);

    const imageHash = computeHash(imageBuffer);
    console.log(`  Computed hash: ${imageHash}`);

    const botState = await getBotState();
    const lastHash = botState.lastHash;

    if (lastHash === null) {
      console.log('  First run - saving baseline.');

      const filename = `${formatTimestamp(now)}_${imageHash.slice(0, 6)}.jpg`;
      const localPath = path.join('storage', 'dp-images', filename);
      const fullPath = path.join(STORAGE_DIR, filename);
      fs.writeFileSync(fullPath, imageBuffer);

      await insertDpHistory({
        imageUrl,
        localPath,
        imageHash,
        isChange: true,
      });

      await updateBotState(imageHash);

      result = `Baseline saved!\nUsername: ${username}\nTime: ${now.toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })}`;
      console.log('  Baseline saved.');
    } else if (lastHash === imageHash) {
      console.log('  No change detected.');
      result = `No DP Change detected.\nUsername: ${username}\nLast checked: ${now.toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })}`;
    } else {
      console.log('  DP change detected!');

      const filename = `${formatTimestamp(now)}_${imageHash.slice(0, 6)}.jpg`;
      const localPath = path.join('storage', 'dp-images', filename);
      const fullPath = path.join(STORAGE_DIR, filename);
      fs.writeFileSync(fullPath, imageBuffer);

      await insertDpHistory({
        imageUrl,
        localPath,
        imageHash,
        isChange: true,
      });

      await updateBotState(imageHash);

      const caption = `DP CHANGE DETECTED!\n\nUsername: ${username}\nTime: ${now.toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })}`;
      await sendTelegramPhoto(fullPath, caption);

      result = `New DP detected and saved!\nUsername: ${username}\nTime: ${now.toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })}`;
      console.log('  Change recorded. Photo sent.');
    }

    console.log(`[${now.toISOString()}] Check cycle complete.`);
  } catch (error) {
    console.error(`[${now.toISOString()}] Check cycle failed:`, error);
    result = `Check failed: ${error}`;
  }

  return result;
}

if (require.main === module) {
  console.log('Initializing Telegram bot...');
  setCheckFunction(runCheckCycle);
  initTelegramBot();

  const now = new Date();
  const startupMsg = `Bot Started!\n\nTracking: ${config.INSTAGRAM_USERNAME}\nTime: ${now.toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })}`;
  sendTelegramMessage(startupMsg);

  runCheckCycle().then((checkResult) => {
    sendTelegramMessage(`[Initial Check]\n${checkResult}`);
  });

  // Auto-sleep after 10 minutes
  const SLEEP_AFTER_MS = 10 * 60 * 1000; // 10 minutes
  console.log(`Bot will auto-sleep after 10 minutes...`);

  setTimeout(async () => {
    const sleepMsg = `Bot going to sleep!\n\nTracking: ${config.INSTAGRAM_USERNAME}\nTime: ${new Date().toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })}`;
    await sendTelegramMessage(sleepMsg);
    console.log('Sleep signal sent. Stopping bot...');
    
    // Stop PM2 process
    const { execSync } = require('child_process');
    try {
      execSync('pm2 stop dp-tracker');
      console.log('Bot stopped successfully.');
    } catch (error) {
      console.error('Error stopping bot:', error);
    }
    process.exit(0);
  }, SLEEP_AFTER_MS);
}
