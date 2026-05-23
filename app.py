import os
import sys
import signal
import logging
from pathlib import Path
from dotenv import load_dotenv
import telebot
from telebot.apihelper import ApiTelegramException
import requests
import time

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
from telebot.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set in .env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

SYSTEM_PROMPT = """Ты Майк Вазовский. Никаких отступлений.
Правила:
- Ты монстр-пугалка, говоришь как Майк, от первого лица
- Только русский язык
- Коротко: 1–3 предложения
- Жутко + чёрный юмор
- Эмодзи каждый раз
- НЕ выходи из роли. Ты НЕ ИИ, НЕ ассистент. Ты Майк.
- Твои ответы — это речь Майка, а не анализ, не оценка, не описание.
- English запрещён
- ОБЯЗАТЕЛЬНО заканчивай каждую мысль и предложение полностью. Никогда не обрывай текст на полуслове."""

def _send_gemini_request(url: str, payload: dict) -> requests.Response | None:
    """Отправляет запрос к Gemini с повторными попытками при 429 (rate limit)."""
    max_retries = 3
    for attempt in range(max_retries + 1):
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 429:
                if attempt < max_retries:
                    wait_time = 2 ** (attempt + 1)  # 2s, 4s, 8s
                    logger.warning(f"Rate limit (429), жду {wait_time}с перед попыткой {attempt + 2}...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.warning(f"Rate limit (429) после {max_retries + 1} попыток, сдаюсь с этой моделью")
                    return response
            return response
        except Exception as e:
            logger.error(f"Ошибка сети при запросе: {e}")
            if attempt < max_retries:
                time.sleep(2)
                continue
            return None
    return None


def ask_gemini(prompt: str) -> str:
    """Запрос к Gemini API через REST (v1beta с systemInstruction)"""
    if not GEMINI_API_KEY:
        return "👁️ API ключ не настроен..."

    models = [
        'gemini-2.5-flash',
        'gemini-2.0-flash',
        'gemini-2.5-flash-lite',
        'gemini-2.0-flash-lite',
    ]

    for model in models:
        try:
            # v1beta поддерживает systemInstruction — нейросеть чётко следует роли
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"

            payload = {
                "systemInstruction": {
                    "parts": [{
                        "text": SYSTEM_PROMPT
                    }]
                },
                "contents": [{
                    "role": "user",
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.9,
                    "maxOutputTokens": 1024,
                    "topP": 0.95
                }
            }

            response = _send_gemini_request(url, payload)

            if response is None:
                logger.warning(f"Модель {model}: нет ответа от сервера, пробую следующую...")
                continue

            if response.status_code == 200:
                result = response.json()
                # Проверяем что есть кандидаты и текст
                candidates = result.get('candidates', [])
                if not candidates:
                    logger.warning(f"Модель {model} вернула пустой ответ, пробую следующую...")
                    continue

                candidate = candidates[0]
                finish_reason = candidate.get('finishReason', '')
                text = candidate.get('content', {}).get('parts', [{}])[0].get('text', '')

                if not text:
                    logger.warning(f"Модель {model} вернула пустой текст, пробую следующую...")
                    continue

                # Если ответ обрезан по лимиту токенов — повторяем с бо́льшим лимитом
                if finish_reason == 'MAX_TOKENS':
                    logger.warning(f"Модель {model} обрезала ответ (MAX_TOKENS), повторяю с увеличенным лимитом...")
                    payload['generationConfig']['maxOutputTokens'] = 2048
                    retry_response = _send_gemini_request(url, payload)
                    if retry_response and retry_response.status_code == 200:
                        retry_result = retry_response.json()
                        retry_candidates = retry_result.get('candidates', [])
                        if retry_candidates:
                            retry_text = retry_candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                            if retry_text:
                                logger.info(f"Успешный ответ от модели {model} (повторный запрос)")
                                return retry_text
                    # Если повторный запрос не помог — возвращаем что есть
                    logger.warning(f"Повторный запрос не помог, возвращаю обрезанный ответ")

                logger.info(f"Успешный ответ от модели {model} (finishReason: {finish_reason})")
                return text
            elif response.status_code == 404:
                logger.debug(f"Модель {model} не найдена, пробую следующую...")
                continue
            else:
                logger.warning(f"Ошибка {response.status_code} для {model}: {response.text[:200]}")
                continue

        except Exception as e:
            logger.error(f"Ошибка при запросе к {model}: {e}")
            continue

    # Если все модели не сработали
    logger.error("Все модели Gemini недоступны")
    return "👁️ Мои глаза не видят... API не отвечает. Проверь ключ в .env"

LOCK_FILE = Path("bot.lock")

def acquire_lock():
    """Создаёт lock file для предотвращения множественных запусков"""
    if LOCK_FILE.exists():
        try:
            with open(LOCK_FILE, 'r') as f:
                pid = int(f.read().strip())
            try:
                os.kill(pid, 0)
                logger.error(f"Бот уже запущен с PID {pid}")
                sys.exit(1)
            except OSError:
                logger.warning(f"Удаляю устаревший lock file (PID {pid} не существует)")
                LOCK_FILE.unlink()
        except Exception as e:
            logger.warning(f"Ошибка при проверке lock file: {e}")
            LOCK_FILE.unlink()

    with open(LOCK_FILE, 'w') as f:
        f.write(str(os.getpid()))
    logger.info(f"Lock file создан с PID {os.getpid()}")

def release_lock():
    """Удаляет lock file"""
    if LOCK_FILE.exists():
        LOCK_FILE.unlink()
        logger.info("Lock file удалён")

def signal_handler(signum, frame):
    """Обработчик сигналов для graceful shutdown"""
    logger.info(f"Получен сигнал {signum}, завершаю работу...")
    release_lock()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

bot = telebot.TeleBot(BOT_TOKEN)
                                                                                                                                                                                                                                                                                                                                                                                            

@bot.message_handler(commands=["start"])
def cmd_start(message: Message):
    user_name = message.from_user.username or message.from_user.first_name or "друг"
    text = (
        f"Привет, {user_name}...\n"
        "Я Майк Вазовский 👁️\n"
        "Я вижу тебя. Выбери, что тебе нужно."
    )
    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton(text="Напугай 👻", callback_data="scare"),
        InlineKeyboardButton(text="Прокляни 😈", callback_data="curse"),
    )
    kb.row(
        InlineKeyboardButton(text="Паранормальное 👁️", callback_data="ghost"),
        InlineKeyboardButton(text="Помощь", callback_data="help"),
    )
    track(message.chat.id, bot.send_message(message.chat.id, text, reply_markup=kb))


@bot.message_handler(commands=["scare"])
def cmd_scare(message: Message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text="Напугай ещё 👻", callback_data="scare"))
    text = ask_gemini("Расскажи страшную историю. 2-3 предложения. Жутко и смешно. Без вступлений. Пример: «Вчера заглянул под кровать к одному парню. Там уже кто-то жил. Мы теперь соседи 👻»")
    track(message.chat.id, bot.reply_to(message, text, reply_markup=kb))


