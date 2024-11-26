from sqlalchemy import Column, Integer, DateTime, String
from app.db.base import Base

class UserToken(Base):
    __tablename__ = "user_token"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    expired_at = Column(Integer)
    userId = Column(Integer)
    refresh_token = Column(String) 
    