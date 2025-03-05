import os
import telebot
from telebot.types import Message, BotCommand
from dotenv import load_dotenv
import time
import threading
from ai_utils.deep_seek import DeepSeekManager
from database.db_connector import initialize_db
import re
from helpers.utils import get_user_from_message
from database.models.user import User
from database.models.product import Product
from helpers.content_parsers import AmazonParser

load_dotenv()


TOKEN = os.environ.get("TOKEN")
commands = [
    BotCommand("start", "Start the bot"),
    BotCommand("track", "Track a product"),
    BotCommand("ai", "Chat with AI"),
]

bot = telebot.TeleBot(TOKEN)
bot.set_my_commands(commands)
db = initialize_db()


@bot.message_handler(commands=["start", "hello"])
def send_welcome(message: Message):
    chat_user = get_user_from_message(message)
    user_ref = db.reference("users")
    reply: str = """
    Hey, ready to start tracking?
    Send the tracking link and expected price separated by a space!
    """
    if not user_ref.child(str(chat_user.id)).get():
        print("user does not exist")
        # Create the user and set it in db
        new_user = User(
            chat_id=message.chat.id,
            user_id=str(chat_user.id),
            username=chat_user.username,
            first_name=chat_user.first_name,
        )
        user_ref.child(new_user.user_id).set(new_user.model_dump())
    else:
        print("user exists")
        if (
            all_products := user_ref.child(str(chat_user.id))
            .child("products")
            .get()
        ):
            print("all_products", all_products)
            for id, product_meta in all_products.items():
                bot.send_message(
                    message.chat.id,
                    (
                        "Link ->"
                        f" {product_meta.get('tracking_link')} \nExpected"
                        " Price ->"
                        f" {product_meta.get('expected_price')} \nCurrent"
                        f" Price -> {product_meta.get('current_price')}"
                    ),
                )
            return

        else:
            bot.reply_to(message, reply)
            return

    bot.reply_to(message, reply)


@bot.message_handler(commands=["track"])
def track_link(message: Message):
    print("now tracking")

    command_args = message.text.split(maxsplit=2)
    if len(command_args) < 3:
        bot.reply_to(
            message,
            (
                "Please provide the tracking link and the expected price"
                " separated by a space"
            ),
        )
        return

    link = command_args[1]
    expected_price = float(command_args[2])
    url_pattern = r"(https?://[^\s]+)"
    match = re.match(url_pattern, link)
    if not match:
        bot.reply_to(message, "The URL is invalid")
        return

    parser = AmazonParser()
    price = float(parser.get_price(link).replace(",", ""))
    product = Product(
        tracking_link=link,
        current_price=price,
        expected_price=expected_price,
        platform="amazon",
    )
    user = get_user_from_message(message)
    product_ref = db.reference("users").child(str(user.id)).child("products")
    all_products = product_ref.get()
    new_product = product.model_dump()
    if not all_products:
        product_ref.set(new_product)
    else:
        product_ref.push(new_product)
    product_ref.push(product.model_dump())
    bot.send_message(
        message.chat.id,
        text=(
            f"Rest easy, we'll notify you once the price deviates from {price}"
        ),
    )


@bot.message_handler(commands=["debug"])
def debug_print(message: Message):
    print("user", message.from_user)
    print("message", message)
    user = User(
        chat_id=message.chat.id,
        user_id=str(message.from_user.id),
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )
    print(f"user is {user.model_dump()}")
    print("now fetching users")
    user_ref = db.reference("users")
    this_user_ref = user_ref.child(str(message.from_user.id))

    product_ref = this_user_ref.child("products")
    print("product_ref", product_ref)
    print("product_ref is", product_ref.get())
    all_products: dict = product_ref.get()
    bot.send_message(message.chat.id, "Fetching list of your products")
    for id, product_meta in all_products.items():
        bot.send_message(
            message.chat.id,
            (
                f"Link -> {product_meta.get('tracking_link')} \nExpected Price"
                f" -> {product_meta.get('expected_price')} \nCurrent Price ->"
                f" {product_meta.get('current_price')}"
            ),
        )


@bot.message_handler(commands=["ai"])
def greet_ai(message: Message):
    command_args = message.text.split(maxsplit=2)
    chat_id = message.chat.id
    ai_manager = DeepSeekManager()

    user_message = " ".join(command_args[1::])
    loading_message = bot.send_message(chat_id, "Thinking")
    print("user message", user_message)

    def process_with_loading():
        nonlocal loading_message
        dots = [".", "..", "..."]
        counter = 0

        def update_loading():
            nonlocal counter
            while not processing_done:
                bot.edit_message_text(
                    f"Thinking{dots[counter % 3]}",
                    chat_id,
                    loading_message.message_id,
                )
                counter += 1
                time.sleep(0.5)

        global processing_done
        processing_done = False
        loading_thread = threading.Thread(target=update_loading)
        loading_thread.start()

        response = ai_manager.chat(user_message)
        processing_done = True

        bot.edit_message_text(response, chat_id, loading_message.message_id)

    processing_thread = threading.Thread(target=process_with_loading)
    processing_thread.start()


bot.infinity_polling()
