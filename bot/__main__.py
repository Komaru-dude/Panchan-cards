import asyncio, os, logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from .handlers.basic import base_router

async def main():
    # Подгружаем виртуальное окружение
    load_dotenv()
    # Настраиваем логирование
    logging.basicConfig(level=logging.INFO)
    # Вытаскиваем токен из виртуального окружения
    token = os.getenv("BOT_API_TOKEN")
    # Создаём объект бота
    bot = Bot(token, ParseMode=ParseMode.MARKDOWN_V2)
    # Диспетчер
    dp = Dispatcher()
    # Регистрируем хэндлеры
    dp.include_routers(base_router)
    # Наконец, запуск
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())