import logging
import hashlib
from os import getenv

import validators
from requests import post, delete
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineQuery, \
    InputTextMessageContent, InlineQueryResultArticle
from aiogram.dispatcher.webhook import SendMessage, AnswerInlineQuery
from aiogram.utils.executor import start_webhook
from dotenv import load_dotenv

# Configure Logging
logging.basicConfig(level=logging.INFO)

API_BASE_URL = "https://short-url-a25r.onrender.com"
WEBHOOK_URL = f"{API_BASE_URL}/webhook"
load_dotenv(".env")

# Initialize bot and dispatcher
bot = Bot(token=getenv("BOT_TOKEN"))
dp = Dispatcher(bot=bot)


@dp.message_handler(commands=['start', 'help'])
async def help_handler(message: types.Message):
    return SendMessage(f"Hi, {message.from_user.full_name}!"
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
        return AnswerInlineQuery(inline_query.id, results=[item], cache_time=1)


@dp.message_handler(commands=['create_url'])
async def create_url(message: types.Message):
    url = message.text.split(' ')[1]
    if validators.url(url):
        resp = post(url=f"{API_BASE_URL}/url", json={"target_url": url})
        data = resp.json()
        res = f"Your short URL: {data['url']}" \
              f"\nAdmin URL:\n {data['admin_url']}\n" \
              f"\nPLEASE SAVE YOUR ADMIN URL, SINCE ONLY WITH IT YOU CAN ACCESS TO URL INFO."
        return SendMessage(text=res)
    else:
        return SendMessage("Please provide a valid URL address!")


@dp.message_handler(commands=['deactivate'])
async def deactivate(message: types.Message):
    if message.text == '/deactivate':
        await message.answer("Please provide your secret key in one message with command. "
                             "E.g.: '/deactivate MY_SECRET_KEY'")
    else:
        try:
            secret_key = message.text.split(' ')[1]
            r = delete(f"{API_BASE_URL}/admin/{secret_key}")

            return SendMessage(r.json()['detail'])
        except Exception as e:
            print(e)
            return SendMessage("PLEASE PROVIDE VALID SECRET KEY")


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    print("start...")


async def on_shutdown(dp):
    await bot.delete_webhook()


if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_URL,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
    )
