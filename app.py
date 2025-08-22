# app.py (THE ABSOLUTE FINAL GUARANTEED VERSION)

import os
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__, static_folder='static', static_url_path='')

# Render ka standard, writable path
DISK_PATH = "/var/data"
COOKIE_FILE_PATH = os.path.join(DISK_PATH, "cookies.txt")

# Environment se aapki di hui Netscape cookies lega
NETSCAPE_COOKIES_TEXT = os.environ.get("INSTA_COOKIES_TEXT")

def create_cookie_file():
    """Environment variable se text lekar disk par file banata hai."""
    if not NETSCAPE_COOKIES_TEXT:
        print("ERROR: INSTA_COOKIES_TEXT environment variable nahi mila.")
        return False
    
    try:
        # Hum maan ke chalenge ki Render ne /var/data folder bana diya hai
        with open(COOKIE_FILE_PATH, 'w') as f:
            f.write(NETSCAPE_COOKIES_TEXT)
        
        print(f"Cookie file successfully created on disk at: {COOKIE_FILE_PATH}")
        return True
    except Exception as e:
        print(f"Disk par cookie file banane me error: {e}")
        return False

# --- API Routes ---
@app.route('/')
def home():
    return send_from_directory('static', 'index.html')

@app.route('/api/get_link', methods=['POST'])
def get_download_link():
    url = request.json.get('url')
    if not url: return jsonify({'error': 'URL nahi mila'}), 400
    if not os.path.exists(COOKIE_FILE_PATH):
        return jsonify({'error': 'Instagram cookie file server par nahi hai.'}), 500

    is_story_request = not url.startswith('http') and ' ' not in url
    if is_story_request:
        url = f"https://www.instagram.com/stories/{url}/"

    try:
        ydl_opts = {
            'quiet': True,
            'format': 'best',
            'cookiefile': COOKIE_FILE_PATH
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info and info['entries']: info = info['entries'][0]
            return jsonify({
                'success': True,
                'download_url': info['url'],
                'filename': f"{info.get('id', 'media')}.mp4"
            })
    except Exception as e:
        print(f"Download me error: {e}")
        return jsonify({'error': 'URL process nahi kar paaye. Shayad private ya galat URL hai.'}), 500

# --- Server Start ---
# Server start hote hi cookie file banayega
create_cookie_file()

if __name__ == '__main__':
    app.run(debug=True)
