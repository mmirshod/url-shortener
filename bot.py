import logging
import hashlib
from os import getenv

import validators
from requests import post, delete
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineQuery, \
    InputTextMessageContent, InlineQueryResultArticle
from dotenv import load_dotenv

# Configure Logging
logging.basicConfig(level=logging.INFO)

API_BASE_URL = "https://short-url-a25r.onrender.com"
load_dotenv(".env")


# Initialize bot and dispatcher
bot = Bot(token=getenv("BOT_TOKEN"))
dp = Dispatcher(bot=bot)


@dp.message_handler(commands=['start', 'help'])
async def help_handler(message: types.Message):
    await message.reply(f"Hi, {message.from_user.full_name}!"
                        f"\nThis is Telegram Bot to share with your friends long URLs as short links."
                        f"\nAll Commands:"
                        f"\n/help --> You will get this message."
                        f"\n/create_url --> To create short URL."
                        f"\n/deactivate --> To deactivate your short URL"
                        )


@dp.inline_handler()
async def create_url(inline_query: InlineQuery):
    url = inline_query.query
    if validators.url(url):
        resp = post(url=f"{API_BASE_URL}/url", json={"target_url": url})
        data = resp.json()
        res = f"Your short URL for {url}: {data['url']}" \
              f"\nAdmin URL:\n {data['admin_url']}\n" \
              f"\nPLEASE SAVE YOUR ADMIN URL, SINCE ONLY WITH IT YOU CAN ACCESS TO URL INFO."
        input_content = InputTextMessageContent(res)
        result_id: str = hashlib.md5(res.encode()).hexdigest()
        item = InlineQueryResultArticle(
            id=result_id,
            title=f"SHORT URL",
            input_message_content=input_content
        )
        await bot.answer_inline_query(inline_query.id, results=[item], cache_time=1)


@dp.message_handler(commands=['create_url'])
async def create_url(message: types.Message):
    url = message.text.split(' ')[1]
    if validators.url(url):
        resp = post(url=f"{API_BASE_URL}/url", json={"target_url": url})
        data = resp.json()
        res = f"Your short URL: {data['url']}" \
              f"\nAdmin URL:\n {data['admin_url']}\n" \
              f"\nPLEASE SAVE YOUR ADMIN URL, SINCE ONLY WITH IT YOU CAN ACCESS TO URL INFO."
        await message.answer(text=res)
    else:
        await message.answer("Please provide a valid URL address!")


@dp.message_handler(commands=['deactivate'])
async def deactivate(message: types.Message):
    if message.text == '/deactivate':
        await message.answer("Please provide your secret key in one message with command. "
                             "E.g.: '/deactivate MY_SECRET_KEY'")
    else:
        try:
            secret_key = message.text.split(' ')[1]
            r = delete(f"{API_BASE_URL}/admin/{secret_key}")

            await message.answer(r.json()['detail'])
        except Exception as e:
            print(e)
            await message.answer("PLEASE PROVIDE VALID SECRET KEY")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
