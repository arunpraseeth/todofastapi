
from typing import Optional, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from database import sessionLocal
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = "5c5ed31385e52016eb4f393f1eb417cabfa3d5008b7c7bf90a7a803dafbebd06"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


class CreateUser(BaseModel):
    username: str
    email: Optional[str]
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: Optional[str]


def get_db():
    try:
        db = sessionLocal()
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def hash_password(password):
    return bcrypt_context.hash(password)


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def create_access_token(username: str, user_id: int, user_role: str, expires_delta: Optional[timedelta] = None):
    encode = {"sub": username, "id": user_id, "role": user_role}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("id")
        user_role = payload.get('role')
        if username is not None or user_id is not None:
            return {"username": username, "user_id": user_id, "user_role": user_role}
        else:
            raise user_exception()
    except JWTError:
        print(JWTError)
        print("password wrong")
        raise token_expired()


@router.post("/create")
async def create_new_user(create_user: CreateUser, db: Session = Depends(get_db)):
    create_user_model = Users()
    create_user_model.username = create_user.username
    create_user_model.email = create_user.email
    create_user_model.first_name = create_user.first_name
    create_user_model.last_name = create_user.last_name
    create_user_model.role = create_user.role
    create_user_model.phone_number = create_user.phone_number
    hashed_password = hash_password(create_user.password)
    create_user_model.hashed_password = hashed_password

    db.add(create_user_model)
    db.commit()
    return {"message": "New user created"}


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not verify_password(plain_password=password, hashed_password=user.hashed_password):
        return False
    return user


@router.post("/token")
async def login_token(db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(username=form_data.username, password=form_data.password, db=db)

    if not user:
        raise token_exception()
    token_expire = timedelta(minutes=15)
    token = create_access_token(username=user.username, user_id=user.id, user_role=user.role, expires_delta=token_expire)
    return {"access_token": token, 'token_type': 'bearer'}


def token_expired():
    token_expired_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                            detail="Token expired, it expires for every 15 minutes",
                                            headers={"WWW-Authenticate": "Bearer"}
                                            )
    return token_expired_exception


def user_exception():
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                         detail="Could not validate credentials",
                                         headers={"WWW-Authenticate": "Bearer"}
                                         )
    return credential_exception


def token_exception():
    token_exception_response = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                             detail="Incorrect username or password",
                                             headers={"WWW-Authenticate": "Bearer"}
                                             )
    return token_exception_response
