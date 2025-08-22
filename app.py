# app.py (FINAL DEBUG VERSION)

import os
import json
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__, static_folder='static', static_url_path='')

JSON_COOKIES = os.environ.get("INSTA_COOKIES")
netscape_cookie_string = None

def convert_cookies_to_netscape(json_string):
    """Browser cookie JSON ko yt-dlp ke format me convert karega (Improved)."""
    try:
        cookies = json.loads(json_string)
        lines = ["# Netscape HTTP Cookie File"]
        for cookie in cookies:
            # Zaroori fields check karenge
            if 'domain' not in cookie or 'name' not in cookie or 'value' not in cookie:
                continue

            domain = cookie.get('domain', '')
            # Agar domain . se shuru hota hai, toh subdomains ke liye hai
            includes_subdomains = 'TRUE' if domain.startswith('.') else 'FALSE'
            path = cookie.get('path', '/')
            secure = str(cookie.get('secure', False)).upper()
            # Expiration date ko integer me convert karenge
            expires = str(int(cookie.get('expirationDate', 0)))
            name = cookie.get('name', '')
            value = str(cookie.get('value', ''))
            
            # Netscape format: domain<TAB>includes_subdomains<TAB>path<TAB>secure<TAB>expires<TAB>name<TAB>value
            line = f"{domain}\t{includes_subdomains}\t{path}\t{secure}\t{expires}\t{name}\t{value}"
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

    is_story_request = not url.startswith('http') and ' ' not in url
    if is_story_request:
        url = f"https://www.instagram.com/stories/{url}/"

    try:
        ydl_opts = {
            'quiet': True,
            'format': 'best',
            'cookiefile_string': netscape_cookie_string
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if 'entries' in info and info['entries']:
                info = info['entries'][0]

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
        # DEBUG: Hum logs me check karenge ki format sahi hai ya nahi
        print("--- Generated Netscape Cookies (for debugging) ---")
        print(netscape_cookie_string)
        print("-------------------------------------------------")
    else:
        print("ERROR: Browser cookies convert nahi ho paayi.")
else:
    print("ERROR: INSTA_COOKIES environment variable nahi mila.")

if __name__ == '__main__':
    app.run(debug=True)
