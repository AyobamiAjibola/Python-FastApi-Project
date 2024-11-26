from fastapi import APIRouter, Depends, status, Request, Body
from fastapi.security import OAuth2PasswordRequestForm
from app.crud.restaurant import (
    authenticate_user,
    create_restaurant_user,
    get_access_token
)
from app.schemas.restaurant import (
    RestaurantUserCreate, 
    RestaurantUserResponse
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.restaurant import RestaurantUser
from app.core.security import oauth2_scheme
from typing import Annotated

router = APIRouter()

@router.post("/register-user", response_model=RestaurantUserResponse, status_code=status.HTTP_201_CREATED)
async def create_restaurant_user_endpoint(
    restaurant_user: Annotated[RestaurantUserCreate, Body(embed=True)],
    db: AsyncSession = Depends(get_db)
):
    created_user = await create_restaurant_user(db, restaurant_user)
    return created_user

@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_db)
):
    token = await authenticate_user(db, form_data.password, email = form_data.username)
    return token

@router.post("/refresh-token", response_model=RestaurantUserResponse, status_code=status.HTTP_201_CREATED)
async def get_access_token_endpoint(token: str, db: AsyncSession = Depends(get_db)):
    refresh = await get_access_token(db, token)
    return refresh

@router.post('/me', status_code=status.HTTP_200_OK, response_model=RestaurantUserResponse)
def get_user_detail(request: Request, authorize: RestaurantUser = Depends(oauth2_scheme),):
    return request.user