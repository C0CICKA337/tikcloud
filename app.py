import os
import random
from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp

app = Flask(__name__)

# Папка для временного скачивания файлов
TEMP_DIR = 'temp_downloads'
os.makedirs(TEMP_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

# API для получения информации о видео с форматами
@app.route('/api/youtube-info', methods=['POST'])
def youtube_info():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'Ссылка не указана'}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            formats = []
            seen_heights = set()
            
            for f in info.get('formats', []):
                # Собираем только те форматы, где есть и видео, и звук сразу, либо доступные разрешения
                if f.get('vcodec') != 'none' and f.get('height'):
                    height = f['height']
                    if height not in seen_heights and height >= 144:
                        seen_heights.add(height)
                        formats.append({
                            'format_id': f['format_id'],
                            'height': height,
                            'ext': f.get('ext', 'mp4')
                        })
            
            formats = sorted(formats, key=lambda x: x['height'], reverse=True)

            return jsonify({
                'title': info.get('title', 'YouTube Video'),
                'thumbnail': info.get('thumbnail', ''),
                'formats': formats
            })
    except Exception as e:
        return jsonify({'error': 'Не удалось получить данные с YouTube'}), 400

# API для скачивания с учетом выбранного качества и правильным кодеком MP4
@app.route('/api/download-youtube', methods=['GET'])
def download_youtube():
    url = request.args.get('url')
    download_type = request.args.get('type', 'video')
    format_id = request.args.get('format_id') # Ловим выбранное качество с фронтенда
    
    random_id = random.randint(1000, 9999)
    
    if download_type == 'audio':
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(TEMP_DIR, f'clip_TikCloud_{random_id}.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        filename = f'clip_TikCloud_{random_id}.mp3'
    else:
        # Если пользователь выбрал конкретное качество — качаем его + лучший звук, иначе берем best
        chosen_format = f'{format_id}+ba/b' if format_id else 'bv*+ba/b'
        
        ydl_opts = {
            'format': chosen_format,
            'merge_output_format': 'mp4',
            # Жестко конвертируем в универсальный H.264 + AAC, чтобы Виндовс открывала без кодеков
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            'outtmpl': os.path.join(TEMP_DIR, f'clip_TikCloud_{random_id}.%(ext)s'),
        }
        filename = f'clip_TikCloud_{random_id}.mp4'

    file_path = None
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
            
            for f in os.listdir(TEMP_DIR):
                if str(random_id) in f:
                    file_path = os.path.join(TEMP_DIR, f)
                    ext = os.path.splitext(f)[1]
                    filename = f'clip_TikCloud_{random_id}{ext}'
                    break

        if not file_path or not os.path.exists(file_path):
            return "Файл не найден после скачивания", 500

        return send_file(file_path, as_attachment=True, download_name=filename)
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)