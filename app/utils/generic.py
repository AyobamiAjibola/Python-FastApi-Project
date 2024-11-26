from sqlalchemy.inspection import inspect
import shutil
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.utils.constant import image_types, max_image_size
import uuid

def sqlalchemy_to_dict(instance):
    return {column.name: getattr(instance, column.name) for column in instance.__table__.columns}

def upload_image(file: UploadFile):
    
    if file.size > max_image_size():
        raise HTTPException(status_code=400, detail="Image size exceeds the maximum allowed size of 5MB.")

    if not any(file.filename.endswith(ext) for ext in image_types()):
        raise HTTPException(status_code=400, detail="Invalid image type. Only image files are allowed.")
    
    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    image_dir = Path("static/uploads")
    image_path = image_dir / unique_filename

    image_dir.mkdir(parents=True, exist_ok=True)

    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return str(image_path)

def sqlalchemy_to_dict2(obj, recursive=False):
    if not obj:
        return None

    # Extract the column attributes
    data = {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}

    # If recursive is True, include relationships
    if recursive:
        for key, rel in inspect(obj).mapper.relationships.items():
            related_obj = getattr(obj, key)
            if related_obj:
                if rel.uselist:
                    # If it's a list, process each item recursively
                    data[key] = [sqlalchemy_to_dict2(child, recursive=True) for child in related_obj]
                else:
                    # Otherwise, process the related object recursively
                    data[key] = sqlalchemy_to_dict2(related_obj, recursive=True)

    return data
