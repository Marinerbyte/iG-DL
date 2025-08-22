# app.py (FINAL-FINAL VERSION)

import os
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__, static_folder='static', static_url_path='')

# Environment se Netscape cookie string lega
NETSCAPE_COOKIES = os.environ.get("INSTA_COOKIES_TEXT")

# --- API Routes ---
@app.route('/')
def home():
    return send_from_directory('static', 'index.html')

@app.route('/api/get_link', methods=['POST'])
def get_download_link():
    url = request.json.get('url')
    if not url: return jsonify({'error': 'URL nahi mila'}), 400
    if not NETSCAPE_COOKIES: return jsonify({'error': 'Instagram cookies load nahi hui'}), 500

    is_story_request = not url.startswith('http') and ' ' not in url
    if is_story_request:
        url = f"https://www.instagram.com/stories/{url}/"

    try:
        ydl_opts = {
            'quiet': True,
            'format': 'best',
            'cookiefile_string': NETSCAPE_COOKIES
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
        return jsonify({'error': 'URL process nahi kar paaye. Shayad private ya galat URL hai.'}), 500

# --- Server Start ---
if NETSCAPE_COOKIES:
    print("Perfect cookies successfully loaded! Server is ready.")
else:
    print("ERROR: INSTA_COOKIES_TEXT environment variable nahi mila.")

if __name__ == '__main__':
    app.run(debug=True)
