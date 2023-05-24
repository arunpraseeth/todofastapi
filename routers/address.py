import sys

sys.path.append("..")
from typing import Optional, Annotated
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
import models
from database import sessionLocal
from .auth import get_current_user, user_exception

router = APIRouter(
    prefix='/address',
    tags=['address'],
    responses={404: {'Description': "Not found"}}
)


def get_db():
    try:
        db = sessionLocal()
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class Address(BaseModel):
    apt_num: Optional[int]
    address1: str
    address2: Optional[str]
    city: str
    state: str
    country: str
    postalcode: str


@router.post("/create")
async def create_address(address: Address, user: user_dependency, db: db_dependency):
    if user is None:
        raise user_exception()
    address_model = models.Address()
    address_model.apt_num = address.apt_num
    address_model.address1 = address.address1
    address_model.address2 = address.address2
    address_model.city = address.city
    address_model.state = address.state
    address_model.country = address.country
    address_model.postalcode = address.postalcode

    db.add(address_model)
    db.flush()

    user_model = db.query(models.Users).filter(models.Users.id == user.get("user_id")).first()

    user_model.address_id = address_model.id

    db.add(user_model)
    db.commit()

    return successful_code(status_code=201)


def successful_code(status_code: int):
    return {"status": status_code, "transaction": "Successful"}
