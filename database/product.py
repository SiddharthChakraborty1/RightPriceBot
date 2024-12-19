from pydantic import BaseModel

class Product(BaseModel):
    user_id: str
    tracking_link: str
    expected_price: float
    
    
    class Config:
        extra = "forbid"