from pydantic import BaseModel, SecretStr, EmailStr
from typing import Optional, List, Union
from datetime import datetime
from fastapi import Form, UploadFile

class RestaurantUserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    level: int
    is_active: bool = True
    password: Optional[SecretStr] = None
    image: str

class RestaurantUserCreate(BaseModel):
    password: str 
    first_name: str
    last_name: str
    email: EmailStr

class RestaurantUserUpdate(BaseModel):
    email: Optional[EmailStr]  = Form(None)
    first_name: Optional[str] = Form(None)
    last_name: Optional[str] = Form(None)
    image: Optional[UploadFile] = Form(None) 

    @classmethod
    def as_form(
        cls,
        email: Optional[EmailStr]  = Form(None),
        first_name: Optional[str] = Form(None),
        last_name: Optional[str] = Form(None),
        image: Optional[UploadFile] = None
    ) -> "RestaurantUserUpdate":
        return cls(email=email, first_name=first_name, last_name=last_name, image=image)

class RestaurantUserResponse(BaseModel):
    id: int
    restaurant_id: Optional[int] = None
    email: EmailStr
    first_name: str
    last_name: str
    # level: int
    is_active: bool = True
    image: str

    class Config:
        from_attributes = True
        
# RestaurantContactInfo Schema
class RestaurantContactInfoBase(BaseModel):
    whatsapp: Optional[str] = None
    landline: Optional[str] = None
    mobile: Optional[str] = None

class RestaurantContactInfoCreate(RestaurantContactInfoBase):
    restaurant_id: int
    
class RestaurantContactInfoUpdate(RestaurantContactInfoBase):
    restaurant_id: Optional[int] = None 

class RestaurantContactInfoRead(RestaurantContactInfoBase):
    id: int

    class Config:
        from_attributes = True


# RestaurantImages Schema
class RestaurantImagesBase(BaseModel):
    logo: Optional[str] = None
    cover_photo: Optional[str] = None

class RestaurantImagesUpdate(BaseModel):
    logo: Optional[UploadFile] = Form(None) 
    cover_photo: Optional[UploadFile] = Form(None) 
    
    @classmethod
    def as_form(
        cls,
        logo: Optional[UploadFile] = None,
        cover_photo: Optional[UploadFile] = None
    ) -> "RestaurantImagesUpdate":
        return cls(logo=logo, cover_photo=cover_photo)

class RestaurantImagesRead(RestaurantImagesBase):
    id: int

    class Config:
        from_attributes = True


# RestaurantAddress Schema
class RestaurantAddressBase(BaseModel):
    address: str
    house_number: Optional[str] = None
    block: Optional[str] = None
    area: Optional[str] = None
    city: str
    
class RestaurantAddressUpdate(RestaurantAddressBase):
    restaurant_id: Optional[int] = None

class RestaurantAddressRead(RestaurantAddressBase):
    id: int

    class Config:
        from_attributes = True


# RestaurantSocials Schema
class RestaurantSocialsBase(BaseModel):
    instagram: Optional[str] = None
    facebook: Optional[str] = None
    tiktok: Optional[str] = None
    snapchat: Optional[str] = None
    youtube: Optional[str] = None
    x: Optional[str] = None
    
class RestaurantSocialsUpdate(RestaurantSocialsBase):
    restaurant_id: Optional[int] = None

class RestaurantSocialsRead(RestaurantSocialsBase):
    id: int

    class Config:
        from_attributes = True


# RestaurantOperationsTime Schema
class RestaurantOperationsTimeBase(BaseModel):
    day: str
    open_time: str
    close_time: str
    priority: int

class RestaurantOperationsTimeCreate(RestaurantOperationsTimeBase):
    restaurant_id: int
    
class RestaurantOperationsTimeUpdate(RestaurantOperationsTimeBase):
    restaurant_id: Optional[int] = None

class RestaurantOperationsTimeRead(RestaurantOperationsTimeBase):
    id: int

    class Config:
        from_attributes = True


# Restaurant Schema
class RestaurantBase(BaseModel):
    business_number: str
    restaurant_name: str
    url_slug: str
    tagline: str
    is_branch: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class RestaurantCreate(BaseModel):
    business_number: str
    restaurant_name: str
    url_slug: str
    tagline: str
    
class BranchRestaurantCreate(BaseModel):
    business_number: str
    restaurant_name: str
    url_slug: str
    tagline: str
    is_branch: bool = True
    user_email: Optional[EmailStr] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
class RestaurantUpdate(BaseModel):
    business_number: str
    restaurant_name: str
    url_slug: str
    tagline: str
    
class RestaurantValidators(BaseModel):
    original_name: Optional[str] = None
    new_name: Optional[str] = None
    original_slug: Optional[str] = None
    new_slug: Optional[str] = None
    original_number: Optional[str] = None
    new_number: Optional[str] = None
    
class ParentRestaurantResponse(BaseModel):
    id: int
    business_number: str
    restaurant_name: str

class BranchUsers():
    email: EmailStr
    first_name: str
    last_name: str

class RestaurantResponse(RestaurantBase):
    id: int
    parent_restaurant_id: Optional[int] = None
    contact_info: Optional[RestaurantContactInfoRead] = None
    images: Optional[RestaurantImagesRead] = None
    address: Optional[RestaurantAddressRead] = None
    socials: Optional[RestaurantSocialsRead] = None
    operations_time: List[RestaurantOperationsTimeRead] = []
    parent_restaurant: Optional[ParentRestaurantResponse] = None

class RestaurantResponseWithBranches(RestaurantBase):
    id: int
    parent_restaurant_id: Optional[int] = None
    contact_info: Optional[RestaurantContactInfoRead] = None
    images: Optional[RestaurantImagesRead] = None
    address: Optional[RestaurantAddressRead] = None
    socials: Optional[RestaurantSocialsRead] = None
    operations_time: List[RestaurantOperationsTimeRead] = []
    parent_restaurant: Optional[ParentRestaurantResponse] = None
    

    class Config:
        from_attributes = True

    