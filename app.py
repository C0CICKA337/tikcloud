import os
import requests
from flask import Flask, render_template, request, send_from_directory, jsonify, Response, stream_with_context

app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/api/pinterest')
def get_pinterest_video():
    url = request.args.get('url')
    if not url:
        return jsonify({'code': 1, 'msg': 'URL не указан'})

    try:
        # Обращаемся к мощному стороннему API (Cobalt) для обхода блокировок Pinterest
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Настройки для Cobalt API
        payload = {
            "url": url,
            "vCodec": "h264",
            "isNoAudio": False
        }
        
        # Делаем POST-запрос к API
        response = requests.post('https://api.cobalt.tools/api/json', json=payload, headers=headers, timeout=15)
        data = response.json()

        # Если API вернул ошибку
        if data.get('status') == 'error' or not data.get('url'):
            return jsonify({'code': 1, 'msg': 'Видео не найдено или пин приватный.'})

        video_url = data.get('url')

        return jsonify({
            'code': 0,
            'data': {
                'title': 'Видео Pinterest',
                'cover': '', # Сторонний API отдает сразу видео без превью
                'video': video_url
            }
        })

    except Exception as e:
        return jsonify({'code': 1, 'msg': 'Сервис временно недоступен. Попробуйте позже.'})

@app.route('/download')
def download_media():
    url = request.args.get('url')
    file_type = request.args.get('type', 'video')
    
    if not url:
        return "URL не указан", 400

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        r = requests.get(url, stream=True, headers=headers)
        
        ext = 'mp3' if file_type == 'audio' else 'mp4'
        filename = f"TikCloud_media.{ext}"

        return Response(
            stream_with_context(r.iter_content(chunk_size=8192)),
            content_type=r.headers.get('Content-Type', f'video/{ext}'),
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        return f"Ошибка скачивания: {str(e)}", 500

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(path):
        return send_from_directory('.', path)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)