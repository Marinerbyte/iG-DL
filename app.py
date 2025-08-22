import os
import io
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp
import instaloader

# Render par session file save karne ke liye ek fixed path
SESSION_DIR = "/etc/secrets"
if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)

app = Flask(__name__, static_folder='static', static_url_path='')

L = instaloader.Instaloader(
    download_pictures=False, download_videos=False, download_video_thumbnails=False,
    download_geotags=False, download_comments=False, save_metadata=False,
    compress_json=False
)

INSTA_USERNAME = os.environ.get("INSTA_USERNAME")
INSTA_PASSWORD = os.environ.get("INSTA_PASSWORD")

cookie_jar_string = None

def instagram_login():
    global cookie_jar_string
    if not INSTA_USERNAME or not INSTA_PASSWORD:
        print("ERROR: INSTA_USERNAME aur INSTA_PASSWORD set nahi hai.")
        return False

    session_filename = os.path.join(SESSION_DIR, L.format_session_filename(INSTA_USERNAME))

    try:
        print(f"Pehle se saved session '{session_filename}' se login karne ki koshish...")
        L.load_session_from_file(INSTA_USERNAME, session_filename)
        print("Session se login successful!")
    except FileNotFoundError:
        try:
            print("Session file nahi mili. Naya login kar raha hai...")
            L.login(INSTA_USERNAME, INSTA_PASSWORD)
            L.save_session_to_file(session_filename)
            print("Naya login successful. Session save ho gaya.")
        except Exception as e:
            print(f"Bhai, login me error aa gaya: {e}")
            return False

    if os.path.exists(session_filename):
        with open(session_filename, 'r') as f:
            cookie_jar_string = f.read()
            print("Cookies ko memory mein load kar liya hai. Ab sab set hai.")
        return True
    return False

# --- API Routes ---
@app.route('/')
def home():
    return send_from_directory('static', 'index.html')

@app.route('/api/get_link', methods=['POST'])
def get_download_link():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL toh de de bhai'}), 400

    if not cookie_jar_string:
         return jsonify({'error': 'Instagram login nahi hua. Server logs check kar.'}), 500
    
    # Check if it's a username for stories or a URL
    is_story_request = not url.startswith('http') and ' ' not in url

    try:
        if is_story_request:
            # Story download logic
            username = url
            print(f"Fetching stories for username: {username}")
            try:
                profile = instaloader.Profile.from_username(L.context, username)
                story_items = L.get_stories(userids=[profile.userid])
                
                # We will just get the first available story's link for simplicity
                for story in story_items:
                    for item in story.get_items():
                        return jsonify({
                            'success': True,
                            'download_url': item.video_url if item.is_video else item.url,
                            'filename': f"{username}_story.mp4" if item.is_video else f"{username}_story.jpg"
                        })
                return jsonify({'error': f'No recent stories found for {username}'}), 404
            except Exception as e:
                print(f"Story download me error: {e}")
                return jsonify({'error': f"Could not fetch stories for '{username}'"}), 500
        else:
            # Reel/Photo download logic
            ydl_opts = {
                'quiet': True,
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'cookiefile_string': cookie_jar_string
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                download_url = info.get('url')
                title = info.get('title', 'media_file').replace(" ", "_")
                ext = 'mp4' if info.get('is_video') else 'jpg'

                return jsonify({
                    'success': True,
                    'download_url': download_url,
                    'filename': f"{title}.{ext}"
                })
    except Exception as e:
        print(f"Download me error: {e}")
        return jsonify({'error': f'URL process nahi kar paaye: Invalid URL or private content.'}), 500

# --- Server Start ---
if __name__ == '__main__':
    instagram_login()
