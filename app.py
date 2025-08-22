# app.py (THE ABSOLUTE FINAL GUARANTEED VERSION - NO DISK NEEDED)

import os
import tempfile
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__, static_folder='static', static_url_path='')

# Environment se aapki di hui Netscape cookies lega
NETSCAPE_COOKIES_TEXT = os.environ.get("INSTA_COOKIES_TEXT")

# --- API Routes ---
@app.route('/')
def home():
    return send_from_directory('static', 'index.html')

@app.route('/api/get_link', methods=['POST'])
def get_download_link():
    url = request.json.get('url')
    if not url: return jsonify({'error': 'URL nahi mila'}), 400
    if not NETSCAPE_COOKIES_TEXT: return jsonify({'error': 'Instagram cookies load nahi hui'}), 500

    is_story_request = not url.startswith('http') and ' ' not in url
    if is_story_request:
        url = f"https://www.instagram.com/stories/{url}/"

    # Har request ke liye ek temporary cookie file banayenge
    # Yeh file apne aap delete ho jayegi
    with tempfile.NamedTemporaryFile(mode='w+', delete=True, suffix='.txt') as temp_cookie_file:
        temp_cookie_file.write(NETSCAPE_COOKIES_TEXT)
        temp_cookie_file.flush() # Data ko file me force write karenge
        
        try:
            ydl_opts = {
                'quiet': True,
                'format': 'best',
                # Hum temporary file ka path de rahe hain
                'cookiefile': temp_cookie_file.name
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
if NETSCAPE_COOKIES_TEXT:
    print("Perfect cookies successfully loaded! Server is ready.")
else:
    print("ERROR: INSTA_COOKIES_TEXT environment variable nahi mila.")

if __name__ == '__main__':
    app.run(debug=True)
