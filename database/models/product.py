from pydantic import BaseModel
from typing import Literal


class Product(BaseModel):
    tracking_link: str
    current_price: float
    expected_price: float
    platform: Literal["amazon"]

    class Config:
        extra = "forbid"
