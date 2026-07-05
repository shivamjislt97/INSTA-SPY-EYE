import axios from 'axios';
import { runCheckCycle } from './index';
import { config } from './config';

async function main() {
  console.log('=== Manual DP Check ===\n');
  const result = await runCheckCycle();
  console.log('\n' + result);

  try {
    await axios.post(
      `https://api.telegram.org/bot${config.TELEGRAM_BOT_TOKEN}/sendMessage`,
      {
        chat_id: config.TELEGRAM_CHAT_ID,
        text: `Manual Check Result:\n\n${result}`,
      },
      { timeout: 10000 }
    );
    console.log('\nResult sent to Telegram!');
  } catch (error) {
    console.error('\nFailed to send to Telegram:', error);
  }

  console.log('\n=== Done ===');
  process.exit(0);
}

main();
