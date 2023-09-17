import os
import json

import openai
from aiogram import Bot, Dispatcher, executor, types


TOKEN = os.environ["OPENAI_API_KEY_FOR_BOTS"]

bot = Bot(TOKEN)
dp = Dispatcher(bot)


def on_startup(_):
    print("\n...\n\tHere we go\n...\n")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
