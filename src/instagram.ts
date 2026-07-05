import { execSync } from 'child_process';
import axios from 'axios';
import { config } from './config';

const SESSION_COOKIE = '80511243444:mxC8zuHGJjI0yq:25:AYh23W6nuuyYpTHsVeo99ZOnCFAw-4Ls5CzbA0qXuA';

interface InstagramFetchResult {
  imageUrl: string;
  imageBuffer: Buffer;
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function fetchProfilePicture(): Promise<InstagramFetchResult> {
  const username = config.INSTAGRAM_USERNAME;

  console.log(`  Fetching CSRF token...`);

  const csrfResponse = execSync(
    `curl -s --max-time 10 \
      -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
      -H "Cookie: sessionid=${SESSION_COOKIE}" \
      "https://www.instagram.com/"`,
    { encoding: 'utf-8', timeout: 15000 }
  );

  const csrfMatch = csrfResponse.match(/csrf_token["\s:]+["\s]*([^"]+)/);
  const csrfToken = csrfMatch ? csrfMatch[1].trim() : '';

  if (!csrfToken) {
    throw new Error('Failed to get CSRF token. Session cookie may be expired.');
  }

  console.log(`  CSRF obtained. Fetching profile via mobile API...`);

  await sleep(1000);

  const apiResponse = execSync(
    `curl -s --max-time 15 \
      -H "User-Agent: Instagram 275.0.0.27.98 (iPhone13,3; iOS 15_6; en_US; en-US; scale=3.00; 1284x2778; 458229258) AppleWebKit/420+" \
      -H "X-IG-App-ID: 936619743392459" \
      -H "Cookie: sessionid=${SESSION_COOKIE}; csrftoken=${csrfToken}" \
      "https://i.instagram.com/api/v1/users/web_profile_info/?username=${username}"`,
    { encoding: 'utf-8', timeout: 20000 }
  );

  let profileData: Record<string, unknown>;
  try {
    profileData = JSON.parse(apiResponse);
  } catch {
    throw new Error('Invalid response from Instagram API');
  }

  const userData = (profileData as { data?: { user?: Record<string, unknown> } })?.data?.user;

  if (!userData) {
    const msg = (profileData as { message?: string })?.message || 'Unknown error';
    throw new Error(`Could not fetch profile: ${msg}`);
  }

  const picUrl =
    (userData.profile_pic_url_hd as string) ||
    (userData.profile_pic_url as string);

  if (!picUrl) {
    throw new Error(`No profile picture found for @${username}`);
  }

  console.log(`  Image URL found. Downloading...`);

  await sleep(1000);

  const imageResponse = await axios.get(picUrl, {
    responseType: 'arraybuffer',
    timeout: 30000,
    headers: {
      'User-Agent': 'Instagram 275.0.0.27.98',
      Cookie: `sessionid=${SESSION_COOKIE}`,
    },
  });

  const imageBuffer = Buffer.from(imageResponse.data);

  if (imageBuffer.length === 0) {
    throw new Error('Downloaded image buffer is empty');
  }

  console.log(`  Image downloaded (${(imageBuffer.length / 1024).toFixed(1)} KB)`);

  return { imageUrl: picUrl, imageBuffer };
}
