from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.restaurant import (
    Restaurant, 
    RestaurantUser, 
    RestaurantImages, 
    RestaurantAddress,
    RestaurantSocials,
    RestaurantOperationsTime
)
from app.schemas.restaurant import (
    RestaurantCreate, 
    RestaurantUpdate, 
    RestaurantResponse, 
    RestaurantUserCreate, 
    BranchRestaurantCreate,
    RestaurantUserUpdate,
    RestaurantImagesUpdate,
    RestaurantAddressUpdate,
    RestaurantSocialsUpdate,
    RestaurantOperationsTimeUpdate
)
from sqlalchemy import or_
from sqlalchemy.future import select
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from app.core.security import (
    hash_password, 
    verify_password, 
    generate_jwt_token,
    verify_refresh_token
)
from app.utils.generic import sqlalchemy_to_dict, upload_image
from app.core.exception.context_manager import TryExcept_context
from app.core.exception.decorator_handle_exception import TryExcept

@TryExcept()
async def create_restaurant_user(db: AsyncSession, user: RestaurantUserCreate):
    
    existing_email = await db.execute(
        select(RestaurantUser).where(RestaurantUser.email == user.email)
    )
    if existing_email.scalars().first():
        raise HTTPException(status_code=400, detail="A user with email already exists")

    db_user = RestaurantUser(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        level=1,
        password=hash_password(user.password)
    )
    db.add(db_user)
    
    await db.commit()
    await db.refresh(db_user)
    
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Sign up was successful"}
    )

async def get_access_token(db: AsyncSession, token: str):
    token = await verify_refresh_token(token, db)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "access_token": token.access_token, 
            "refresh_token": token.refresh_token,
            "token_type": token.token_type,
            "expires_in": token.expires_in
        }
    )

@TryExcept()
async def authenticate_user(db: AsyncSession, password: str, email: str):
    result = await db.execute(
        select(RestaurantUser)
        .filter(RestaurantUser.email == email)
    )
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Email is not registered with us.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid Login Credentials.",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Your account is inactive. Please contact support.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    data = { 
            "id": user.id
        }
    token = await generate_jwt_token(db, data)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "access_token": token.access_token, 
            "refresh_token": token.refresh_token,
            "token_type": token.token_type,
            "expires_in": token.expires_in
        }
    )

@TryExcept()
async def get_restaurants(db: AsyncSession, skip: int = 0, limit: int = 10):
    result = await db.execute(
        select(Restaurant)
        .offset(skip)
        .limit(limit)
    )
    restaurants = result.scalars().all()

    validated_restaurants = []

    for restaurant in restaurants:
        parent_restaurant = None
        parent_payload: dict = {}

        # Check if restaurant has a parent restaurant
        if restaurant.parent_restaurant_id:
            parent_result = await db.execute(
                select(Restaurant).filter(Restaurant.id == restaurant.parent_restaurant_id)
            )
            parent_restaurant = parent_result.scalars().first()

        # If parent restaurant exists, prepare its payload
        if parent_restaurant:
            parent_payload = {
                "id": parent_restaurant.id,
                "business_number": parent_restaurant.business_number,
                "restaurant_name": parent_restaurant.restaurant_name
            }
        else:
            parent_payload = None

        restaurant_payload = sqlalchemy_to_dict(restaurant)
        
        restaurant_payload["parent_restaurant"] = parent_payload
        
        validated_restaurants.append(RestaurantResponse.model_validate(restaurant_payload))

    return validated_restaurants

