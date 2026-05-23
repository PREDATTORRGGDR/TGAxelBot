#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для проверки статуса Telegram бота.
Показывает информацию о webhook, pending updates и состоянии бота.
"""
import urllib.request
import json
import sys
import os
from pathlib import Path

# Исправление кодировки для Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def load_token():
    """Загружает токен из .env файла"""
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('BOT_TOKEN='):
                    return line.split('=', 1)[1].strip().strip('"\'')
    return None

TOKEN = load_token()

def check_status():
    """Проверяет статус бота"""
    if not TOKEN:
        print("❌ Не удалось найти BOT_TOKEN в .env файле")
        return False

    base_url = f"https://api.telegram.org/bot{TOKEN}"

    try:
        print("📊 Проверка статуса бота...\n")

        print("1️⃣ Информация о боте:")
        with urllib.request.urlopen(f"{base_url}/getMe", timeout=10) as response:
            result = json.loads(response.read().decode())
            if result.get('ok'):
                bot = result['result']
                print(f"   ✅ ID: {bot['id']}")
                print(f"   ✅ Имя: {bot['first_name']}")
                print(f"   ✅ Username: @{bot['username']}")
            else:
                print(f"   ❌ Ошибка: {result}")
                return False

        print("\n2️⃣ Статус webhook:")
        with urllib.request.urlopen(f"{base_url}/getWebhookInfo", timeout=10) as response:
            result = json.loads(response.read().decode())
            if result.get('ok'):
                info = result['result']
                if info.get('url'):
                    print(f"   ⚠️  Webhook активен: {info['url']}")
                    print(f"   ⚠️  Pending updates: {info.get('pending_update_count', 0)}")
                    print("\n   💡 Для polling нужно удалить webhook:")
                    print("      python fix_bot_conflict.py")
                else:
                    print("   ✅ Webhook не установлен (polling доступен)")
                    pending = info.get('pending_update_count', 0)
                    if pending > 0:
                        print(f"   ⚠️  Pending updates: {pending}")
            else:
                print(f"   ❌ Ошибка: {result}")

        print("\n3️⃣ Проверка lock file:")
        lock_file = Path(__file__).parent / 'bot.lock'
        if lock_file.exists():
            with open(lock_file, 'r') as f:
                pid = f.read().strip()
            print(f"   ⚠️  Lock file существует (PID: {pid})")
            try:
                os.kill(int(pid), 0)
                print(f"   ⚠️  Процесс {pid} запущен")
            except (OSError, ValueError):
                print(f"   ⚠️  Процесс {pid} не найден (устаревший lock)")
        else:
            print("   ✅ Lock file отсутствует")

        print("\n✅ Проверка завершена")
        return True

    except urllib.error.URLError as e:
        print(f"❌ Ошибка сети: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

if __name__ == "__main__":
    success = check_status()
    sys.exit(0 if success else 1)
