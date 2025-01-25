from database.models import user

class UserManager:
    
    def check_if_exists(self, username):
        """Checks if a user already exists"""
        # Check cache if user exists
        # if yes, return True
        # If not, check db if user exists
        # if not, return False
        # if yes, rehydrate the cache and return True
        pass
    
    def create_user(self, user_info: dict):
        """Creates a new user in db and saves in cache"""
        