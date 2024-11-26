from functools import wraps
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
import inspect

# def TryExcept(
#     check_email=False,
#     check_restaurant_name=False,
#     check_slug=False,
#     check_biz_no=False
# ):
#     def decorator(func):
#         @wraps(func)
#         async def wrapper(*args, **kwargs):
#             # Get the signature of the decorated function
#             func_signature = inspect.signature(func)
#             bound_args = func_signature.bind(*args, **kwargs)
#             bound_args.apply_defaults()  # Apply default values to missing args
#             arguments = bound_args.arguments

#             try:
#                 return await func(*args, **kwargs)
#             except IntegrityError as e:
#                 db = arguments.get('db')
#                 await db.rollback()
#                 print(f"IntegrityError: {e.orig}")

#                 # Check email duplication logic
#                 if check_email and 'email' in str(e.orig):
#                     original_email = arguments.get('original_email')
#                     new_email = arguments.get('new_email')
#                     if original_email != new_email:
#                         raise HTTPException(status_code=400, detail="A user with the provided email already exists.")

#                 # Check restaurant name duplication logic
#                 if check_restaurant_name and 'restaurant_name' in str(e.orig):
#                     original_name = arguments.get('original_name')
#                     new_name = arguments.get('new_name')
#                     if original_name != new_name:
#                         raise HTTPException(status_code=400, detail="A restaurant with the provided name already exist.")

#                 # Check slug duplication logic
#                 if check_slug and 'urlSlug' in str(e.orig):
#                     original_slug = arguments.get('original_slug')
#                     new_slug = arguments.get('new_slug')
#                     if original_slug != new_slug:
#                         raise HTTPException(status_code=400, detail="A restaurant with the provided url slug already exist.")

#                 # Check business number duplication logic
#                 if check_biz_no and 'business_number' in str(e.orig):
#                     original_number = arguments.get('original_number')
#                     new_number = arguments.get('new_number')
#                     if original_number != new_number:
#                         raise HTTPException(status_code=400, detail="A restaurant with the provided business number already exist.")

#                 raise HTTPException(status_code=400, detail="Database integrity error: Duplicate or invalid entry")
#             except Exception as e:
#                 db = arguments.get('db')
#                 await db.rollback()
#                 print(f"Error: {e}")
#                 raise HTTPException(status_code=400, detail=f"{str(e)}")
#         return wrapper
#     return decorator

def TryExcept():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except IntegrityError as e:
                db = kwargs.get('db') or args[0]  # Assuming `db` is the first argument or in kwargs
                await db.rollback()
                print(f"IntegrityError: {e.orig}")

                raise HTTPException(status_code=400, detail="Database integrity error: Duplicate or invalid entry")
            except Exception as e:
                db = kwargs.get('db') or args[0]  # Assuming `db` is the first argument or in kwargs
                await db.rollback()
                print(f"Error: {e}")
                raise HTTPException(status_code=400, detail=f"{str(e)}")
        return wrapper
    return decorator
