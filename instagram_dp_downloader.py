#!/usr/bin/env python3
"""
Instagram DP Downloader - indown.io website ka use karke
Profile picture download karta hai kisi bhi Instagram profile ki.
"""

import re
import sys
import os
import requests
from urllib.parse import urlparse, unquote


# Browser jaise headers taaki Cloudflare block na kare
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://indown.io/insta-dp-viewer",
    "Origin": "https://indown.io",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
}

BASE_URL = "https://indown.io"
DP_VIEWER_URL = f"{BASE_URL}/insta-dp-viewer"
DOWNLOAD_URL = f"{BASE_URL}/download"


def extract_username(url):
    """Instagram URL se username nikalta hai."""
    url = url.strip().rstrip("/")
    parsed = urlparse(url)
    path_parts = [p for p in parsed.path.split("/") if p]
    if path_parts:
        return path_parts[0]
    return "unknown_dp"


def extract_csrf_token(html):
    """HTML se CSRF token (_token) extract karta hai."""
    match = re.search(r'name=["\']_token["\']\s+value=["\']([^"\']+)["\']', html)
    if match:
        return match.group(1)
    match = re.search(r'value=["\']([^"\']+)["\']\s+name=["\']_token["\']', html)
    if match:
        return match.group(1)
    return None


def extract_dp_urls(html):
    """Response HTML se DP image URLs extract karta hai."""
    urls = []

    # Pattern 1: <a href="CDN_URL"> - View ya Download buttons
    a_href_matches = re.findall(r'<a[^>]+href=["\']([^"\']+)["\']', html, re.IGNORECASE)
    for url in a_href_matches:
        # HTML entities decode karo
        url = url.replace("&amp;", "&")
        if is_cdn_url(url):
            urls.append(url)

    # Pattern 2: <img src="CDN_URL"> 
    img_matches = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE)
    for url in img_matches:
        url = url.replace("&amp;", "&")
        if is_cdn_url(url):
            urls.append(url)

    # Pattern 3: data-src, data-url attributes
    data_matches = re.findall(r'data-(?:src|url|image)=["\']([^"\']+)["\']', html, re.IGNORECASE)
    for url in data_matches:
        url = url.replace("&amp;", "&")
        if is_cdn_url(url):
            urls.append(url)

    # Deduplicate karo order maintain karte hue
    seen = set()
    unique_urls = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)

    return unique_urls


def is_cdn_url(url):
    """Check karta hai ki URL Instagram CDN pe hai."""
    url_lower = url.lower()
    return any(cdn in url_lower for cdn in ["cdninstagram", "fbcdn", "scontent"])


def get_download_url(urls):
    """Download URL select karta hai (dl=1 parameter wala)."""
    for url in urls:
        if "dl=1" in url:
            return url
    return urls[0] if urls else None


def download_image(url, filename, session):
    """Image download karta hai aur save karta hai."""
    try:
        print(f"  Downloading...")
        resp = session.get(url, headers=HEADERS, timeout=30, stream=True)
        resp.raise_for_status()

        content_type = resp.headers.get("content-type", "")
        if "png" in content_type:
            ext = ".png"
        elif "webp" in content_type:
            ext = ".webp"
        else:
            ext = ".jpg"

        if not filename.endswith((".jpg", ".jpeg", ".png", ".webp")):
            filename = filename + ext

        with open(filename, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        file_size = os.path.getsize(filename)
        print(f"  Saved: {filename} ({file_size:,} bytes)")
        return True

    except Exception as e:
        print(f"  Download failed: {e}")
        return False


def main():
    print("=" * 50)
    print("  Instagram DP Downloader (via indown.io)")
    print("=" * 50)
    print()

    if len(sys.argv) > 1:
        instagram_url = sys.argv[1]
    else:
        instagram_url = input("Instagram profile URL dalo: ").strip()

    if not instagram_url:
        print("Error: URL empty hai!")
        return

    username = extract_username(instagram_url)
    print(f"\nProfile: {username}")
    print(f"URL: {instagram_url}")

    session = requests.Session()
    session.headers.update(HEADERS)

    # Step 1: CSRF token lo
    print("\n[1/4] CSRF token le rahe hain...")
    try:
        resp = session.get(DP_VIEWER_URL, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Error: Page load nahi ho paya: {e}")
        return

    token = extract_csrf_token(resp.text)
    if not token:
        print("Error: CSRF token nahi mila!")
        return
    print(f"  Token mila!")

    # Step 2: POST request
    print("\n[2/4] Instagram profile fetch ho raha hai...")
    post_data = {
        "referer": DP_VIEWER_URL,
        "locale": "en",
        "_token": token,
        "link": instagram_url,
    }

    try:
        resp = session.post(DOWNLOAD_URL, data=post_data, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Error: POST request fail: {e}")
        return

    print(f"  Status: {resp.status_code}")

    # Step 3: DP URLs extract
    print("\n[3/4] DP image dhundh rahe hain...")
    dp_urls = extract_dp_urls(resp.text)

    if not dp_urls:
        print("  Koi DP image nahi mili!")
        # Check for errors
        if "captcha" in resp.text.lower():
            print("  Cloudflare captcha detect hua!")
        elif "not found" in resp.text.lower() or "error" in resp.text.lower():
            error_match = re.search(r'class=["\'][^"\']*error[^"\']*["\'][^>]*>([^<]+)<', resp.text, re.IGNORECASE)
            if error_match:
                print(f"  Error: {error_match.group(1).strip()}")
        return

    print(f"  {len(dp_urls)} URLs mile!")

    # Download URL select karo
    download_url = get_download_url(dp_urls)

    # Step 4: Download
    print(f"\n[4/4] Download ho raha hai...")
    filename = f"{username}_dp"
    success = download_image(download_url, filename, session)

    if success:
        print("\n" + "=" * 50)
        print("  Download complete!")
        print(f"  File: {os.path.abspath(filename)}")
        print("=" * 50)
    else:
        print("\nDownload fail ho gaya.")


if __name__ == "__main__":
    main()
