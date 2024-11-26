from contextlib import asynccontextmanager
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

@asynccontextmanager
async def TryExcept_context(db, check_email=False, original_email=None, new_email=None):
    try:
        yield
    except IntegrityError as e:
        await db.rollback()
        print(f"IntegrityError: {e.orig}")

        # Custom logic for 'email' field if enabled
        if check_email and 'email' in str(e.orig):
            if original_email and new_email and original_email != new_email:
                raise HTTPException(status_code=400, detail="A user with the provided email already exists.")
        
        raise HTTPException(status_code=400, detail="Database integrity error: Duplicate or invalid entry")
    except Exception as e:
        await db.rollback()
        print(f"Error: {e}")
        raise HTTPException(status_code=400, detail=f"{str(e)}")
