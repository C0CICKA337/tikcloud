import os
import traceback
import yt_dlp
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder='.')


@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(path):
        return send_from_directory('.', path)
    return send_from_directory('.', 'index.html')


@app.route('/api/youtube-info', methods=['POST'])
def get_youtube_info():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'status': 'error', 'message': 'URL not provided'}), 400

    url = data['url']

    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                'status': 'success',
                'title': info.get('title'),
                'url': info.get('url'),
            })
    except Exception as e:
        err_msg = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        print(err_msg)  # выведет в логи Render
        return jsonify({'status': 'error', 'message': str(e)}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)