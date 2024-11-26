from sqlalchemy import Column, Integer, Table, ForeignKey
from app.db.base import Base

# Association table for the many-to-many relationship between Dish and Addons
dish_addon_association = Table('dish_addons', Base.metadata,
    Column('dish_id', Integer, ForeignKey('dish.id'), primary_key=True),
    Column('addon_id', Integer, ForeignKey('addons.id'), primary_key=True)
)
