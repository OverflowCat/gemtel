import asyncio
import logging
from os import getenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.markdown import hbold
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from gem import ask, rewrite
from aiogram.client.session.aiohttp import AiohttpSession

PROXY = getenv("PROXY")
session = AiohttpSession(proxy=PROXY) if PROXY else None

TOKEN = getenv("GEM_BOT_TOKEN")
assert TOKEN is not None, "GEM_BOT_TOKEN is not set"

dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.reply(
        f"你好, {hbold(message.from_user.full_name)}!", parse_mode=ParseMode.HTML
    )


@dp.message(Command("gem"))
async def cmd_ask(message: types.Message):
    waiting_msg = await message.reply("正在请求 Gemini Advanced，请稍等…")
    # 引用发送的消息
    # 调用 Gemini
    try:
        response = await ask(message)
    except Exception as e:
        response = str(e).split("\n")[-1]
    try:
        await message.reply(response, parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as _:
        await message.reply(response)
    await waiting_msg.delete()


@dp.message(Command("beijing"))
async def cmd_beijing(message: types.Message):
    waiting_msg = await message.reply(
        "正跟 Gemini Advanced 这家伙商量着，给您整点儿地道的老北京味儿，您擎好吧您嘞！"
    )
    try:
        response = await rewrite(message, "beijing")
    except Exception as e:
        response = str(e).split("\n")[-1]
    try:
        await message.reply(response, parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as _:
        await message.reply(response)
    await waiting_msg.delete()


@dp.message(Command("canton"))
async def cmd_canton(message: types.Message):
    waiting_msg = await message.reply(
        "等陣先，我依家叫緊 Gemini Advanced 幫你用廣東話重新寫過啲嘢…"
    )
    try:
        response = await rewrite(message, "canton")
    except Exception as e:
        response = str(e).split("\n")[-1]
    try:
        await message.reply(response, parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as _:
        await message.reply(response)
    await waiting_msg.delete()


"""
@dp.message(F.text.startswith("/gem"))
async def echo(message: types.Message):
    waiting_msg = await message.reply("正在请求 Gemini Advanced，请稍等…")
    try:
        response = await ask(message)
    except Exception as e:
        response = str(e).split("\n")[-1]
    try:
        await message.reply(response, parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as _:
        await message.reply(response)
    await waiting_msg.delete()
"""


async def main():
    # 创建 Bot 实例
    bot = Bot(token=TOKEN, session=session)

    # 启动 bot
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
