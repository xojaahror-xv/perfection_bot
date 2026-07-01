import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database import init_db
from handlers import router

logging.basicConfig(level=logging.INFO)

async def main():
    # Ma'lumotlar bazasini initsializatsiya qilish
    init_db()

    # Bot va Dispatcher yaratish
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Router'ni ulash
    dp.include_router(router)

    # Botni ishga tushirish (Polling)
    await bot.delete_webhook(drop_pending_updates=True)
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi.")
