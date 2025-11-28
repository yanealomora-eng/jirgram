#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Конфигурационный файл для jirgram
Скопируйте этот файл в config.py и заполните своими данными
"""

import os
from pathlib import Path

# ======================
# TELEGRAM API НАСТРОЙКИ
# ======================
# Получите API ID и API Hash на https://my.telegram.org
API_ID = 0  # Замените на ваш API ID
API_HASH = ""  # Замените на ваш API Hash

# Номер телефона в международном формате (например: "+79991234567")
PHONE_NUMBER = "+0000000000"

# ======================
# НАСТРОЙКИ БЕЗОПАСНОСТИ
# ======================
# Ключ шифрования для локальной базы данных TDLib
# Используйте надёжный пароль
DATABASE_ENCRYPTION_KEY = "change_this_to_secure_password_123"

# ======================
# ПУТИ И ФАЙЛЫ
# ======================
# Директория для хранения файлов TDLib
FILES_DIRECTORY = Path("tdlib_files")

# База данных для хранения удалённых/отредактированных сообщений
MESSAGE_DATABASE = Path("messages_backup.db")

# Логи
LOG_FILE = Path("jirgram.log")
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# ======================
# ФУНКЦИИ КЛИЕНТА
# ======================
# Ghost Mode - скрывает онлайн статус и прочтение сообщений
GHOST_MODE_ENABLED = False

# Anti-Delete - сохраняет удалённые сообщения
ANTI_DELETE_ENABLED = True

# Save Edit History - сохраняет историю редактирования
SAVE_EDIT_HISTORY = True

# Auto-save media - автоматически сохранять медиа из важных чатов
AUTO_SAVE_MEDIA = False

# Список ID чатов для авто-сохранения медиа (если AUTO_SAVE_MEDIA = True)
AUTO_SAVE_CHAT_IDS = []

# ======================
# ДОПОЛНИТЕЛЬНО
# ======================
# Использовать прокси (необязательно)
USE_PROXY = False
PROXY_TYPE = "socks5"  # http, socks5
PROXY_SERVER = "127.0.0.1"
PROXY_PORT = 1080
PROXY_USERNAME = ""
PROXY_PASSWORD = ""

# Создание необходимых директорий
FILES_DIRECTORY.mkdir(exist_ok=True)