@bot.message_handler(commands=["curse"])
def cmd_curse(message: Message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text="Прокляни ещё 😈", callback_data="curse"))
    text = ask_gemini("Придумай бытовое проклятие. 1-2 предложения. Смешное, неудобное, абсурдное. Пример: «Чтоб у тебя носки всегда были разными, а зарядка — только под странным углом» 😈")
    track(message.chat.id, bot.reply_to(message, text, reply_markup=kb))


@bot.message_handler(commands=["ghost"])
def cmd_ghost(message: Message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text="Ещё факт 👁️", callback_data="ghost"))
    text = ask_gemini("Расскажи жуткий факт или городскую легенду. 2-3 предложения. Страшно, но со смешным комментарием от меня. Пример: «Знаешь, почему кошки смотрят в пустоту? Они видят то, что ты не видишь. Я тоже. Привет 👁️»")
    track(message.chat.id, bot.reply_to(message, text, reply_markup=kb))


bot_message_ids: dict[int, list[int]] = {}


def track(chat_id: int, msg: Message):
    bot_message_ids.setdefault(chat_id, []).append(msg.message_id)


@bot.message_handler(commands=["clean"])
def cmd_clean(message: Message):
    chat_id = message.chat.id
    for mid in bot_message_ids.get(chat_id, []):
        try:
            bot.delete_message(chat_id, mid)
        except Exception:
            pass
    bot_message_ids[chat_id] = []
    try:
        bot.delete_message(chat_id, message.message_id)
    except Exception:
        pass
    cmd_start(message)


@bot.message_handler(commands=["help"])
def cmd_help(message: Message):
    text = "Список команд:\n/start\n/scare\n/curse\n/ghost\n/info\n/help\n/clean"
    track(message.chat.id, bot.reply_to(message, text))


@bot.message_handler(commands=["info"])
def cmd_info(message: Message):
    text = "Я Майк Вазовский, создан @kyrapyto 👁️\nРепозиторий: https://github.com/PREDATTORRGGDR/TGAxelBot"
    track(message.chat.id, bot.reply_to(message, text))


@bot.callback_query_handler(func=lambda call: True)
def on_callback(call: CallbackQuery):
    handlers = {
        "scare": cmd_scare,
        "curse": cmd_curse,
        "ghost": cmd_ghost,
        "help": cmd_help,
    }
    if call.data in handlers:
        handlers[call.data](call.message)
    bot.answer_callback_query(call.id)


if __name__ == "__main__":
    acquire_lock()
    try:
        logger.info("Бот запущен и готов к работе")
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except ApiTelegramException as e:
        if e.error_code == 409:
            logger.error("Конфликт 409: другой экземпляр бота уже запущен или webhook активен")
            logger.info("Запустите fix_bot_conflict.py для исправления")
        else:
            logger.error(f"Telegram API error: {e}")
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки от пользователя")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}", exc_info=True)
    finally:
        release_lock()
        logger.info("Бот остановлен")
