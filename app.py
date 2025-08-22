# app.py (FINAL VERSION WITH QUALITY SELECTION)

import os
import tempfile
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__, static_folder='static', static_url_path='')

NETSCAPE_COOKIES_TEXT = os.environ.get("INSTA_COOKIES_TEXT")

@app.route('/')
def home():
    return send_from_directory('static', 'index.html')

@app.route('/api/get_link', methods=['POST'])
def get_download_link():
    data = request.get_json()
    url = data.get('url')
    # YEH LINE NAYI HAI: Hum frontend se quality le rahe hain
    quality = data.get('quality', '720') # Default 720p hai agar kuchh na aaye

    if not url: return jsonify({'error': 'URL nahi mila'}), 400
    if not NETSCAPE_COOKIES_TEXT: return jsonify({'error': 'Instagram cookies load nahi hui'}), 500

    is_story_request = not url.startswith('http') and ' ' not in url
    if is_story_request:
        url = f"https://www.instagram.com/stories/{url}/"

    # YEH HISSA NAYA HAI: Quality ke hisaab se format set kar rahe hain
    quality_formats = {
        '1080': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        '720': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        '360': 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
    }
    # Agar frontend se koi galat value aaye, toh default 720p use hoga
    selected_format = quality_formats.get(quality, quality_formats['720'])

    with tempfile.NamedTemporaryFile(mode='w+', delete=True, suffix='.txt') as temp_cookie_file:
        temp_cookie_file.write(NETSCAPE_COOKIES_TEXT)
        temp_cookie_file.flush()
        
        try:
            ydl_opts = {
                'quiet': True,
                # YEH LINE UPDATE HUI HAI: Ab yeh dynamic hai
                'format': selected_format,
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

if NETSCAPE_COOKIES_TEXT:
    print("Perfect cookies successfully loaded! Server is ready.")
else:
    print("ERROR: INSTA_COOKIES_TEXT environment variable nahi mila.")

if __name__ == '__main__':
    app.run(debug=True)
