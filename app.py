import os
import requests
from flask import Flask, render_template, request, send_file, jsonify

app = Flask(__name__)

DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Создаем сессию для сохранения кук и стабильного соединения
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://tikwm.com/'
})

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
        api_url = f"https://tikwm.com/api/?url={url}&hd=1"
        response = session.get(api_url, timeout=10)
        
        if response.status_code != 200:
            return jsonify({'error': f'Ошибка API: статус {response.status_code}'}), 400

        res_data = response.json()

        if res_data.get('code') == 0:
            info = res_data.get('data', {})
            return jsonify({
                'title': info.get('title', 'Видео TikTok'),
                'thumbnail': info.get('cover', ''),
                'duration': info.get('duration', 0)
            })
        else:
            return jsonify({'error': 'Не удалось найти видео. Проверьте правильность ссылки.'}), 400

    except Exception as e:
        print(f"Error in get_info: {e}")
        return jsonify({'error': 'Превышено время ожидания ответа от сервера TikTok. Попробуйте еще раз.'}), 500

@app.route('/download', methods=['POST'])
def download():
    data = request.json or {}
    url = data.get('url')
    download_type = data.get('type', 'video')

    if not url:
        return jsonify({'error': 'Не указана ссылка'}), 400

    try:
        api_url = f"https://tikwm.com/api/?url={url}&hd=1"
        response = session.get(api_url, timeout=10)
        res_data = response.json()

        if res_data.get('code') == 0:
            info = res_data.get('data', {})
            media_link = info.get('music') if download_type == 'audio' else info.get('play')

            if media_link:
                file_res = session.get(media_link, stream=True, timeout=20)
                ext = 'mp3' if download_type == 'audio' else 'mp4'
                temp_filename = os.path.join(DOWNLOAD_FOLDER, f"temp_{os.getpid()}.{ext}")
                
                with open(temp_filename, 'wb') as f:
                    for chunk in file_res.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                return send_file(temp_filename, as_attachment=True, download_name=f"tiktok.{ext}")

        return jsonify({'error': 'Ссылка на файл не найдена'}), 400

    except Exception as e:
        print(f"Error in download: {e}")
        return jsonify({'error': 'Ошибка при скачивании файла'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)