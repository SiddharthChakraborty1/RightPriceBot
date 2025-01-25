import os
import telebot
from telebot.types import Message, BotCommand
from uuid import uuid4
from dotenv import load_dotenv
import re
from helpers.utils import get_user_from_message
import firebase_admin
from firebase_admin import credentials, db
from database.models.user import User
from database.models.product import Product
from helpers.content_parsers import AmazonParser


load_dotenv()


TOKEN = os.environ.get("TOKEN")
commands = [
    BotCommand("start", "Start the bot"),
    BotCommand("track", "Track a product")
]
def _get_rtdb_configs():
    return {
        "type": os.environ.get("RTDF_TYPE"),
        "auth_uri": os.environ.get("RTDB_AUTH_URI"),
        "client_id": os.environ.get("RTDB_CLIENT_ID"),
        "token_uri": os.environ.get("RTDB_TOKEN_URi"),
        "project_id": os.environ.get("RTDB_PROJECT_ID"),
        "private_key": os.environ.get("RTDB_PRIVATE_KEY"),
        "client_email": os.environ.get("RTDB_CLIENT_EMAIL"),
        "private_key_id": os.environ.get("RTDB_PRIVATE_KEY_ID"),
        "auth_provider_x509_cert_url": os.environ.get(
            "RTDB_AUTH_PROVIDER_X509_CERT_URL"
        ),
        "universe_domain": os.environ.get("RTDB_UNIVERSE_DOMAIN"),
        "client_x509_cert_url": os.environ.get("RTDB_CLIENT_X509_CERT_URL"),
    }
DB_URL = os.environ.get("RTDB_URL")
bot = telebot.TeleBot(TOKEN)
bot.set_my_commands(commands)
firebase_config = _get_rtdb_configs()
cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred, {
    "databaseURL": f"{DB_URL}/"
})


@bot.message_handler(commands=["start", "hello"])
def send_welcome(message: Message):
    chat_user = get_user_from_message(message)
    user_ref = db.reference("users")
    reply: str = "Hey, ready to start tracking? Send the tracking link and expected price separated by a space!"
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
        if all_products := user_ref.child(str(chat_user.id)).child('products').get():
            print("all_products", all_products)
            for id, product_meta in all_products.items():
                bot.send_message(
                    message.chat.id,
                    f"Link -> {product_meta.get('tracking_link')} \nExpected Price -> {product_meta.get('expected_price')} \nCurrent Price -> {product_meta.get('current_price')}",
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
    if(len(command_args) < 3):
        bot.reply_to(message, "Please provide the tracking link and the expected price separated by a space")
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
        tracking_link=link, current_price=price, expected_price=expected_price, platform="amazon"
        
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
    bot.send_message(message.chat.id, text=f"Rest easy, we'll notify you once the price deviates from {price}")

@bot.message_handler(commands=["debug"])
def debug_print(message:Message):
    print("user", message.from_user)
    print("message", message)
    user = User(
        chat_id=message.chat.id,
        user_id=str(message.from_user.id),
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )
    print(f"user is {user.model_dump()}")
    print("now fetching users")
    user_ref: db.Reference = db.reference("users")
    this_user_ref = user_ref.child(str(message.from_user.id))
    # now fetching current user product
    product_ref = this_user_ref.child("products")
    print("product_ref", product_ref)
    # printing current user products
    print("product_ref is", product_ref.get())
    all_products: dict = product_ref.get()
    bot.send_message(message.chat.id, "Fetching list of your products")
    for id, product_meta in all_products.items():
        bot.send_message(message.chat.id, f"Link -> {product_meta.get('tracking_link')} \nExpected Price -> {product_meta.get('expected_price')} \nCurrent Price -> {product_meta.get('current_price')}")


bot.infinity_polling()
