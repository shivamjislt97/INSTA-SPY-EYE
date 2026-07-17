#!/usr/bin/env python3
"""
Instagram DP Monitor - Telegram Bot
Har ghante Instagram profile check karta hai aur change detect hone pe Telegram pe notify karta hai.
"""

import re
import os
import sys
import json
import time
import hashlib
import requests
from datetime import datetime
from urllib.parse import urlparse
from io import BytesIO

try:
    import imagehash
    from PIL import Image
    HAS_IMAGEHASH = True
except ImportError:
    HAS_IMAGEHASH = False
    print("Warning: imagehash/Pillow not installed. DP comparison using MD5 hash.")

# ============== CONFIG ==============
BOT_TOKEN = "8980206929:AAF_t_akPdu09o0F5xcyF8K9zAKR8JYUAdU"  # Yaha apna bot token dalo
CHAT_ID = "6267031612"    # Yaha apna chat ID dalo
CHECK_INTERVAL = 3600  # 1 hour in seconds
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "instagram_monitor_data.json")

# Browser headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://indown.io/insta-dp-viewer",
    "Origin": "https://indown.io",
}

BASE_URL = "https://indown.io"
DP_VIEWER_URL = f"{BASE_URL}/insta-dp-viewer"
DOWNLOAD_URL = f"{BASE_URL}/download"


# ============== STORAGE ==============
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"profiles": {}}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ============== TELEGRAM ==============
def send_telegram_message(text, photo_bytes=None):
    if not BOT_TOKEN or not CHAT_ID:
        print("  [Telegram] BOT_TOKEN ya CHAT_ID set nahi hai!")
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    if photo_bytes:
        # Photo ke saath message bhejo
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        files = {"photo": ("dp.jpg", photo_bytes, "image/jpeg")}
        data = {"chat_id": CHAT_ID, "caption": text, "parse_mode": "HTML"}
        try:
            resp = requests.post(url, data=data, files=files, timeout=30)
            return resp.status_code == 200
        except Exception as e:
            print(f"  [Telegram] Error: {e}")
            return False
    else:
        data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
        try:
            resp = requests.post(url, data=data, timeout=15)
            return resp.status_code == 200
        except Exception as e:
            print(f"  [Telegram] Error: {e}")
            return False


# ============== INSTAGRAM ==============
def extract_username(url):
    url = url.strip().rstrip("/")
    parsed = urlparse(url)
    path_parts = [p for p in parsed.path.split("/") if p]
    if path_parts:
        return path_parts[0]
    return None


def extract_csrf_token(html):
    match = re.search(r'name=["\']_token["\']\s+value=["\']([^"\']+)["\']', html)
    if match:
        return match.group(1)
    match = re.search(r'value=["\']([^"\']+)["\']\s+name=["\']_token["\']', html)
    if match:
        return match.group(1)
    return None


def get_dp_url(username):
    """indown.io se DP URL nikalta hai."""
    session = requests.Session()
    session.headers.update(HEADERS)

    # CSRF token lo
    try:
        resp = session.get(DP_VIEWER_URL, timeout=15)
        resp.raise_for_status()
    except Exception:
        return None, None

    token = extract_csrf_token(resp.text)
    if not token:
        return None, None

    # POST request
    post_data = {
        "referer": DP_VIEWER_URL,
        "locale": "en",
        "_token": token,
        "link": f"https://www.instagram.com/{username}/",
    }

    try:
        resp = session.post(DOWNLOAD_URL, data=post_data, timeout=20)
        resp.raise_for_status()
    except Exception:
        return None, None

    # CDN URLs extract karo
    a_matches = re.findall(r'<a[^>]+href=["\']([^"\']+)["\']', resp.text, re.IGNORECASE)
    for url in a_matches:
        url = url.replace("&amp;", "&")
        if "cdninstagram" in url or "scontent" in url or "fbcdn" in url:
            return url, session

    return None, None


def download_dp(url, session):
    """DP download karo aur bytes return karo."""
    try:
        resp = session.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return resp.content
    except Exception:
        return None


def get_image_hash(image_bytes):
    """Image ka perceptual hash nikalo."""
    if HAS_IMAGEHASH and image_bytes:
        try:
            img = Image.open(BytesIO(image_bytes))
            return str(imagehash.phash(img))
        except Exception:
            pass
    # Fallback: MD5 hash
    if image_bytes:
        return hashlib.md5(image_bytes).hexdigest()
    return None


