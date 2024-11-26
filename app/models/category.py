from sqlalchemy import Column, Integer, ARRAY, String, ForeignKey
from app.db.base import Base
from sqlalchemy.orm import relationship

class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    priority = Column(String, nullable=True)
    status = Column(String, nullable=False, default="active")
    banner_image = Column(String, nullable=True)
    description = Column(String, nullable=True)
    sub_categories = Column(ARRAY(String), nullable=True)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'), nullable=False)
    restaurant = relationship('Restaurant', back_populates='category')
    dishes = relationship('Dish', back_populates='category')
    
    # from app.models.dish import Dish