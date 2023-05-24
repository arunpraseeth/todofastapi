from typing import Optional, Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from models import Todos, Users
from database import sessionLocal
from .auth import get_current_user, user_exception

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)


def get_db():
    try:
        db = sessionLocal()
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get('/todos', status_code=status.HTTP_200_OK)
async def admin_read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get('user_role') != 'CEO':
        raise user_exception()
    todo_model = db.query(Todos).all()
    return todo_model


@router.delete('/todos/delete/{todo_id}', status_code=status.HTTP_200_OK)
async def admin_delete(user: user_dependency, db: db_dependency, todo_id: int):
    if user is None or user.get('user_role') != 'CEO':
        raise user_exception()
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('user_id')).first()
    if todo_model is not None:
        db.delete(todo_model)
        db.commit()
        return successful_code()
    else:
        raise http_exception()


@router.get('/all_info', status_code=status.HTTP_200_OK)
async def admin_read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise user_exception()
    todo_model = db.query(Users).all()
    return todo_model


def successful_code(status_code: int):
    return {"status": status_code, "transaction": "Successful"}


def http_exception():
    return HTTPException(status_code=404, detail="Item not found")
