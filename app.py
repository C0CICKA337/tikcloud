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
        # Используем сессию, чтобы сохранять cookies при редиректах (важно для pin.it)
        session = requests.Session()
        
        # Расширенные заголовки, чтобы сервер выглядел как 100% реальный браузер
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        }
        
        response = session.get(url, headers=headers, timeout=15, allow_redirects=True)
        html = response.text

        # 1. Пробуем найти ссылку в JSON-данных страницы
        video_match = re.search(r'"contentUrl"\s*:\s*"([^"]+\.mp4)"', html)
        
        # 2. Ищем любые прямые ссылки на видео от пинтереста
        if not video_match:
            video_match = re.search(r'(https://[a-zA-Z0-9-]+\.pinimg\.com/[^"\']+\.mp4)', html)
            
        # 3. Ищем ссылки с экранированными слешами
        if not video_match:
            video_match = re.search(r'(https:\\/\\/[a-zA-Z0-9-]+\.pinimg\.com\\/[^"\']+\.mp4)', html)

        if not video_match:
            # Для отладки: если видео снова не найдется, сервер вернет часть HTML, чтобы понять, заблокировал ли нас Pinterest
            return jsonify({'code': 1, 'msg': 'Видео не найдено. Убедитесь, что это пин с видео.'})

        # Очищаем ссылку от экранирования, если оно было
        video_url = video_match.group(1).replace('\\/', '/')

        # Ищем обложку
        cover_match = re.search(r'"thumbnailUrl"\s*:\s*"([^"]+\.jpg)"', html)
        cover_url = cover_match.group(1).replace('\\/', '/') if cover_match else ""

        # Ищем заголовок
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
        return jsonify({'code': 1, 'msg': 'Ошибка при обработке ссылки. Сервер Pinterest не отвечает.'})