from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    
    user_id: str
    user_name: str
    
    class Config:
        extra = "forbid"