@TryExcept()
async def get_user_restaurant(db: AsyncSession, user: RestaurantUser):
    
    if user.restaurant_id is None:
        raise HTTPException(status_code=404, detail="Logged in user is not assigned to a restaurant.")
    
    result = await db.execute(
        select(Restaurant)
        .options(
            selectinload(Restaurant.contact_info),
            selectinload(Restaurant.images),
            selectinload(Restaurant.address),
            selectinload(Restaurant.socials),
            selectinload(Restaurant.operations_time),
            selectinload(Restaurant.user)
        )
        .filter(Restaurant.id == user.restaurant_id)
    )
    restaurant = result.scalars().first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    parent_restaurant = None
    if restaurant.parent_restaurant_id:
        parent_result = await db.execute(
            select(Restaurant).filter(Restaurant.id == restaurant.parent_restaurant_id)
        )
        parent_restaurant = parent_result.scalars().first()

    parent_payload: dict = {}
    if parent_restaurant:
        parent_payload = {
            "id": parent_restaurant.id,
            "business_number": parent_restaurant.business_number,
            "restaurant_name": parent_restaurant.restaurant_name
        }
    else:
        parent_payload = None

    # Convert the restaurant to a dictionary
    restaurant_payload = sqlalchemy_to_dict(restaurant)
    
    # Include parent restaurant data in the response payload
    restaurant_payload["parent_restaurant"] = parent_payload

    # Return validated response
    return RestaurantResponse.model_validate(restaurant_payload)

@TryExcept()
async def create_restaurant(db: AsyncSession, restaurant: RestaurantCreate, user: RestaurantUser):
    
    if user.restaurant_id is not None:
        raise HTTPException(status_code=400, detail="The logged in user already have a restaurant assigned.")
    
    existing_restaurant = await db.execute(
        select(Restaurant).where(Restaurant.restaurant_name == restaurant.restaurant_name)
    )
    if existing_restaurant.scalars().first():
        raise HTTPException(status_code=400, detail="Restaurant name already exists")
    
    existing_restaurant_number = await db.execute(
        select(Restaurant).where(Restaurant.business_number == restaurant.business_number)
    )
    if existing_restaurant_number.scalars().first():
        raise HTTPException(status_code=400, detail="Restaurant with business number already exists")
    
    db_restaurant = Restaurant(
        **restaurant.model_dump()
    )
    db.add(db_restaurant)
    
    await db.commit()
    await db.refresh(db_restaurant)
    
    #update restaurant user
    restaurant_user = await db.execute(select(RestaurantUser).where(RestaurantUser.id == user.id))
    _user = restaurant_user.scalars().first()
    payload = {
        "restaurant_id": db_restaurant.id
    }
    for key, value in payload.items():
        setattr(_user, key, value)
        
    db.add(_user)    
    await db.commit()
    await db.refresh(_user)
    
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={ "message": "Restaurant created successfully" }
    )

@TryExcept()
async def update_restaurant(
    db: AsyncSession, 
    restaurant: RestaurantUpdate, 
    user: RestaurantUser
):

    if user.restaurant_id is None:
        raise HTTPException(status_code=404, detail="Logged in user is not assigned to a restaurant.")
    
    result = await db.execute(
            select(Restaurant)
            .filter(Restaurant.id == user.restaurant_id)
        )
    db_restaurant = result.scalars().first()
 
    if db_restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    result = await db.execute(
        select(Restaurant)
        .filter(
            or_(
                (Restaurant.restaurant_name == restaurant.restaurant_name),
                (Restaurant.url_slug == restaurant.url_slug),
                (Restaurant.business_number == restaurant.business_number)
            )
        )
    )
    existing_restaurant = result.scalars().first()

    if existing_restaurant and existing_restaurant.id != db_restaurant.id:
        if existing_restaurant.restaurant_name == restaurant.restaurant_name:
            raise HTTPException(status_code=400, detail="A restaurant with the provided name already exists.")
        if existing_restaurant.url_slug == restaurant.url_slug:
            raise HTTPException(status_code=400, detail="A restaurant with the provided URL slug already exists.")
        if existing_restaurant.business_number == restaurant.business_number:
            raise HTTPException(status_code=400, detail="A restaurant with the provided business number already exist.")
    
    for key, value in restaurant.model_dump(exclude_unset=True).items():
        setattr(db_restaurant, key, value)

    await db.commit()
    await db.refresh(db_restaurant)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Restaurant updated successfully"}
    )

