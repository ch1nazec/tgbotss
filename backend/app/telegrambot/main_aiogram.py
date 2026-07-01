import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import bot_token



bot = Bot(bot_token)
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start(mess: Message):
    await mess.answer(
        'Даров, заебал!',
        
    )


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())