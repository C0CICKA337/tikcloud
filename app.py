import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Актуальный эндпоинт Cobalt API v10
COBALT_API_URL = "https://api.cobalt.tools"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/youtube-info', methods=['POST'])
def youtube_info():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL не указан'}), 400

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": url,
        "videoQuality": "max"
    }

    try:
        response = requests.post(COBALT_API_URL, json=payload, headers=headers, timeout=15)
        res_data = response.json()

        if response.status_code != 200 or res_data.get("status") in ["error", "rate-limited"]:
            error_msg = res_data.get("text", "Ошибка при обработке ссылки через Cobalt")
            return jsonify({'error': error_msg}), 400

        direct_url = res_data.get("url") or res_data.get("picker", [{}])[0].get("url")

        if not direct_url:
            return jsonify({'error': 'Не удалось получить прямую ссылку на медиа'}), 400

        video_data = {
            'title': res_data.get('filename', 'Медиа файл'),
            'duration': 0,
            'thumbnail': '',
            'direct_url': direct_url,
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
        return jsonify({'error': 'Ошибка соединения с API загрузчика'}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)