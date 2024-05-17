from ast import Constant
from collections import defaultdict
from os import getenv
from typing import Callable, Optional
from gemini_webapi import GeminiClient
from aiogram.types import Message
from aiogram.utils.markdown import blockquote
from dotenv import load_dotenv
load_dotenv()

# Replace "COOKIE VALUE HERE" with your actual cookie values.
# Leave Secure_1PSIDTS empty if it's not available for your account.
Secure_1PSID = getenv("SECURE_1PSID")
Secure_1PSIDTS = getenv("SECURE_1PSIDTS")
assert Secure_1PSID is not None, "Secure_1PSID is not set"
assert Secure_1PSIDTS is not None, "Secure_1PSIDTS is not set"

client = GeminiClient(Secure_1PSID, Secure_1PSIDTS, proxies=None)
chats = defaultdict(client.start_chat)

is_initialized = False

Prompter = Callable[[Message], str]


def get_message_text(message: Message) -> str:
    text = message.text if message.text is not None else message.caption
    if text is None:
        text = ""
    if message.reply_to_message is not None:
        quoted = get_message_text(message.reply_to_message)
        text = f"{blockquote(quoted)}\n\n{text}"
    return text


async def get_message_image(message: Message) -> Optional[bytes]:
    if message.photo:
        file_info = await message.bot.get_file(message.photo[-1].file_id)
        bytes_io = await message.bot.download_file(file_info.file_path)
        return bytes_io.read()
    elif message.reply_to_message:
        return await get_message_image(message.reply_to_message)
    return None


async def ask(message: Message, prompter: Optional[Callable] = None) -> str:
    global is_initialized
    if not is_initialized:
        await client.init(
            timeout=300, auto_close=False, close_delay=300, auto_refresh=True
        )
        is_initialized = True
    chat = chats[message.chat.id]
    if prompter is not None:
        text = prompter(message)
    else:
        text = get_message_text(message)
    # if has image
    image: Optional[Constant] = await get_message_image(message)

    if text.startswith("@"):
        if not text.startswith("@youtube"):
            text = text[1:]  # 保护隐私
    response = await chat.send_message(text, image=image)
    urls = []
    for img in response.images:
        urls.append(img.url)
    text = response.text
    if urls:
        text += "\n\n" + "\n".join(urls)
    return text


async def rewrite(message: Message, style: str) -> str:
    prompters = {
        "beijing": """你是一个土生土长的北京人，40岁,是个普通的老百姓会北京俚语、你喜欢用修辞手法来叙事。你爱关注时事,喜欢就社会热点新闻发表自己的看法。
现在,帮我写一篇文章，不得抄袭原文中的任何句子，直接写出全文，不需要小标题和提示词，语言通俗易懂、接地气，并且需要分析、叙述结合输出全文，灵活使用成语俗语歇后语，如文中有年份或者数据，请在全文适当位置使用，语气要贴近生活，全文上下文逻辑性强。
文章结构为:
【背景介绍】：理解文中内容，详细介绍文章发生时的背景，可适当添加一句名言或俗语，最后要疑问或反问的带入手法;
【正文内容】:不需要分述点，将全文核心内容，详细的描述出来，语言要有感染力，能与读者产生共鸣;介绍正文内容最终的一个结局，内容要详细，有趣幽默，不要重复表达正文内容;
【结尾升华】:根据全文内容，做主题升华和观点输出，可适当使用不同修辞手法，使得文章更具有趣味性和阅读性。

文章概要如下：""",
        "canton": """你喺廣東土生土長嘅，三十幾歲人仔，講開廣東話，香港嗰啲潮語、俚語都識。鍾意用啲修辭手法嚟講故仔。平時都好留意時事，得閒就上 lihkg 灌水。
        請幫我寫一篇文章，唔好抄襲原文中嘅任何句子，直接寫出全文，唔需要小標題同提示詞，語言通俗易懂、接地氣，需要分析、敘述結合輸出全文，靈活使用成語俗語，如文中有年份或者數據，請喺全文適當位置使用，語氣要貼近生活，全文上下文邏輯性強。""",
        # 係一個土生土長嘅廣東人，三十幾歲，講得一口流利嘅廣東話，香港嘅俚語都識。鍾意用啲修辭手法嚟講故仔，又鍾意𥄫下時事新聞，喺
    }
    if style in prompters:
        return await ask(
            message, lambda msg: prompters[style] + "\n" + get_message_text(msg)
        )
    else:
        return "Unknown style"
