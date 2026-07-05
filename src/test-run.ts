import fs from 'fs';
import path from 'path';
import { config } from './config';
import { fetchProfilePicture } from './instagram';
import { computeHash } from './hash';
import { getBotState, updateBotState, insertDpHistory } from './db';
import { sendTelegramMessage } from './notify';

const STORAGE_DIR = path.resolve(__dirname, '..', 'storage', 'dp-images');

function formatTimestamp(date: Date): string {
  return date.toISOString().replace(/[:.]/g, '-');
}

async function main(): Promise<void> {
  if (!fs.existsSync(STORAGE_DIR)) {
    fs.mkdirSync(STORAGE_DIR, { recursive: true });
  }

  const username = config.INSTAGRAM_USERNAME;
  const now = new Date();

  console.log(`\n=== DP Tracker Test Run for @${username} ===\n`);

  try {
    console.log(`1. Fetching profile info for @${username}...`);
    const { imageUrl, imageBuffer } = await fetchProfilePicture();
    console.log(`   ✓ HD image URL found: ${imageUrl}`);
    console.log(`   ✓ Image downloaded (${(imageBuffer.length / 1024).toFixed(1)} KB)`);

    const imageHash = computeHash(imageBuffer);
    console.log(`   ✓ Hash computed: ${imageHash}`);

    const botState = await getBotState();
    const lastHash = botState.lastHash;

    if (lastHash === null) {
      console.log('   ✓ Comparing with last stored hash: none found (first run)');
    } else if (lastHash === imageHash) {
      console.log('   ✓ Comparing with last stored hash: matches (no change)');
      await updateBotState(lastHash);
      console.log('\n=== No changes detected. Done. ===');
      return;
    } else {
      console.log(`   ✓ Comparing with last stored hash: differs`);
      console.log(`     Previous: ${lastHash.slice(0, 12)}...`);
      console.log(`     Current:  ${imageHash.slice(0, 12)}...`);
    }

    const filename = `${formatTimestamp(now)}_${imageHash.slice(0, 6)}.jpg`;
    const localPath = path.join('storage', 'dp-images', filename);
    const fullPath = path.join(STORAGE_DIR, filename);
    fs.writeFileSync(fullPath, imageBuffer);
    console.log(`   ✓ Saved to ${localPath}`);

    await insertDpHistory({
      imageUrl,
      localPath,
      imageHash,
      isChange: true,
    });
    console.log('   ✓ DB record created');

    await updateBotState(imageHash);

    await sendTelegramMessage(
      lastHash === null
        ? `Baseline saved for @${username} at ${now.toISOString()}\nHash: ${imageHash.slice(0, 12)}...`
        : `DP change detected for @${username} at ${now.toISOString()}\nNew hash: ${imageHash.slice(0, 12)}...`
    );
    console.log('   ✓ Telegram notification sent');

    console.log('\n=== Test run complete. ===');
  } catch (error) {
    console.error('\n✗ Test run failed:', error);
    process.exit(1);
  }
}

main();
