import os
import pyautogui
import platform
import asyncio
from aiogram import Bot, Dispatcher, types, executor

# --- КОНФИГУРАЦИЯ ---
API_TOKEN = '8777973485:AAHg2x7ez-wCOMb1b9CEC-uaO4uKf4tVAxM'
ADMIN_ID = 7917303098  
# --------------------

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Проверка прав доступа
def is_admin(user_id):
    return user_id == ADMIN_ID

# Лог при старте
async def on_startup(_):
    print("====================================")
    print(f"🚀 Бот post.py ЗАПУЩЕН")
    print(f"👤 Админ ID: {ADMIN_ID}")
    print("====================================")
    try:
        await bot.send_message(ADMIN_ID, "✅ Бот post.py запущен и готов к командам!")
    except Exception as e:
        print(f"❌ Ошибка отправки стартового сообщения: {e}")

# Команда /start
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    if is_admin(message.from_user.id):
        await message.answer(
            "⚙️ **Система управления подключена**\n\n"
            "📸 /screen — Скриншот экрана\n"
            "ℹ️ /info — Данные системы\n"
            "💬 /msg <текст> — Окно на экране\n"
            "🔌 /off — Выключить ПК"
        )
    else:
        print(f"⚠️ Попытка доступа! ID: {message.from_user.id}")

# Команда /screen
@dp.message_handler(commands=['screen'])
async def make_screenshot(message: types.Message):
    if is_admin(message.from_user.id):
        print("🛠 LOG: Создаю скриншот...")
        try:
            filename = "temp_screen.png"
            # Делаем снимок
            img = pyautogui.screenshot()
            img.save(filename)
            print(f"🛠 LOG: Снимок сохранен как {filename}")
            
            # Отправляем файл
            with open(filename, "rb") as file:
                await bot.send_document(message.chat.id, file, caption="📸 Скриншот рабочего стола")
            
            # Чистим за собой
            os.remove(filename)
            print("🛠 LOG: Packet sent successfully.")
        except Exception as e:
            print(f"❌ ОШИБКА при скриншоте: {e}")
            await message.answer(f"Ошибка: {e}")

# Команда /info
@dp.message_handler(commands=['info'])
async def system_info(message: types.Message):
    if is_admin(message.from_user.id):
        data = (
            f"💻 Имя ПК: {platform.node()}\n"
            f"💽 ОС: {platform.system()} {platform.release()}\n"
            f"👤 Юзер: {os.getlogin()}"
        )
        await message.answer(data)

# Команда /msg
@dp.message_handler(commands=['msg'])
async def send_message_pc(message: types.Message):
    if is_admin(message.from_user.id):
        text = message.get_args()
        if text:
            await message.answer("✅ Окно показано на мониторе.")
            pyautogui.alert(text, "Сообщение от Telegram")
        else:
            await message.answer("Напиши текст: /msg Привет")

# Команда /off
@dp.message_handler(commands=['off'])
async def shutdown_pc(message: types.Message):
    if is_admin(message.from_user.id):
        await message.answer("⚠ Выключаю компьютер через 10 секунд...")
        os.system("shutdown /s /t 10")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
