from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

class CategoryBase(BaseModel):
    name: str
    priority: Optional[str] = None
    status: str
    banner_image: Optional[str] = None
    description: Optional[str] = None
    sub_categories: Optional[List[str]] = None

class CategoryCreate(CategoryBase):
    restaurant_id: int
    
class CategoryUpdate(CategoryBase):
    restaurant_id: int
    
class CategoryRead(CategoryBase):
    id: int

    class Config:
        orm_mode = True 