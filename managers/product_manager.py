from firebase_admin import db

class ProductManager:
    
    def __init__(self, database: db):
        self.db = database
    
    def fetch_all_products(self)->list:
        """
        This is an unsafe method as it fetches all users at once and iterates over them
        to fetch all of their products that have been saved, only use if dataset is small or retrieval is super fast
        """
        all_products = []
        user_ref = self.db.reference("users")
        users_data = user_ref.get()
        
        if not users_data:
            return []
        
        for _ , user_info in users_data.item():
            user_products = user_info.get("products", [])
            all_products.extend(user_products)
        
        return all_products
