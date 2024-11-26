from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from sqlalchemy.future import select
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
import os
from app.models.restaurant import RestaurantUser
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from typing import Annotated
from app.core.responses import TokenResponse
from app.models.user_token import UserToken
from starlette.authentication import AuthCredentials, UnauthenticatedUser
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)
    
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def verify_token(token: Annotated[str, Depends(oauth2_scheme)], db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, os.getenv("ACCESS_TOKEN_SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        userId: str = payload.get("id")
        if userId is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    result = await db.execute(select(RestaurantUser).filter(RestaurantUser.id == userId))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    return user

async def generate_jwt_token(db: AsyncSession, data: dict, refresh_token: str = None):
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid refresh token.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Define expiration times
    access_expire_time = datetime.now() + timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_TIME")))
    refresh_expire_time = datetime.now() + timedelta(minutes=int(os.getenv("REFRESH_TOKEN_EXPIRE_TIME")))
    
    # Generate tokens
    access_token = jwt.encode(
        {**data, "exp": access_expire_time}, 
        os.getenv("ACCESS_TOKEN_SECRET_KEY"), 
        algorithm=os.getenv("ALGORITHM")
    )
    
    result = await db.execute(select(UserToken).filter(UserToken.userId == data["id"]))
    user_token = result.scalars().first()
    
    if refresh_token:
        if user_token is None or user_token.refresh_token != refresh_token:
            raise credentials_exception
    else:
        if user_token is not None:
            await db.delete(user_token)
            await db.commit()
        
        refresh_token = jwt.encode(
            {**data, "exp": refresh_expire_time}, 
            os.getenv("REFRESH_TOKEN_SECRET_KEY"), 
            algorithm=os.getenv("ALGORITHM")
        )
            
        db_user_token = UserToken(
            userId=data["id"],
            refresh_token=refresh_token,
            expired_at=access_expire_time.timestamp()
        )

        db.add(db_user_token)
        
        await db.commit()
        await db.refresh(db_user_token)
        
    return TokenResponse (
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=int(access_expire_time.timestamp())
    )
    
async def verify_refresh_token(token: str, db: AsyncSession):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    exp_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Token is expired.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    REFRESH_TOKEN_SECRET_KEY = os.getenv("REFRESH_TOKEN_SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")

    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, REFRESH_TOKEN_SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("id")

        if not user_id:
            raise credentials_exception

        result = await db.execute(select(UserToken).filter(UserToken.userId == user_id))
        user = result.scalars().first()

        if user is None:
            raise credentials_exception

        current_date = int(datetime.now().timestamp())
        if user.expired_at < current_date:
            raise exp_exception
        
        data = { 
                "id": user.userId
            }
        token = await generate_jwt_token(db, data, refresh_token=token)

        return token

    except JWTError:
        raise credentials_exception

def get_token_payload(token):
   
    try:
        payload = jwt.decode(token, os.getenv("ACCESS_TOKEN_SECRET_KEY"), algorithms=os.getenv("ALGORITHM"))
    except JWTError:
        return None
    return payload    

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Optional[RestaurantUser]:
    async for db in get_db():
        payload = get_token_payload(token)
        
        if not payload or not isinstance(payload, dict):
            return None

        user_id = payload.get('id')
        if not user_id:
            return None

        dbase: AsyncSession = db

        # Await the execute coroutine
        result = await dbase.execute(select(RestaurantUser).filter(RestaurantUser.id == user_id))
        user = result.scalars().first()
        
        return user

class JWTAuth:
    async def authenticate(self, conn):
        guest = AuthCredentials(['unauthenticated']), UnauthenticatedUser()
        
        if 'authorization' not in conn.headers:
            return guest
        
        token = conn.headers.get('authorization').split(' ')[1]  # Bearer token_hash
       
        if not token:
            return guest
        
        user = await get_current_user(token=token)

        if not user:
            return guest
        
        return AuthCredentials('authenticated'), user
 