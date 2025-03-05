from firebase_admin import db
from helpers.content_parsers import AmazonParser


class ProductManager:
    def __init__(self, database: db):
        self.db = database
        self.parser: AmazonParser = AmazonParser()

    def fetch_user_wise_products(self) -> list:
        """
        This is an unsafe method as it fetches all users at once
        and iterates over them to fetch all of their products that
        have been saved, only use if dataset is small or retrieval
        is super fast
        """
        user_ref = self.db.reference("users")
        users_data = user_ref.get()

        if not users_data:
            return []

        user_wise_products: dict = {}

        for user_id, user_info in users_data.items():
            print(user_info)
            user_products = user_info.get("products", {})
            user_wise_products[user_id] = user_products

        return user_wise_products

    def fetch_product_price(self, product: dict) -> None | int:
        if not product:
            return None

        print("product supplied to fetch_product_price", product)

        link = product.get("tracking_link")
        current_price = float(self.parser.get_price(link).replace(",", ""))
        print(f"price for product {link} is {current_price}")
        return current_price
