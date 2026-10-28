import os
import requests
from flask import Flask, render_template, request, send_file, jsonify

app = Flask(__name__)

DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

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
    except Exception as e:
        print(f"Error in get_info: {e}")

    return jsonify({
        'title': 'Видео TikTok',
        'thumbnail': '',
        'duration': 0
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
        response = requests.get(api_url, timeout=15)
        res_data = response.json()

        if res_data.get('code') == 0:
            info = res_data.get('data', {})
            media_link = info.get('music') if download_type == 'audio' else info.get('play')

            if media_link:
                file_res = requests.get(media_link, stream=True, timeout=20)
                ext = 'mp3' if download_type == 'audio' else 'mp4'
                temp_filename = os.path.join(DOWNLOAD_FOLDER, f"temp_{os.getpid()}.{ext}")
                
                with open(temp_filename, 'wb') as f:
                    for chunk in file_res.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                return send_file(temp_filename, as_attachment=True, download_name=f"tiktok.{ext}")

        return jsonify({'error': 'Не удалось получить ссылку на файл от API'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)