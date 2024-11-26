from typing import List, Optional
from pydantic import BaseModel, StringConstraints, Field
from typing_extensions import Annotated
from decimal import Decimal

# Addons Schema
class AddonsBase(BaseModel):
    name: Annotated[
            str,
            StringConstraints(
                strip_whitespace=True,
                min_length=1
            ),
        ]
    price: Annotated[Decimal, Field(strict=True, gt=0, decimal_places=2)]
    
class AddonsCreate(AddonsBase):
    restaurant_id: int

class AddonsUpdate(AddonsBase):
    name: Optional[
            Annotated[
                str,
                StringConstraints(
                    strip_whitespace=True,
                    min_length=1
                ),
            ]
        ] = None
    price: Optional[
            Annotated[Decimal, Field(strict=True, gt=0, decimal_places=2)]
        ] = None

class AddonsRead(AddonsBase):
    id: int
    dishes: Optional[List[int]] = []

    class Config:
        orm_mode = True 