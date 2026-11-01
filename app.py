import os
from flask import Flask, render_template, request, send_from_directory

# Указываем Flask, что шаблоны лежат в папке templates
app = Flask(__name__, template_folder='templates', static_folder='static')


@app.route('/')
def serve_index():
    return render_template('index.html')


@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(path):
        return send_from_directory('.', path)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)