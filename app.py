# app.py (FINAL VERSION - Uses Browser Cookies)

import os
import json
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__, static_folder='static', static_url_path='')

# Environment se cookie JSON lega
JSON_COOKIES = os.environ.get("INSTA_COOKIES")
netscape_cookie_string = None

def convert_cookies_to_netscape(json_string):
    """Browser cookie JSON ko yt-dlp ke format me convert karega."""
    try:
        cookies = json.loads(json_string)
        lines = ["# Netscape HTTP Cookie File"]
        for cookie in cookies:
            domain = cookie.get('domain', '')
            host_only = str(cookie.get('hostOnly', 'FALSE')).upper()
            path = cookie.get('path', '/')
            secure = str(cookie.get('secure', 'FALSE')).upper()
            # Expiration date ko integer me convert karenge
            expires = str(int(cookie.get('expirationDate', 0)))
            name = cookie.get('name', '')
            value = cookie.get('value', '')
            
            # Netscape format: domain<TAB>hostOnly<TAB>path<TAB>secure<TAB>expires<TAB>name<TAB>value
            line = f"{domain}\t{host_only}\t{path}\t{secure}\t{expires}\t{name}\t{value}"
            lines.append(line)
        
        return "\n".join(lines)
    except Exception as e:
        print(f"Cookie convert karne me error: {e}")
        return None

# --- API Routes ---
@app.route('/')
def home():
    return send_from_directory('static', 'index.html')

@app.route('/api/get_link', methods=['POST'])
def get_download_link():
    url = request.json.get('url')
    if not url: return jsonify({'error': 'URL nahi mila'}), 400
    if not netscape_cookie_string: return jsonify({'error': 'Instagram cookies load nahi hui'}), 500

    # Story ke liye URL ko yt-dlp format me banayenge
    is_story_request = not url.startswith('http') and ' ' not in url
    if is_story_request:
        url = f"instagram:stories:{url}"

    try:
        ydl_opts = {
            'quiet': True,
            'format': 'best',
            'cookiefile_string': netscape_cookie_string
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Agar story hai toh pehla item nikalenge
            if is_story_request:
                if 'entries' in info and info['entries']:
                    info = info['entries'][0]
                else:
                    return jsonify({'error': f'No stories found for user'}), 404

            return jsonify({
                'success': True,
                'download_url': info['url'],
                'filename': f"{info.get('id', 'media')}.mp4"
            })
    except Exception as e:
        print(f"Download me error: {e}")
        return jsonify({'error': 'URL process nahi kar paaye. Shayad private ya galat URL hai.'}), 500

# --- Server Start ---
if JSON_COOKIES:
    netscape_cookie_string = convert_cookies_to_netscape(JSON_COOKIES)
    if netscape_cookie_string:
        print("Browser cookies aasaani se load ho gayi hain! Server taiyaar hai.")
    else:
        print("ERROR: Browser cookies convert nahi ho paayi.")
else:
    print("ERROR: INSTA_COOKIES environment variable nahi mila.")

if __name__ == '__main__':
    app.run(debug=True)
