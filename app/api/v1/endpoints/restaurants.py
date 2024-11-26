from fastapi import APIRouter, Depends, status, Request, Body, UploadFile, Form, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated, Optional
from app.schemas.restaurant import (
    RestaurantCreate,
    RestaurantResponse, 
    RestaurantUpdate,
    BranchRestaurantCreate,
    RestaurantUserUpdate,
    RestaurantUserResponse,
    RestaurantImagesUpdate,
    RestaurantImagesRead,
    RestaurantAddressUpdate,
    RestaurantAddressRead,
    RestaurantSocialsRead,
    RestaurantSocialsUpdate,
    RestaurantOperationsTimeUpdate
)
from app.models.restaurant import RestaurantUser
from app.crud.restaurant import (
    create_restaurant,
    get_user_restaurant,
    get_restaurants,
    update_restaurant,
    delete_restaurant,
    create_branch,
    fetch_branch_restaurants,
    profile_update,
    upload_restaurant_image,
    update_restaurant_address,
    update_restaurant_socials,
    restaurant_operations_time,
    delete_operation_time
)
from app.db.session import get_db
from app.core.security import oauth2_scheme
from pydantic import EmailStr

router = APIRouter()

# Route to get all restaurants
@router.get("/fetch-restaurants", response_model=List[RestaurantResponse])
async def read_restaurants(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    restaurants = await get_restaurants(db, skip=skip, limit=limit)
    return restaurants

##############  Authorized routes  ##################
@router.post("/", response_model=RestaurantResponse, status_code=status.HTTP_201_CREATED)
async def create_new_restaurant(
    request: Request,
    restaurant: Annotated[RestaurantCreate, Body(embed=True)],
    authorize: RestaurantUser = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    db_restaurant = await create_restaurant(db, restaurant, user = request.user)
    return db_restaurant

@router.post("/update_operations_time", response_model=RestaurantResponse, status_code=status.HTTP_201_CREATED)
async def operations_time(
    request: Request,
    operations_time: Annotated[RestaurantOperationsTimeUpdate, Body(embed=True)],
    authorize: RestaurantUser = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    operations = await restaurant_operations_time(db, operations_time, user = request.user)
    return operations

@router.post("/delete_operations_time", response_model=RestaurantResponse, status_code=status.HTTP_201_CREATED)
async def operations_time_delete(
    id: int, 
    authorize: RestaurantUser = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    operation_time = await delete_operation_time(db, id)
    return operation_time

@router.put("/update-restaurant-address", response_model=RestaurantAddressRead)
async def restaurant_address(
    request: Request,
    restaurant_address: Annotated[RestaurantAddressUpdate, Body(embed=True)],
    authorize: RestaurantUser = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    result = await update_restaurant_address(db, restaurant_address, user = request.user)
    return result

@router.put("/update-restaurant-socials", response_model=RestaurantSocialsRead)
async def restaurant_socials(
    request: Request,
    restaurant_socials: Annotated[RestaurantSocialsUpdate, Body(embed=True)],
    authorize: RestaurantUser = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    result = await update_restaurant_socials(db, restaurant_socials, user = request.user)
    return result

@router.put("/upload_images", response_model=RestaurantImagesRead)
async def upload_logo_cover_photo(
    request: Request,
    authorize: RestaurantUser = Depends(oauth2_scheme),
    logo: Optional[UploadFile] = File(None),
    cover_photo: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    images = RestaurantImagesUpdate(
        logo=logo, 
        cover_photo=cover_photo
    )
    result = await upload_restaurant_image(db, images, user = request.user)
    return result

@router.put("/user-profile-update", response_model=RestaurantUserResponse)
async def user_update(
    request: Request,
    authorize: RestaurantUser = Depends(oauth2_scheme),
    email: Optional[EmailStr] = Form(None),
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    user_data = RestaurantUserUpdate(
        email=email, 
        first_name=first_name, 
        last_name=last_name, 
        image=image
    )
    result = await profile_update(db, user_data, user = request.user)
    return result

@router.get("/get-branch-restaurants")
async def branch_restaurants(
    request: Request,
    db: AsyncSession = Depends(get_db),
    authorize: RestaurantUser = Depends(oauth2_scheme),
):
    result = await fetch_branch_restaurants(db, user = request.user)
    return result

# Route to get a specific restaurant by ID
@router.get("/user-restaurant", response_model=RestaurantResponse)
async def read_restaurant(
    request: Request,
    authorize: RestaurantUser = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    restaurant = await get_user_restaurant(db, user = request.user)
    return restaurant

# Route to update an existing restaurant
@router.put("/update", response_model=RestaurantResponse)
async def update_existing_restaurant(
    request: Request,
    restaurant: Annotated[RestaurantUpdate, Body(embed=True)],
    authorize: RestaurantUser = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    
    db_restaurant = await update_restaurant(db, restaurant, user = request.user)
    return db_restaurant

# Route to delete a restaurant by ID
@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_restaurant(
    restaurant_id: int, 
    authorize: RestaurantUser = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    result = await delete_restaurant(db, restaurant_id=restaurant_id)
    return result

@router.post("/create-branch-restaurant", response_model=RestaurantResponse)
async def create_branch_restaurant(
    restaurant: Annotated[BranchRestaurantCreate, Body(embed=True)],
    request: Request,
    authorize: RestaurantUser = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    result = await create_branch(db, restaurant, user = request.user)
    return result


