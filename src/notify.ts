import axios from 'axios';
import fs from 'fs';
import TelegramBot from 'node-telegram-bot-api';
import { config } from './config';

let bot: TelegramBot | null = null;
let checkFunction: (chatId?: number) => Promise<string> = async () => 'Not configured';

export function setCheckFunction(fn: (chatId?: number) => Promise<string>): void {
  checkFunction = fn;
}

export function initTelegramBot(): void {
  bot = new TelegramBot(config.TELEGRAM_BOT_TOKEN, { polling: true });

  bot.onText(/\/start/, (msg) => {
    const chatId = msg.chat.id;
    const keyboard = {
      inline_keyboard: [
        [{ text: 'Check DP Now', callback_data: 'check_dp' }],
        [{ text: 'Status', callback_data: 'status' }],
      ],
    };

    bot!.sendMessage(
      chatId,
      'Hello! DP Tracker Bot.\n\n' +
      'Tracking: ' + config.INSTAGRAM_USERNAME + '\n\n' +
      'Commands:\n' +
      '/check - Manual DP check\n' +
      '/status - Bot status\n\n' +
      'Press button below:',
      { reply_markup: keyboard }
    );
  });

  bot.onText(/\/check/, async (msg) => {
    const chatId = msg.chat.id;
    bot!.sendMessage(chatId, 'Checking DP... Please wait...');
    const result = await checkFunction(chatId);
    bot!.sendMessage(chatId, result);
  });

  bot.onText(/\/status/, async (msg) => {
    const chatId = msg.chat.id;
    bot!.sendMessage(
      chatId,
      'Bot Status\n\n' +
      'Tracking: ' + config.INSTAGRAM_USERNAME + '\n' +
      'Interval: ' + config.CHECK_INTERVAL_CRON + '\n' +
      'Status: Online'
    );
  });

  bot.on('callback_query', async (query) => {
    const chatId = query.message?.chat.id;
    if (!chatId) return;

    if (query.data === 'check_dp') {
      bot!.answerCallbackQuery(query.id, { text: 'Checking DP...' });
      bot!.sendMessage(chatId, 'Checking DP... Please wait...');
      const result = await checkFunction(chatId);
      bot!.sendMessage(chatId, result);
    } else if (query.data === 'status') {
      bot!.answerCallbackQuery(query.id, { text: 'Showing status...' });
      bot!.sendMessage(
        chatId,
        'Bot Status\n\n' +
        'Tracking: ' + config.INSTAGRAM_USERNAME + '\n' +
        'Interval: ' + config.CHECK_INTERVAL_CRON + '\n' +
        'Status: Online'
      );
    }
  });

  console.log('Telegram bot started with polling.');
}

export async function sendTelegramMessage(text: string): Promise<void> {
  try {
    await bot!.sendMessage(config.TELEGRAM_CHAT_ID, text);
  } catch (error) {
    console.error('[TELEGRAM ERROR]', error);
  }
}

export async function sendTelegramPhoto(imagePath: string, caption: string): Promise<void> {
  try {
    await bot!.sendPhoto(config.TELEGRAM_CHAT_ID, imagePath, { caption });
  } catch (error) {
    console.error('[TELEGRAM PHOTO ERROR]', error);
  }
}
