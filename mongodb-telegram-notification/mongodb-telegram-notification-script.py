import pymongo
from pymongo import MongoClient
import telebot
from telebot.types import InputMediaPhoto
from telebot.apihelper import ApiTelegramException
from telebot.util import antiflood
from datetime import datetime, timedelta
import json
import os
import time
import random
import re

# MongoDB连接设置
MONGO_URI = "mongodb+srv://readonly:cS9NSuiJ1ebHnUL0@cluster0.8mosa.mongodb.net/Cluster0?retryWrites=true&w=majority"
DATABASE_NAME = "sehuatang"
COLLECTION_NAME = "asia_mosaic_originate"

# Telegram Bot设置
TELEGRAM_BOT_TOKEN = "6*****************************KQ"
CHAT_ID = "-10***********"

# 配置文件路径
CONFIG_FILE = "config.json"

# 保留的天数
KEEP_DAYS = 7

# 图片代理URL
IMAGE_PROXY_URL = "https://sht-img.790366.xyz"

# 需要转义的Markdown字符
MARKDOWN_ESCAPE_CHARS = [
    "_",
    "*",
    "[",
    "]",
    "(",
    ")",
    "~",
    "`",
    ">",
    "#",
    "+",
    "-",
    "=",
    "|",
    "{",
    "}",
    ".",
    "!",
]

# 连接到MongoDB
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# 创建Telegram Bot实例
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"sent_items": {}, "query_date": None}


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)


def clean_old_data(config):
    today = datetime.now().date()
    config["sent_items"] = {
        date: items
        for date, items in config["sent_items"].items()
        if (today - datetime.strptime(date, "%Y-%m-%d").date()).days < KEEP_DAYS
    }


def replace_image_url(image_url):
    pattern = r"(https?://)([^/]+)/tupian"
    return re.sub(pattern, f"{IMAGE_PROXY_URL}/tupian", image_url)


def escape_markdown(text):
    for char in MARKDOWN_ESCAPE_CHARS:
        text = text.replace(char, f"\\{char}")
    return text


def send_telegram_message(chat_id, content, image_list):
    media_group = []
    for index, image in enumerate(image_list):
        image = replace_image_url(image)
        if index == len(image_list) - 1:
            media_group.append(
                InputMediaPhoto(media=image, caption=content, parse_mode="MarkdownV2")
            )
        else:
            media_group.append(InputMediaPhoto(media=image))

    try:
        antiflood(bot.send_media_group, chat_id=chat_id, media=media_group)
        return True
    except ApiTelegramException as e:
        print(f"Telegram API 错误: {e}")
        return False
    except Exception as e:
        print(f"发送消息时出错: {e}")
        return False


def query_and_notify():
    config = load_config()
    clean_old_data(config)

    query_date = config.get("query_date") or datetime.now().strftime("%Y-%m-%d")
    sent_items = set(config["sent_items"].get(query_date, []))

    query = {"date": query_date}
    results = collection.find(query).sort("post_time", pymongo.DESCENDING)

    new_sent_items = []
    for doc in results:
        doc_id = str(doc["_id"])
        if doc_id not in sent_items:
            content = f"*日期:* {escape_markdown(doc['date'])}\n"
            content += f"*标题:* {escape_markdown(doc['title'])}\n"
            content += f"*发布时间:* {escape_markdown(doc['post_time'])}\n"
            content += f"*番号:* {escape_markdown(doc['number'])}\n"

            if doc["magnet"]:
                content += f"*磁力链接:* `{escape_markdown(doc['magnet'])}`\n"

            if doc["img"] and len(doc["img"]) > 0:
                if send_telegram_message(CHAT_ID, content, doc["img"]):
                    new_sent_items.append(doc_id)
                    sent_items.add(doc_id)
                else:
                    print(f"无法发送消息，ID: {doc_id}")
            else:
                # 如果没有图片，发送普通文本消息
                try:
                    antiflood(
                        bot.send_message,
                        chat_id=CHAT_ID,
                        text=content,
                        parse_mode="MarkdownV2",
                    )
                    new_sent_items.append(doc_id)
                    sent_items.add(doc_id)
                except Exception as e:
                    print(f"发送文本消息时出错，ID: {doc_id}, 错误: {e}")

    config["sent_items"][query_date] = list(sent_items)
    save_config(config)

    return len(new_sent_items)


def set_query_date(date_str):
    config = load_config()
    config["query_date"] = date_str
    save_config(config)
    print(f"查询日期已设置为: {date_str}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        set_query_date(sys.argv[1])
    else:
        sent_count = query_and_notify()
        print(f"已发送 {sent_count} 条新通知")