@TryExcept()
async def create_branch(db: AsyncSession, restaurant: BranchRestaurantCreate, user: RestaurantUser):

    if user.restaurant_id is None:
        raise HTTPException(status_code=404, detail="This user is not a restaurant owner.")
    
    restaurant_result = await db.execute(
        select(Restaurant).filter(Restaurant.id == user.restaurant_id)
    )
    
    db_restaurant = restaurant_result.scalars().first()
    if db_restaurant is None:
        raise HTTPException(status_code=404, detail="User restaurant not found")
    
    if db_restaurant.parent_restaurant_id is not None:
        raise HTTPException(status_code=404, detail="User's restaurant is not a parent restaurant.")

    existing_restaurant = await db.execute(
        select(Restaurant).filter(
            (Restaurant.restaurant_name == restaurant.restaurant_name) |
            (Restaurant.business_number == restaurant.business_number)
        )
    )
    if existing_restaurant.scalars().first():
        raise HTTPException(status_code=400, detail="Restaurant name or business number already exists")
    
    new_db_restaurant_payload = restaurant.model_dump(exclude={"user_email"})
    
    new_db_restaurant = Restaurant(
        **new_db_restaurant_payload, 
        parent_restaurant_id=db_restaurant.id
    )
    db.add(new_db_restaurant)
    
    await db.commit()
    await db.refresh(new_db_restaurant) 
    
    branch_user = RestaurantUser(
        email=restaurant.model_dump()["user_email"],
        password=hash_password("Password12@"),
        restaurant_id=new_db_restaurant.id
    )
    db.add(branch_user)
    
    await db.commit()
    await db.refresh(branch_user)
    
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Branch restaurant created successfully"}
    )
   
@TryExcept()    
async def delete_restaurant(db: AsyncSession, restaurant_id: int):
    result = await db.execute(
        select(Restaurant)
        .filter(Restaurant.id == restaurant_id)
    )
    db_restaurant = result.scalars().first()
    
    if db_restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    await db.delete(db_restaurant)
    await db.commit()
    
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Restaurant deleted successfully"}
    )
    
@TryExcept()
async def fetch_branch_restaurants(db: AsyncSession, user: RestaurantUser):
    if user.restaurant_id is None:
        raise HTTPException(status_code=404, detail="This user is not a restaurant owner.")
    
    # Retrieve the parent restaurant associated with the user
    restaurant_result = await db.execute(
        select(Restaurant)
        .options(
            selectinload(Restaurant.branches)
        )
        .filter(Restaurant.id == user.restaurant_id)
    )
    db_restaurant = restaurant_result.scalars().first()
    
    if db_restaurant is None:
        raise HTTPException(status_code=404, detail="User's restaurant not found")

    if db_restaurant.parent_restaurant_id is not None:
        raise HTTPException(status_code=400, detail="User's restaurant is not a parent restaurant.")

    branch_restaurants = db_restaurant.branches
    
    branch_data = []
    for branch in branch_restaurants:
        result = await db.execute(
            select(Restaurant)
            .options(
                selectinload(Restaurant.contact_info),
                selectinload(Restaurant.images),
                selectinload(Restaurant.address),
                selectinload(Restaurant.socials),
                selectinload(Restaurant.operations_time),
                selectinload(Restaurant.user)
            )
            .filter(Restaurant.id == branch.id)
        )
        restaurant = result.scalars().first()
        
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        branch_dict = sqlalchemy_to_dict(restaurant)

        branch_data.append(branch_dict)

    return branch_data

async def profile_update(db: AsyncSession, user_data: RestaurantUserUpdate, user: RestaurantUser):
    user_info = await db.execute(
        select(RestaurantUser).filter(RestaurantUser.id == user.id)
    )
    db_user = user_info.scalars().first()
    
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist.")

    original_email = db_user.email
    new_email = user_data.email 
    
    if user_data.image:
        image_path = upload_image(file = user_data.image)
            
        db_user.image = str(image_path)

    # Dynamically update other fields if provided
    updatable_fields = ["email", "first_name", "last_name"]
    for field in updatable_fields:
        value = getattr(user_data, field, None)
        if value is not None:
            setattr(db_user, field, value)

    async with TryExcept_context(db, check_email=True, original_email=original_email, new_email=new_email):
        await db.commit()
        await db.refresh(db_user)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Profile updated successfully"}
        )
    
