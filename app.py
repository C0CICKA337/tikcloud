import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Адрес нашего личного прокси на Fly.io
FLY_PROXY_URL = "https://tikcloud-proxy.fly.dev/parse"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/youtube-info', methods=['POST'])
def youtube_info():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL не указан'}), 400

    try:
        # Перенаправляем запрос на наш чистый микросервис Fly.io
        resp = requests.post(FLY_PROXY_URL, json={'url': url}, timeout=20)
        
        if resp.status_code != 200:
            return jsonify({'error': 'Ошибка от прокси-сервера'}), 400
            
        res_data = resp.json()
        
        video_data = {
            'title': res_data.get('title', 'Видео без названия'),
            'duration': res_data.get('duration', 0),
            'thumbnail': res_data.get('thumbnail', ''),
            'direct_url': res_data.get('direct_url'),
            'formats': [
                {
                    'format_id': 'best',
                    'resolution': 'HD / Best',
                    'ext': res_data.get('ext', 'mp4'),
                    'filesize': 0
                }
            ]
        }
                    
        return jsonify(video_data)
            
    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}")
        return jsonify({'error': 'Не удалось связаться с прокси'}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)