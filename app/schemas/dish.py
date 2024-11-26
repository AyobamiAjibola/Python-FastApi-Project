from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime
from typing_extensions import Annotated
from fastapi import Form, UploadFile

# Common type aliases for reusability
DecimalField = Annotated[Decimal, Field(strict=True, gt=0, decimal_places=2)]

# Mixin for shared `as_form` logic
class FormMixin:
    @classmethod
    def as_form(cls, **data) -> "BaseModel":
        return cls(**data)

class CreateDish(BaseModel, FormMixin):
    name: str = Form()
    price: DecimalField = Form()
    discount: Optional[DecimalField] = Form(None)
    image: Optional[UploadFile] = Form(None)
    description: Optional[str] = Form(None)
    spice_level: str = Form()
    hot_seller: Optional[str] = Form(None)
    category_id: int = Form()
    sub_category: Optional[str] = Form(None)

class UpdateDish(BaseModel, FormMixin):
    name: Optional[str] = Form(None)
    price: Optional[DecimalField] = Form(None)
    discount: Optional[DecimalField] = Form(None)
    image: Optional[UploadFile] = Form(None)
    description: Optional[str] = Form(None)
    spice_level: Optional[str] = Form(None)
    hot_seller: Optional[str] = Form(None)
    category_id: Optional[int] = Form(None)
    sub_category: Optional[str] = Form(None)
    
class DishRead(BaseModel):
    id: int
    restaurant_id: int
    
    class Config:
        from_attributes = True
    
    