async def upload_restaurant_image(db: AsyncSession, images: RestaurantImagesUpdate, user: RestaurantUser):
    restaurant_image_info = await db.execute(
        select(RestaurantImages)
        .filter(RestaurantImages.restaurant_id == user.restaurant_id)
    )
    db_image_restaurant = restaurant_image_info.scalars().first()
    
    async with TryExcept_context(db):
        
        if db_image_restaurant is None:
            new_db_restaurant_image = RestaurantImages(
                restaurant_id=user.restaurant_id,
                logo=upload_image(file=images.logo) if images.logo else None,
                cover_photo=upload_image(file=images.cover_photo) if images.cover_photo else None
            )
            db.add(new_db_restaurant_image)
            await db.commit()
            await db.refresh(new_db_restaurant_image)
            
        else:
            if db_image_restaurant.logo:
                logo_path = upload_image(file = images.logo)
                    
                db_image_restaurant.logo = str(logo_path)
            
            if images.cover_photo:
                cover_photo_path = upload_image(file = images.cover_photo)
                
                db_image_restaurant.cover_photo = str(cover_photo_path)
        
            await db.commit()
            await db.refresh(db_image_restaurant)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Image uploaded successfully"}
        )

@TryExcept()     
async def update_restaurant_address(db: AsyncSession, restaurant_address: RestaurantAddressUpdate, user: RestaurantUser):
    restaurant_address_info = await db.execute(
        select(RestaurantAddress)
        .filter(RestaurantAddress.restaurant_id == user.restaurant_id)
    )
    db_address_restaurant = restaurant_address_info.scalars().first()

    if db_address_restaurant is None:
        new_db_restaurant_address = RestaurantAddress(
            restaurant_id=user.restaurant_id,
            **restaurant_address.model_dump(exclude_unset=True)
        )
        db.add(new_db_restaurant_address)
        
        await db.commit()
        await db.refresh(new_db_restaurant_address)
        
    else:
        for key, value in restaurant_address.model_dump(exclude_unset=True).items():
            setattr(db_address_restaurant, key, value)

        await db.commit()
        await db.refresh(db_address_restaurant)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Successful"}
    )
        
@TryExcept()
async def update_restaurant_socials(db: AsyncSession, restaurant_socials: RestaurantSocialsUpdate, user: RestaurantUser):
    restaurant_socials_info = await db.execute(
        select(RestaurantSocials)
        .filter(RestaurantSocials.restaurant_id == user.restaurant_id)
    )
    db_socials_restaurant = restaurant_socials_info.scalars().first()
    
    if db_socials_restaurant is None:
        new_db_restaurant_socials = RestaurantSocials(
            restaurant_id=user.restaurant_id,
            **restaurant_socials.model_dump(exclude_unset=True)
        )
        db.add(new_db_restaurant_socials)
        
        await db.commit()
        await db.refresh(new_db_restaurant_socials)
        
    else:
        for key, value in restaurant_socials.model_dump(exclude_unset=True).items():
            setattr(db_socials_restaurant, key, value)

        await db.commit()
        await db.refresh(db_socials_restaurant)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Successful"}
    )

@TryExcept()        
async def restaurant_operations_time(
    db: AsyncSession, 
    operations_time: RestaurantOperationsTimeUpdate, 
    user: RestaurantUser
):
    restaurant_operation_info = await db.execute(
        select(RestaurantOperationsTime)
        .filter(RestaurantOperationsTime.restaurant_id == user.restaurant_id)
    )
    db_operation_time_restaurant = restaurant_operation_info.scalars().first()
    
    if db_operation_time_restaurant is None:
        new_db_restaurant_operation = RestaurantOperationsTime(
            restaurant_id=user.restaurant_id,
            **operations_time.model_dump(exclude_unset=True)
        )
        db.add(new_db_restaurant_operation)
        
        await db.commit()
        await db.refresh(new_db_restaurant_operation)
        
    else:
        for key, value in operations_time.model_dump(exclude_unset=True).items():
            setattr(db_operation_time_restaurant, key, value)

        await db.commit()
        await db.refresh(db_operation_time_restaurant)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Successful"}
    )

@TryExcept()
async def delete_operation_time(db: AsyncSession, id: int):
    result = await db.execute(
        select(RestaurantOperationsTime)
        .filter(RestaurantOperationsTime.id == id)
    )
    db_restaurant_operation_time = result.scalars().first()
    
    if db_restaurant_operation_time is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    await db.delete(db_restaurant_operation_time)
    await db.commit()
    
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Deleted successfully"}
    )
    