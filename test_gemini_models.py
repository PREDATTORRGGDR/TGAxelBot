#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для проверки доступных моделей Gemini API
"""
import os
import sys
from dotenv import load_dotenv
from google import genai

#кодировки для Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY не найден в .env")
    exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)

print("🔍 Проверка доступных моделей Gemini...\n")

# Список моделей для проверки
models_to_test = [
    'gemini-1.5-flash-latest',
    'gemini-1.5-flash',
    'gemini-1.5-pro',
    'gemini-1.5-pro-latest',
    'gemini-pro',
    'gemini-flash',
]

working_models = []

for model_name in models_to_test:
    try:
        print(f"Тестирую {model_name}...", end=" ")
        response = client.models.generate_content(
            model=model_name,
            contents="Скажи 'работает' одним словом"
        )
        print(f"✅ Работает! Ответ: {response.text.strip()}")
        working_models.append(model_name)
    except Exception as e:
        error_str = str(e)
        if "404" in error_str or "NOT_FOUND" in error_str:
            print(f"❌ Не найдена")
        elif "429" in error_str:
            print(f"⚠️  Лимит исчерпан")
        else:
            print(f"❌ Ошибка: {e}")

print(f"\n{'='*50}")
if working_models:
    print(f"✅ Рабочие модели ({len(working_models)}):")
    for model in working_models:
        print(f"   - {model}")
    print(f"\n💡 Рекомендуется использовать: {working_models[0]}")
else:
    print("❌ Ни одна модель не работает!")
    print("Проверьте:")
    print("  1. Правильность GEMINI_API_KEY")
    print("  2. Активирован ли API в Google AI Studio")
    print("  3. Есть ли доступ к моделям в вашем регионе")
