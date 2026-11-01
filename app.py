import os
from flask import Flask, render_template, request, jsonify
import yt_dlp

app = Flask(__name__)

# Автоматически создаем cookies.txt из переменной окружения на сервере Render
cookies_content = os.environ.get("YOUTUBE_COOKIES")
if cookies_content:
    with open("cookies.txt", "w", encoding="utf-8") as f:
        f.write(cookies_content)

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

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'geo_bypass': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    if os.path.exists('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Используем safe extract с подавлением строгой проверки форматов
            info = ydl.extract_info(url, download=False)
            
            video_data = {
                'title': info.get('title', 'Видео без названия'),
                'duration': info.get('duration', 0),
                'thumbnail': info.get('thumbnail', ''),
                'formats': [
                    {
                        'format_id': 'best',
                        'resolution': 'HD / Best',
                        'ext': 'mp4',
                        'filesize': 0
                    }
                ]
            }
                    
            return jsonify(video_data)
            
    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}")
        return jsonify({'error': 'Не удалось получить данные с YouTube'}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)