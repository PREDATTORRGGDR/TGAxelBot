#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест Gemini API через прямые HTTP запросы
"""
import os
import sys
import requests
from dotenv import load_dotenv

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY не найден в .env")
    exit(1)

print("🔍 Тестирование Gemini API через REST...\n")

# Список моделей для проверки
models = [
    'gemini-1.5-flash',
    'gemini-1.5-pro',
    'gemini-pro',
]

for model in models:
    print(f"Тестирую {model}...", end=" ")

    url = f"https://generativelanguage.googleapis.com/v1/models/{model}:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [{
            "parts": [{
                "text": "Скажи 'работает' одним словом"
            }]
        }]
    }

    try:
        response = requests.post(url, json=payload, timeout=10)

        if response.status_code == 200:
            result = response.json()
            text = result['candidates'][0]['content']['parts'][0]['text']
            print(f"✅ Работает! Ответ: {text.strip()}")
        elif response.status_code == 404:
            print(f"❌ Не найдена")
        else:
            print(f"❌ Ошибка {response.status_code}: {response.text[:100]}")
    except Exception as e:
        print(f"❌ Исключение: {e}")

print("\n" + "="*50)
print("💡 Если все модели не работают, проверьте:")
print("  1. API ключ активен в https://aistudio.google.com/apikey")
print("  2. Включён ли Gemini API в вашем проекте")
print("  3. Доступ из вашего региона")
