#!/usr/bin/env bash
set -o errexit

# Обновляем пакеты и ставим системный ffmpeg
apt-get update
apt-get install -y ffmpeg

# Устанавливаем python зависимости
pip install -r requirements.txt