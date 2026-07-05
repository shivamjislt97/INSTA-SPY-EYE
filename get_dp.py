import instaloader
import sys
import json
import os

os.environ['https_proxy'] = 'socks5h://188.93.140.146:1080'
os.environ['http_proxy'] = 'socks5h://188.93.140.146:1080'

def get_profile_pic(username):
    L = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        quiet=True
    )
    
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        
        pic_url = None
        try:
            pic_url = profile.profile_pic_url
        except:
            pass
        
        if not pic_url:
            try:
                pic_url = profile.profile_pic_url
            except:
                pass
        
        if pic_url:
            result = {
                "success": True,
                "imageUrl": pic_url,
                "username": username,
                "is_private": profile.is_private,
                "followers": profile.followers
            }
        else:
            result = {
                "success": False,
                "error": "No profile picture URL found"
            }
    except Exception as e:
        result = {
            "success": False,
            "error": str(e)
        }
    
    print(json.dumps(result))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "Username required"}))
        sys.exit(1)
    
    get_profile_pic(sys.argv[1])
