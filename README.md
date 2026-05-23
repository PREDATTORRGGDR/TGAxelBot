# TGAxelBot — Майк Вазовский 👁️

Телеграм бот-пугалка в образе Майка Вазовского. Пугает, проклинает и рассказывает паранормальные факты.

## Команды

- `/start` — начало, главное меню
- `/scare` — случайная страшная история (генерирует Gemini AI)
- `/curse` — случайное проклятие (генерирует Gemini AI)
- `/ghost` — паранормальный факт (генерирует Gemini AI)
- `/info` — информация о боте
- `/help` — список команд
- `/clean` — очистить сообщения бота

## Установка и запуск

1. Установи зависимости:
```bash
pip install -r requirements.txt
```

2. Создай `.env` и добавь токены:
```env
BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
```

3. Запусти:
```bash
python app.py
```

## Модели Gemini

Бот поочерёдно пробует следующие модели (fallback chain):

1. `gemini-2.5-flash`
2. `gemini-2.0-flash`
3. `gemini-2.5-flash-lite`
4. `gemini-2.0-flash-lite`

Если модель недоступна или возвращает ошибку — автоматически переключается на следующую.

## Устранение проблем

### Ошибка 429 (Rate Limit)

Бот автоматически обрабатывает ошибку 429 — повторяет запрос до 3 раз с экспоненциальной задержкой (2с → 4с → 8с). Если лимит исчерпан полностью, переключается на следующую модель.

### Обрезанные ответы (MAX_TOKENS)

Бот проверяет `finishReason` в ответе API. Если ответ обрезан (`MAX_TOKENS`), автоматически повторяет запрос с увеличенным лимитом токенов.

### Ошибка 409 Conflict

Если видишь ошибку `Conflict: terminated by other getUpdates request`:

```bash
python fix_bot_conflict.py
```

Это удалит webhook и очистит pending updates.

### Проверка статуса

```bash
python check_bot_status.py
```

Покажет статус бота, webhook и lock file.

### Множественные экземпляры

Бот автоматически создаёт `bot.lock` при запуске. Если видишь ошибку о запущенном экземпляре:

1. Проверь процессы: `tasklist | findstr python` (Windows)
2. Останови старый процесс
3. Или удали `bot.lock` если процесс не существует

## Changelog

### 2026-05-23

✅ Логирование в файл `bot.log`  
✅ Защита от множественных запусков (lock file)  
✅ Обработка ошибок и graceful shutdown  
✅ Улучшенная обработка конфликта 409  
✅ Скрипт проверки статуса  
✅ Retry с экспоненциальной задержкой при 429 (rate limit)  
✅ Проверка `finishReason` и автоматический retry при обрезке ответа  
✅ Увеличен `maxOutputTokens` (500 → 1024) для полных ответов  
✅ Добавлена модель `gemini-2.5-flash-lite` в цепочку fallback  
✅ Системный промпт: инструкция не обрывать текст на полуслове  

## Стек

- Python 3.10+
- pyTelegramBotAPI
- python-dotenv
- requests
- Gemini API (REST, v1beta)

## Автор

tg:[@kyrapyto](https://t.me/kyrapyto)  
Репозиторий: https://github.com/PREDATTORRGGDR/TGAxelBot
