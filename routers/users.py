from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from models import Users
from database import sessionLocal
from .auth import get_current_user, user_exception

router = APIRouter(
    prefix='/users',
    tags=['users']
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    try:
        db = sessionLocal()
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


def hash_password(password):
    return bcrypt_context.hash(password)


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=5)


@router.get('/get_user', status_code=status.HTTP_200_OK)
async def admin_read_all(user: user_dependency, db: db_dependency):
    if user is not None:
        user_model = db.query(Users).filter(Users.id == user.get('user_id')).first()
        var = {"email": user_model.email}
        return var
    raise user_exception()


@router.put('/change_password', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    if user is None:
        raise user_exception()
    user_model = db.query(Users).filter(Users.id == user.get('user_id')).first()
    if user_model is None:
        raise http_exception()
    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail="Your existing password is wrong")

    hashed_password = hash_password(user_verification.new_password)
    user_model.hashed_password = hashed_password

    db.add(user_model)
    db.commit()

    return successful_code(status_code=200)


def successful_code(status_code: int):
    return {"status": status_code, "transaction": "Successful"}


def http_exception():
    return HTTPException(status_code=404, detail="Item not found")
