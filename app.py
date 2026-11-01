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

    # Настройки yt-dlp с прокси и эмуляцией Android-клиента для обхода бота
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'geo_bypass': True,
        'proxy': 'socks5://45.74.31.41:10054',
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web']
            }
        },
        'user_agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
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
        return jsonify({'error': 'Не удалось получить данные через прокси'}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)