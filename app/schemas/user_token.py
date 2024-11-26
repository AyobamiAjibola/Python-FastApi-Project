from pydantic import BaseModel
from typing import Optional

class UserTokenBase(BaseModel):
    expired_at: int
    userId: int
    refresh_token: str

class UserTokenCreate(UserTokenBase):
    expired_at: int
    userId: int
    refresh_token: str

class UserTokenResponse(UserTokenBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True 