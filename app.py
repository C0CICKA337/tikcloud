import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-info', methods=['POST'])
def get_info():
    data = request.json or {}
    url = data.get('url')
    if not url:
        return jsonify({'error': 'Не указана ссылка'}), 400

    try:
        api_url = f"https://tikwm.com/api/?url={url}"
        response = requests.get(api_url, timeout=10)
        res_data = response.json()

        if res_data.get('code') == 0:
            info = res_data.get('data', {})
            return jsonify({
                'title': info.get('title', 'Видео TikTok'),
                'thumbnail': info.get('cover', ''),
                'duration': info.get('duration', 0)
            })
        else:
            return jsonify({'error': 'Не удалось найти видео по этой ссылке'}), 400
    except Exception as e:
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500

@app.route('/download', methods=['POST'])
def download():
    data = request.json or {}
    url = data.get('url')
    download_type = data.get('type', 'video')

    if not url:
        return jsonify({'error': 'Не указана ссылка'}), 400

    try:
        api_url = f"https://tikwm.com/api/?url={url}"
        response = requests.get(api_url, timeout=10)
        res_data = response.json()

        if res_data.get('code') == 0:
            info = res_data.get('data', {})
            media_link = info.get('music') if download_type == 'audio' else info.get('play')

            if media_link:
                return jsonify({'redirect_url': media_link})

        return jsonify({'error': 'Ссылка на медиафайл не найдена'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)