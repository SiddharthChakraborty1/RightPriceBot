import os
import telebot
from telebot.types import Message, BotCommand
from dotenv import load_dotenv
import re
from helpers.content_parsers import AmazonParser


load_dotenv()

TOKEN = os.environ.get("TOKEN")
commands = [
    BotCommand("start", "Start the bot"),
    BotCommand("track", "Track a product")
]

bot = telebot.TeleBot(TOKEN)
bot.set_my_commands(commands)


@bot.message_handler(commands=["start", "hello"])
def send_welcome(message):
    bot.reply_to(message, "Hey, ready to start tracking?")

@bot.message_handler(commands=["track"])
def track_link(message: Message):
    print("now tracking")

    command_args = message.text.split(maxsplit=1)
    if(len(command_args) < 2):
        bot.reply_to(message, "Please provide a link to track")
        return

    link = command_args[1]
    url_pattern = r"(https?://[^\s]+)"
    match = re.match(url_pattern, link)
    if not match:
        bot.reply_to(message, "The URL is invalid")
        return
    
    parser = AmazonParser()
    price = parser.get_price(link)
    bot.send_message(message.chat.id, text=f"Rest easy, we'll notify you once the price deviates from {price}")


bot.infinity_polling()