def get_profile_bio(username):
    """Instagram profile page se bio nikalo."""
    try:
        resp = requests.get(
            f"https://www.instagram.com/{username}/",
            headers={"User-Agent": HEADERS["User-Agent"]},
            timeout=15
        )
        # Meta description se bio nikalo
        match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)["\']', resp.text, re.IGNORECASE)
        if match:
            bio = match.group(1)
            # Instagram ka default description remove karo
            if "Followers" in bio and "Following" in bio:
                # "X Followers, Y Following, Z Posts - See Instagram photos..." format
                parts = bio.split(" - ")
                if len(parts) > 1:
                    return parts[0].strip()
            return bio
    except Exception:
        pass
    return None


# ============== CHECKER ==============
def check_profile(username, stored_data):
    """Profile check karo aur changes return karo."""
    changes = []
    now = datetime.now().isoformat()

    print(f"  Checking @{username}...")

    # DP check
    dp_url, session = get_dp_url(username)
    if dp_url and session:
        dp_bytes = download_dp(dp_url, session)
        if dp_bytes:
            new_hash = get_image_hash(dp_bytes)
            old_hash = stored_data.get("dp_hash")

            if old_hash and new_hash and old_hash != new_hash:
                changes.append(("dp", dp_bytes))
                print(f"    DP CHANGED!")
            elif not old_hash:
                print(f"    DP hash stored (first time)")
            else:
                print(f"    DP same hai")

            stored_data["dp_hash"] = new_hash
        else:
            print(f"    DP download fail")
    else:
        print(f"    DP URL nahi mila")

    # Bio check
    new_bio = get_profile_bio(username)
    if new_bio:
        old_bio = stored_data.get("bio")
        if old_bio and new_bio != old_bio:
            changes.append(("bio", new_bio))
            print(f"    BIO CHANGED!")
            print(f"      Old: {old_bio[:50]}...")
            print(f"      New: {new_bio[:50]}...")
        elif not old_bio:
            print(f"    Bio stored (first time)")
        else:
            print(f"    Bio same hai")
        stored_data["bio"] = new_bio
    else:
        print(f"    Bio nahi mili")

    stored_data["last_checked"] = now
    return changes


# ============== MAIN ==============
def monitor_profiles(profiles_list):
    """Main monitoring loop."""
    data = load_data()

    print("\n" + "=" * 50)
    print("  Instagram DP Monitor Started")
    print(f"  Checking every {CHECK_INTERVAL // 60} minutes")
    print(f"  Monitoring: {', '.join(profiles_list)}")
    print("=" * 50)

    # Startup message
    send_telegram_message(
        f"<b>Instagram Monitor Started</b>\n\n"
        f"Monitoring: {', '.join('@' + p for p in profiles_list)}\n"
        f"Check interval: {CHECK_INTERVAL // 60} minutes"
    )

    while True:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Starting check...")

        for username in profiles_list:
            if username not in data["profiles"]:
                data["profiles"][username] = {}

            changes = check_profile(username, data["profiles"][username])

            for change_type, change_data in changes:
                if change_type == "dp":
                    msg = (
                        f"<b>DP Changed!</b>\n\n"
                        f"Profile: @{username}\n"
                        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    send_telegram_message(msg, photo_bytes=change_data)
                elif change_type == "bio":
                    msg = (
                        f"<b>Bio Changed!</b>\n\n"
                        f"Profile: @{username}\n"
                        f"New Bio: {change_data}\n"
                        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    send_telegram_message(msg)

        save_data(data)
        print(f"  Next check in {CHECK_INTERVAL // 60} minutes...")
        time.sleep(CHECK_INTERVAL)


def interactive_menu():
    """Interactive menu for bot."""
    data = load_data()

    while True:
        print("\n" + "=" * 50)
        print("  Instagram DP Monitor - Telegram Bot")
        print("=" * 50)
        print("1. Add profile to monitor")
        print("2. Remove profile")
        print("3. List monitored profiles")
        print("4. Check all profiles now")
        print("5. Set Telegram config")
        print("6. Start auto monitoring")
        print("7. Exit")
        print("-" * 50)

        choice = input("Select option (1-7): ").strip()

        if choice == "1":
            username = input("Instagram username dalo (sirf username, URL nahi): ").strip()
            username = username.replace("https://www.instagram.com/", "").replace("/", "").strip()
            if username:
                if username not in data["profiles"]:
                    data["profiles"][username] = {}
                    save_data(data)
                    print(f"  @{username} added!")
                else:
                    print(f"  @{username} already added hai.")

        elif choice == "2":
            username = input("Username remove karna hai: ").strip()
            if username in data["profiles"]:
                del data["profiles"][username]
                save_data(data)
                print(f"  @{username} removed!")
            else:
                print(f"  @{username} found nahi hua.")

        elif choice == "3":
            profiles = list(data["profiles"].keys())
            if profiles:
                print("\n  Monitored profiles:")
                for p in profiles:
                    last = data["profiles"][p].get("last_checked", "Never")
                    print(f"    - @{p} (Last: {last[:16] if last != 'Never' else 'Never'})")
            else:
                print("  Koi profile add nahi kiya abhi.")

        elif choice == "4":
            profiles = list(data["profiles"].keys())
            if not profiles:
                print("  Pehle profile add karo!")
                continue
            print("\n  Checking all profiles...")
            for username in profiles:
                changes = check_profile(username, data["profiles"][username])
                if changes:
                    for change_type, change_data in changes:
                        if change_type == "dp":
                            send_telegram_message(
                                f"<b>DP Changed!</b>\n\nProfile: @{username}",
                                photo_bytes=change_data
                            )
                        elif change_type == "bio":
                            send_telegram_message(
                                f"<b>Bio Changed!</b>\n\nProfile: @{username}\nNew: {change_data}"
                            )
                    print(f"  Changes detected for @{username}! Telegram pe notify kiya.")
                else:
                    print(f"  @{username} - koi change nahi.")
            save_data(data)

        elif choice == "5":
            global BOT_TOKEN, CHAT_ID
            print("\n  Telegram Bot Setup:")
            print("  1. @BotFather ko /newbot bhejo Telegram pe")
            print("  2. Bot token mil jayega")
            print("  3. Bot ko start karo, phir https://api.telegram.org/bot<TOKEN>/getUpdates se Chat ID nikalo")
            print()
            BOT_TOKEN = input("Bot Token: ").strip()
            CHAT_ID = input("Chat ID: ").strip()
            if BOT_TOKEN and CHAT_ID:
                # Test message
                if send_telegram_message("<b>Test Message</b>\n\nBot connected successfully!"):
                    print("  Test message sent! Telegram pe check karo.")
                else:
                    print("  Test message failed. Token aur Chat ID check karo.")

        elif choice == "6":
            profiles = list(data["profiles"].keys())
            if not profiles:
                print("  Pehle profile add karo!")
                continue
            if not BOT_TOKEN or not CHAT_ID:
                print("  Pehle Telegram config set karo (option 5)!")
                continue
            monitor_profiles(profiles)

        elif choice == "7":
            print("Bye!")
            break


def check_once(profiles_list):
    """Single check - run once and exit (for cron/scheduling)."""
    data = load_data()
    print(f"Checking {len(profiles_list)} profile(s)...")

    for username in profiles_list:
        if username not in data["profiles"]:
            data["profiles"][username] = {}

        changes = check_profile(username, data["profiles"][username])

        for change_type, change_data in changes:
            if change_type == "dp":
                send_telegram_message(
                    f"<b>DP Changed!</b>\n\nProfile: @{username}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    photo_bytes=change_data
                )
                print(f"  @{username}: DP CHANGED - Notified!")
            elif change_type == "bio":
                send_telegram_message(
                    f"<b>Bio Changed!</b>\n\nProfile: @{username}\nNew: {change_data}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                print(f"  @{username}: BIO CHANGED - Notified!")

        data["profiles"][username]["last_checked"] = datetime.now().isoformat()

    save_data(data)
    print("Done!")


if __name__ == "__main__":
    # Check for command line args
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Single check mode (for cron/scheduling): python instagram_monitor_bot.py --once
        data = load_data()
        profiles = list(data["profiles"].keys())
        if profiles:
            check_once(profiles)
        else:
            print("No profiles! Add profiles first using interactive menu.")
    elif len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        # Continuous monitoring: python instagram_monitor_bot.py --monitor username1 username2
        profiles = sys.argv[2:]
        if not profiles:
            data = load_data()
            profiles = list(data["profiles"].keys())
        if profiles:
            monitor_profiles(profiles)
        else:
            print("No profiles to monitor! Run without --monitor to add profiles.")
    else:
        interactive_menu()
