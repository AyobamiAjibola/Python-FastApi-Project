from app.core.exception.decorator_handle_exception import TryExcept
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.restaurant import RestaurantUser, Restaurant
from app.models.dish import Dish
from app.models.category import Category
from app.schemas.dish import (
    CreateDish,
    UpdateDish
)
from sqlalchemy.future import select
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from app.utils.generic import upload_image
from sqlalchemy.orm import selectinload

async def check_user(db: AsyncSession, id: int):
    user_info = await db.execute(
        select(RestaurantUser).filter(RestaurantUser.id == id)
    )
     
    db_user = user_info.scalars().first()
    
    return db_user

@TryExcept()
async def create_dish(db: AsyncSession, dish: CreateDish, user: RestaurantUser):
     
    db_user = await check_user(db, id=user.id)
    
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist.")
    
    result = await db.execute(
        select(Dish).filter(
            Dish.restaurant_id == user.restaurant_id,
            Dish.name == dish.name
        )
    )
    
    exist_dish = result.scalars().first()
    
    if exist_dish:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A dish already exist with the provided dish name.")
    
    category_ = await db.execute(
        select(Category).filter(Category.id == dish.category_id)
    )
    
    category = category_.scalars().first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category does not exist.")
    
    image_uri = None
    if dish.image:
        image_path = upload_image(file=dish.image)
        image_uri = str(image_path)
        
    payload = Dish(
        restaurant_id=user.restaurant_id,
        image=image_uri,
        **dish.model_dump(exclude=None)
    )
    
    db.add(payload) 
    await db.commit()
    await db.refresh(payload)
    
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Dish created successfully"}
    )
    
@TryExcept
async def fetch_restaurant_dishes(db: AsyncSession, slug: str, skip: int = 0, limit: int = 10):
    
    result = await db.execute(
        select(Restaurant).filter(Restaurant.url_slug == slug)
    )
    
    restaurant = result.scalars().first()
    
    if restaurant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Restaurant not found."
        )
        
    result = await db.execute(
        select(Dish)
        .options(
            selectinload(Dish.addons),
            selectinload(Dish.category),
            selectinload(Dish.restaurant)
        )
        .filter(Dish.restaurant_id == restaurant.id)
        .offset(skip)
        .limit(limit)
    )
    
    dishes = result.scalars().all()
    
    if not dishes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No dishes found for this restaurant."
        )
    
    return dishes

@TryExcept
async def get_single_dish(db: AsyncSession, dish_id: int):
    
    result = await db.execute(
        select(Dish)
        .options(
            selectinload(Dish.addons),
            selectinload(Dish.category),
            selectinload(Dish.restaurant)
        )
        .filter(Dish.id == dish_id)
    )
    
    dish = result.scalars().first()
    
    if dish is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Dish does not exist."
        )
        
    return dish

@TryExcept
async def update_dish(db: AsyncSession, dish_id: int, dish: UpdateDish, user: RestaurantUser):
    
    db_user = await check_user(db, id=user.id)
    
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist.")
    
    result = await db.execute(
        select(Dish)
        .filter(Dish.id == dish_id)
    )
    
    db_dish = result.scalars().first()
    
    if db_dish is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Dish does not exist."
        )
        
    result = await db.execute(
        select(Dish)
        .filter(
            (Dish.name == dish.name)
        )
    )
    existing_dish = result.scalars().first()

    if existing_dish and existing_dish.id != db_dish.id:
        if existing_dish.name == dish.name:
            raise HTTPException(status_code=400, detail="A dish with the provided name already exists.")
  
    if dish.image:
        image_path = upload_image(file=dish.image)
        db_dish = str(image_path)
        
    updatable_fields = [
        "name", "price", 
        "discount", "description", 
        "spice_level", "hot_seller",
        "category_id", "sub_category"
    ]
    
    for field in updatable_fields:
        value = getattr(dish, field, None)
        if value is not None:
            setattr(dish, field, value)
            
    await db.commit()
    await db.refresh(existing_dish) 
        
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Dish updated successfully"}
    )

@TryExcept()    
async def delete_dish(db: AsyncSession, dish_id: int, user: RestaurantUser):
    
    db_user = await check_user(db, id=user.id)
    
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist.")
    
    result = await db.execute(
        select(Dish)
        .filter(Dish.id == dish_id)
    )
    db_dish = result.scalars().first()
    
    if db_dish is None:
        raise HTTPException(status_code=404, detail="Dish not found")
    
    await db.delete(db_dish)
    await db.commit()
    
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Dish deleted successfully"}
    )