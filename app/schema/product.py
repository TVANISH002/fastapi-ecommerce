from pydantic import BaseModel, Field
from typing import Optional


class Product(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    category: Optional[str] = Field(default=None, max_length=50)
    in_stock: bool = True


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    price: Optional[float] = Field(default=None, gt=0)
    category: Optional[str] = Field(default=None, max_length=50)
    in_stock: Optional[bool] = None
