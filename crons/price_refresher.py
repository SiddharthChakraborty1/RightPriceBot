from database.db_connector import initialize_db
from managers.product_manager import ProductManager
import os
import telebot

db = initialize_db()
message_queue = {}


def notify_users():
    if not message_queue:
        return

    TOKEN = os.environ.get("TOKEN")
    bot = telebot.TeleBot(TOKEN)
    for user_id in message_queue.keys():
        bot.send_message(user_id, "Price of an item has changed")


def check_product_prices_for_user(
    product_handler: ProductManager, user_id: str, products: dict
):
    if not all([user_id, products]):
        return

    notifiable_products = {}

    for product_id, product_info in products.items():
        current_price = product_handler.fetch_product_price(
            product=product_info
        )
        if current_price != product_info.get("current_price", 0):
            # TODO @sid -> update current price of the product in db
            pass

        if current_price <= product_info.get("expected_price", 0):
            product_info.update({"current_price": current_price})
            notifiable_products[product_id] = product_info

    if not notifiable_products:
        return

    message_queue[user_id] = notifiable_products


def refresh_prices():
    product_handler = ProductManager(database=db)
    user_wise_products = product_handler.fetch_user_wise_products()
    if not user_wise_products:
        return

    for user_id, products in user_wise_products.items():
        check_product_prices_for_user(product_handler, user_id, products)

    message_queue and notify_users()


refresh_prices()
