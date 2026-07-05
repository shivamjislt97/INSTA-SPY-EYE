import dotenv from 'dotenv';
import path from 'path';

dotenv.config({ path: path.resolve(__dirname, '..', '.env') });

interface Config {
  INSTAGRAM_USERNAME: string;
  CHECK_INTERVAL_CRON: string;
  TELEGRAM_BOT_TOKEN: string;
  TELEGRAM_CHAT_ID: string;
}

function loadConfig(): Config {
  const required = [
    'INSTAGRAM_USERNAME',
    'CHECK_INTERVAL_CRON',
    'TELEGRAM_BOT_TOKEN',
    'TELEGRAM_CHAT_ID',
  ];

  const missing = required.filter((key) => !process.env[key]);

  if (missing.length > 0) {
    throw new Error(
      `Missing required environment variables: ${missing.join(', ')}\n` +
      'Copy .env.example to .env and fill in the values.'
    );
  }

  return {
    INSTAGRAM_USERNAME: process.env.INSTAGRAM_USERNAME!,
    CHECK_INTERVAL_CRON: process.env.CHECK_INTERVAL_CRON!,
    TELEGRAM_BOT_TOKEN: process.env.TELEGRAM_BOT_TOKEN!,
    TELEGRAM_CHAT_ID: process.env.TELEGRAM_CHAT_ID!,
  };
}

export const config = loadConfig();
