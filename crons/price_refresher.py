from database.db_connector import initialize_db
from managers.product_manager import ProductManager

db = initialize_db()

product_handler = ProductManager(database=db)
all_products = product_handler.fetch_all_products()
print("all_products", all_products)
