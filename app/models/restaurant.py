from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func
from app.db.base import Base
from sqlalchemy.orm import relationship

class Restaurant(Base):
    __tablename__ = "restaurant"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    business_number = Column(String, nullable=False, unique=True)
    restaurant_name = Column(String, nullable=False, unique=True)
    url_slug = Column(String, nullable=False, unique=True)
    tagline = Column(String, nullable=False)
    is_branch = Column(Boolean, default=False)
    parent_restaurant_id = Column(Integer, ForeignKey('restaurant.id'), nullable=True)
    parent_restaurant = relationship('Restaurant', remote_side=[id], backref='branches')
    #location = Column(Geometry(geometry_type='POINT', srid=4326), nullable=True)
    contact_info = relationship('RestaurantContactInfo', uselist=False, back_populates='restaurant', cascade='all, delete-orphan')
    images = relationship('RestaurantImages', uselist=False, back_populates='restaurant', cascade='all, delete-orphan')
    address = relationship('RestaurantAddress', uselist=False, back_populates='restaurant', cascade='all, delete-orphan')
    socials = relationship('RestaurantSocials', uselist=False, back_populates='restaurant', cascade='all, delete-orphan')
    operations_time = relationship('RestaurantOperationsTime', back_populates='restaurant', cascade='all, delete-orphan')
    user = relationship('RestaurantUser', uselist=False, back_populates='restaurant', cascade='all, delete-orphan')
    dishes = relationship('Dish', back_populates='restaurant', cascade='all, delete-orphan')
    addons = relationship('Addons', back_populates='restaurant', cascade='all, delete-orphan')
    category = relationship('Category', back_populates='restaurant', cascade='all, delete-orphan')
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # from geoalchemy2.functions import ST_AsText
    # query location like so: session.query(ST_AsText(restaurant.location)).scalar()

from app.models.dish import Dish
from app.models.addons import Addons
from app.models.category import Category
    
class RestaurantUser(Base):
    __tablename__ = "restaurant_user"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'), nullable=True)
    email = Column(String, nullable=False, unique=True)
    image = Column(String, nullable=True)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    level = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    restaurant = relationship('Restaurant', back_populates='user', foreign_keys=[restaurant_id])
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
class RestaurantContactInfo(Base):
    __tablename__ = "restaurant_contact_info"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'), nullable=False)
    whatsapp = Column(String, nullable=True)
    landline = Column(String, nullable=True)
    mobile = Column(String, nullable=True)
    restaurant = relationship('Restaurant', back_populates='contact_info')
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
class RestaurantImages(Base):
    __tablename__ = "restaurant_images"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'), nullable=False)
    logo = Column(String, nullable=True)
    cover_photo = Column(String, nullable=True)
    restaurant = relationship('Restaurant', back_populates='images')
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
class RestaurantAddress(Base):
    __tablename__ = "restaurant_address"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'), nullable=False)
    address = Column(String, nullable=True)
    house_number = Column(String, nullable=True)
    block = Column(String, nullable=True)
    area = Column(String, nullable=True)
    city = Column(String, nullable=True)
    restaurant = relationship('Restaurant', back_populates='address')
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
class RestaurantSocials(Base):
    __tablename__ = "restaurant_socials"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'), nullable=False)
    instagram = Column(String, nullable=True)
    facebook = Column(String, nullable=True)
    tiktok = Column(String, nullable=True)
    snapchat = Column(String, nullable=True)
    youtube = Column(String, nullable=True)
    x = Column(String, nullable=True)
    restaurant = relationship('Restaurant', back_populates='socials')
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
class RestaurantOperationsTime(Base):
    __tablename__ = 'restaurant_operations_time'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    day = Column(String, nullable=False)
    open_time = Column(String, nullable=False)
    close_time = Column(String, nullable=False)
    priority=Column(Integer, nullable=False)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'), nullable=False)
    restaurant = relationship("Restaurant", back_populates="operations_time") #One-to-many relationship
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # operation_times = [
    #     OperationTime(day="Monday", open_time="09:00", close_time="18:00"),
    #     OperationTime(day="Tuesday", open_time="09:00", close_time="18:00"),
    #     # Add more days as needed
    # ]

    # restaurant.operation_times = operation_times
    #   session.add(restaurant)