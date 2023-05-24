from typing import Optional, Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Request
from starlette import status
from models import Todos
from database import sessionLocal
from .auth import get_current_user, user_exception
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix='/todo',
    tags=['todo']
)


templates = Jinja2Templates(directory="templates")


def get_db():
    try:
        db = sessionLocal()
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class Todo(BaseModel):
    title: str
    description: Optional[str]
    priority: int = Field(gt=0, lt=6, description="The priority must be between 1 to 5")
    complete: bool = Field(default=False)


@router.get("/test")
async def test(request: Request):
    print(f"req {request}")
    return templates.TemplateResponse("home.html", {"request": request})


@router.get('/read')
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise user_exception()
    else:
        print(f'user id: {user.get("user_id")}')
        user_value = db.query(Todos).filter(Todos.owner_id == user.get("user_id")).all()
        print(user_value)
        return user_value


@router.get('/{todo_id}')
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int):
    if user is None:
        raise user_exception()
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("user_id")).first()
    if todo_model is not None:
        return todo_model
    else:
        raise http_exception()


@router.post('/add')
async def create_todo(user: user_dependency, db: db_dependency, todo: Todo):
    if user is None:
        raise user_exception()
    todo_model = Todos(**todo.dict(), owner_id=user.get('user_id'))

    db.add(todo_model)
    db.commit()

    return successful_code(status_code=201)


@router.put('/update/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, todo_id: int, todo: Todo):
    if user is None:
        raise user_exception()
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('user_id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete

    db.add(todo_model)
    db.commit()

    return successful_code(status_code=200)


@router.delete('/delete/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int):
    if user is None:
        raise user_exception()
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('user_id')).first()
    if todo_model is not None:
        db.delete(todo_model)
        db.commit()
        return successful_code(status_code=201)
    else:
        raise http_exception()


def successful_code(status_code: int):
    return {"status": status_code, "transaction": "Successful"}


def http_exception():
    return HTTPException(status_code=404, detail="Item not found")
