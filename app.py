import os
import subprocess
import zipfile
from flask import Flask, jsonify, render_template, request, send_file
from yt_dlp import YoutubeDL

app = Flask(__name__)
DOWNLOAD_FOLDER = "./downloads"

if not os.path.exists(DOWNLOAD_FOLDER):
  os.makedirs(DOWNLOAD_FOLDER)


@app.route("/")
def index():
  return render_template("index.html")


@app.route("/get-info", methods=["POST"])
def get_info():
  data = request.json
  url = data.get("url")

  if not url:
    return jsonify({"error": "Ссылка не указана"}), 400

  ydl_opts = {"format": "best"}

  try:
    with YoutubeDL(ydl_opts) as ydl:
      info = ydl.extract_info(url, download=False)
      video_data = {
          "title": info.get("title", "Контент из TikTok"),
          "author": info.get("uploader", "Автор"),
          "thumbnail": info.get("thumbnail"),
          "id": info.get("id"),
      }
      return jsonify({"success": True, "data": video_data})
  except Exception as e:
    return jsonify({"error": str(e)}), 500


@app.route("/download-content", methods=["POST"])
def download_content():
  data = request.json
  url = data.get("url")
  tab = data.get("tab", "video")  # 'video' или 'photo'
  mode = data.get("mode", "video")  # 'video' или 'audio'
  quality = data.get("quality", "1080")

  ydl_opts = {
      "outtmpl": os.path.join(DOWNLOAD_FOLDER, "%(id)s.%(ext)s"),
      "format": "best",
  }

  try:
    with YoutubeDL(ydl_opts) as ydl:
      info = ydl.extract_info(url, download=True)

      # Если выбрана вкладка фото или карусель
      if tab == "photo" or "entries" in info:
        photo_files = []
        if "entries" in info:
          for entry in info["entries"]:
            p_file = ydl.prepare_filename(entry)
            if os.path.exists(p_file):
              photo_files.append(p_file)
        else:
          p_file = ydl.prepare_filename(info)
          if os.path.exists(p_file):
            photo_files.append(p_file)

        zip_filename = os.path.join(DOWNLOAD_FOLDER, f"{info['id']}_photos.zip")
        with zipfile.ZipFile(zip_filename, "w") as zipf:
          for f in photo_files:
            zipf.write(f, os.path.basename(f))

        return jsonify(
            {"success": True, "filename": os.path.basename(zip_filename)}
        )

      # Если выбрана вкладка видео
      original_filename = ydl.prepare_filename(info)

      if mode == "audio":
        base, _ = os.path.splitext(original_filename)
        mp3_filename = base + ".mp3"
        cmd = [
            r"C:\ffmpeg\bin\ffmpeg.exe",
            "-y",
            "-i",
            original_filename,
            "-vn",
            "-ab",
            "192k",
            mp3_filename,
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return jsonify(
            {"success": True, "filename": os.path.basename(mp3_filename)}
        )
      else:
        if quality in ["720", "480", "360", "240", "144"]:
          base, ext = os.path.splitext(original_filename)
          output_filename = f"{base}_{quality}p{ext}"
          cmd = [
              r"C:\ffmpeg\bin\ffmpeg.exe",
              "-y",
              "-i",
              original_filename,
              "-vf",
              f"scale=-2:{quality}",
              "-c:v",
              "libx264",
              "-crf",
              "23",
              "-c:a",
              "copy",
              output_filename,
          ]
          subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
          return jsonify(
              {"success": True, "filename": os.path.basename(output_filename)}
          )

        return jsonify(
            {"success": True, "filename": os.path.basename(original_filename)}
        )

  except Exception as e:
    return jsonify({"error": str(e)}), 500


@app.route("/get-file/<filename>")
def get_file(filename):
  return send_file(
      os.path.join(DOWNLOAD_FOLDER, filename), as_attachment=True
  )


if __name__ == "__main__":
  app.run(debug=True, port=5000)