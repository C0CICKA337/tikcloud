import os
import re
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
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        html = response.text

        video_match = re.search(r'"contentUrl"\s*:\s*"([^"]+\.mp4)"', html)
        if not video_match:
            video_match = re.search(r'(https://v\.pinimg\.com/[^"]+\.mp4)', html)

        if not video_match:
            return jsonify({'code': 1, 'msg': 'Видео не найдено. Убедитесь, что это пин с видео.'})

        video_url = video_match.group(1).replace('\\/', '/')

        cover_match = re.search(r'"thumbnailUrl"\s*:\s*"([^"]+\.jpg)"', html)
        cover_url = cover_match.group(1).replace('\\/', '/') if cover_match else ""

        title_match = re.search(r'<title>(.*?)</title>', html)
        title = title_match.group(1).replace(' | Pinterest', '') if title_match else "Pinterest Video"

        return jsonify({
            'code': 0,
            'data': {
                'title': title,
                'cover': cover_url,
                'video': video_url
            }
        })

    except Exception as e:
        return jsonify({'code': 1, 'msg': 'Ошибка при обработке ссылки'})

# НОВЫЙ ЭНДПОИНТ ДЛЯ ПРИНУДИТЕЛЬНОГО СКАЧИВАНИЯ
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
        # Делаем потоковый запрос (stream=True), чтобы сервер не зависал на больших видео
        r = requests.get(url, stream=True, headers=headers)
        
        ext = 'mp3' if file_type == 'audio' else 'mp4'
        filename = f"TikCloud_media.{ext}"

        # Заголовок attachment заставляет браузер именно скачать файл, а не открыть вкладку
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