import os
import requests
from flask import Flask, render_template, request, send_file, jsonify

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
                'duration': info.get('duration', 0),
                'formats': [
                    {'height': 'best', 'label': 'Лучшее качество (HD)'},
                    {'height': 'watermark', 'label': 'С водяным знаком'}
                ]
            })
    except Exception:
        pass

    # Безопасный фоллбек, чтобы интерфейс всегда открывал кнопки
    return jsonify({
        'title': 'Видео TikTok',
        'thumbnail': '',
        'duration': 0,
        'formats': [{'height': 'best', 'label': 'Лучшее качество'}]
    })

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
            
            if download_type == 'audio':
                media_link = info.get('music')
            else:
                media_link = info.get('play') # Ссылка на видео без водяного знака

            if media_link:
                # Скачиваем файл во временную памету и отдаем клиенту
                file_res = requests.get(media_link, stream=True, timeout=15)
                ext = 'mp3' if download_type == 'audio' else 'mp4'
                temp_filename = f"tiktok_download.{ext}"
                
                with open(temp_filename, 'wb') as f:
                    for chunk in file_res.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                response = send_file(temp_filename, as_attachment=True)
                return response

        return jsonify({'error': 'Не удалось получить файл от TikTok'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)