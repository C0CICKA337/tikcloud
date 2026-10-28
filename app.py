import os
import zipfile
from flask import Flask, render_template, request, send_file, jsonify
from yt_dlp import YoutubeDL

app = Flask(__name__)

# Папка для временного скачивания файлов
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
ddef index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    quality = data.get('quality', 'best') # Получаем качество (например, '360', '720' или 'best')
    download_type = data.get('type', 'video') # 'video', 'audio' или 'slides'

    if not url:
        return jsonify({'error': 'Не указана ссылка'}), 400

    try:
        # Базовые настройки для yt-dlp (без жестких путей к ffmpeg)
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(id)s.%(ext)s'),
        }

        # Настройка в зависимости от типа скачивания
        if download_type == 'audio':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        elif download_type == 'video':
            if quality == 'best':
                ydl_opts['format'] = 'bestvideo+bestaudio/best'
            else:
                # Выбираем конкретное разрешение по высоте (например, 360, 480, 720)
                ydl_opts['format'] = f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best'
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Если качали аудио, расширение изменится на mp3
            if download_type == 'audio':
                filename = os.path.splitext(filename)[0] + '.mp3'

        return send_file(filename, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)