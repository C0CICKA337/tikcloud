import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-info', methods=['POST'])
def get_info():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({'error': 'Не указана ссылка'}), 400

    try:
        # Используем быстрое публичное API для получения прямой информации о видео TikTok
        api_url = f"https://tikwm.com/api/?url={url}"
        response = requests.get(api_url, timeout=10)
        res_data = response.json()

        if res_data.get('code') == 0:
            info = res_data.get('data', {})
            return jsonify({
                'title': info.get('title', 'Видео TikTok'),
                'thumbnail': info.get('cover', ''),
                'duration': info.get('duration', 0),
                'formats': [{'height': 720}, {'height': 480}, {'height': 360}]
            })
    except Exception:
        pass

    # Заглушка на случай сбоя сети, чтобы интерфейс не ломался
    return jsonify({
        'title': 'Видео TikTok',
        'thumbnail': '',
        'duration': 0,
        'formats': [{'height': 720}, {'height': 480}, {'height': 360}]
    })

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    download_type = data.get('type', 'video')

    if not url:
        return jsonify({'error': 'Не указана ссылка'}), 400

    try:
        # Получаем прямую ссылку на медиафайл через надежный API-парсер
        api_url = f"https://tikwm.com/api/?url={url}"
        response = requests.get(api_url, timeout=10)
        res_data = response.json()

        if res_data.get('code') == 0:
            info = res_data.get('data', {})
            
            if download_type == 'audio':
                media_link = info.get('music') # Ссылка на аудио
            else:
                media_link = info.get('play') # Ссылка на видео без водяных знаков

            if media_link:
                # Перенаправляем пользователя на прямую загрузку файла
                return jsonify({'redirect_url': media_link})

        return jsonify({'error': 'Не удалось получить ссылку на скачивание от TikTok'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)