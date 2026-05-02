import os
import pyautogui
from aiogram import Bot, Dispatcher, types, executor

# --- ТВОИ ДАННЫЕ ---
API_TOKEN = '8777973485:AAHg2x7ez-wCOMb1b9CEC-uaO4uKf4tVAxM'
ADMIN_ID = 0  # ЗАМЕНИ 0 НА СВОЙ ID (например, 12345678)
# -------------------

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Проверка, что пишет именно хозяин
def is_admin(user_id):
    return user_id == ADMIN_ID

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    if is_admin(message.from_user.id):
        await message.answer(
            "🎮 Доступ разрешен!\n\n"
            "Команды управления:\n"
            "📸 /screen — сделать скриншот\n"
            "🔌 /off — выключить компьютер\n"
            "💬 /msg <текст> — отправить окно с текстом на экран"
        )
    else:
        await message.answer("Ошибка доступа. Вы не являетесь администратором.")

@dp.message_handler(commands=['screen'])
async def make_screenshot(message: types.Message):
    if is_admin(message.from_user.id):
        try:
            # Делаем скриншот
            pyautogui.screenshot("temp_screen.png")
            with open("temp_screen.png", "rb") as photo:
                await bot.send_photo(message.chat.id, photo, caption="Текущий экран ПК")
            os.remove("temp_screen.png")
        except Exception as e:
            await message.answer(f"Не удалось сделать скрин: {e}")

@dp.message_handler(commands=['msg'])
async def send_message_pc(message: types.Message):
    if is_admin(message.from_user.id):
        text = message.get_args()
        if text:
            # Всплывающее окно на компьютере
            pyautogui.alert(text, "Внимание!")
            await message.answer("Сообщение доставлено на рабочий стол.")
        else:
            await message.answer("Пример: /msg Купи хлеб")

@dp.message_handler(commands=['off'])
async def shutdown_pc(message: types.Message):
    if is_admin(message.from_user.id):
        await message.answer("Выключение компьютера через 10 секунд...")
        os.system("shutdown /s /t 10")

if __name__ == '__main__':
    print("Бот запущен. Ожидаю команд от ID:", ADMIN_ID)
    executor.start_polling(dp, skip_updates=True)
