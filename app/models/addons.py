from sqlalchemy import Column, Integer, Numeric, String, Boolean, ForeignKey
from app.db.base import Base
from sqlalchemy.orm import relationship
from .associations import dish_addon_association

class Addons(Base):
    __tablename__ = "addons"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)

    # Foreign key to reference the restaurant that created the addon
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'), nullable=False)
    restaurant = relationship('Restaurant', back_populates='addons')

    # Many-to-many relationship with Dish
    dishes = relationship('Dish', secondary=dish_addon_association, back_populates='addons')