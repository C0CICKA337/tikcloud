import os
from flask import Flask, render_template, request, jsonify
import yt_dlp

app = Flask(__name__)

DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/youtube-info', methods=['POST'])
def youtube_info():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL не указан'}), 400

    # Ультра-простые и чистые настройки, как для TikTok
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Универсальный захват прямой ссылки на медиапоток
            direct_url = info.get('url')
            if not direct_url and 'entries' in info:
                direct_url = info['entries'][0].get('url')

            video_data = {
                'title': info.get('title', 'Видео без названия'),
                'duration': info.get('duration', 0),
                'thumbnail': info.get('thumbnail', ''),
                'direct_url': direct_url,
                'formats': [
                    {
                        'format_id': 'best',
                        'resolution': 'Best Quality',
                        'ext': info.get('ext', 'mp4'),
                        'filesize': info.get('filesize') or info.get('filesize_approx') or 0
                    }
                ]
            }
                    
            return jsonify(video_data)
            
    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}")
        return jsonify({'error': 'Не удалось получить данные с сервера'}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)