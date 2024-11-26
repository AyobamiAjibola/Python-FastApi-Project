from fastapi import APIRouter, Depends
from app.api.v1.endpoints import restaurants, auth

api_v1_router = APIRouter()

api_v1_router.include_router(
    restaurants.router, 
    prefix="/restaurant", 
    tags=["Restaurants"],
    responses={404: {"description": "Not found"}},
)
#  dependencies=[Depends(oauth2_scheme)]
api_v1_router.include_router(
    auth.router, 
    prefix="/auth", 
    tags=["Auth"],
    responses={404: {"description": "Not found"}},
)