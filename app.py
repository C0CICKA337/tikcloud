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
        
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        if response.status_code != 200:
            return jsonify({'code': 1, 'msg': 'Не удалось загрузить страницу пина'})

        # Пинтерест прячет ссылки в JSON и экранирует слеши. Снимаем экранирование.
        html_text = response.text.replace('\\/', '/')
        
        # Ищем вообще все ссылки на .mp4
        mp4_links = re.findall(r'https://[^"\'\s]+\.mp4', html_text)
        
        video_url = None
        # Ищем среди найденных ту, что принадлежит Pinterest
        for link in mp4_links:
            if 'pinimg.com' in link:
                video_url = link
                # Если нашли в хорошем качестве — сразу берем её
                if '720p' in link or '1080p' in link:
                    break

        if not video_url:
            return jsonify({'code': 1, 'msg': 'Видео не найдено. Возможно, это картинка или приватный пин.'})

        return jsonify({
            'code': 0,
            'data': {
                'title': 'Видео Pinterest',
                'cover': '',
                'video': video_url
            }
        })

    except Exception as e:
        return jsonify({'code': 1, 'msg': f'Ошибка: {str(e)}'})

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