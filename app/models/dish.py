from sqlalchemy import Column, Integer, Numeric, String, ForeignKey, DateTime, func
from app.db.base import Base
from sqlalchemy.orm import relationship
from .associations import dish_addon_association

class Dish(Base):
    __tablename__ = "dish"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    discount = Column(Numeric(10, 2), nullable=True)
    availability = Column(String, nullable=True)
    image = Column(String, nullable=True)
    description = Column(String, nullable=True)
    spice_level = Column(String, nullable=False)
    hot_seller = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    category = relationship('Category', uselist=False, back_populates='dishes')
    sub_category = Column(String, nullable=True)
    variant = Column(String, nullable=False)
    addons = relationship('Addons', secondary=dish_addon_association, back_populates='dishes') # Many-to-many relationship with Addons
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'), nullable=False)
    restaurant = relationship('Restaurant', back_populates='dishes')
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now()) 

