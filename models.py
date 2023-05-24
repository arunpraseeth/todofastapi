from sqlalchemy import Boolean, Column, String, Integer, ForeignKey
from sqlalchemy.orm import Relationship
from database import Base


class Users(Base):
    # creating a table name
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)
    phone_number = Column(String)
    address_id = Column(Integer, ForeignKey("address.id"), nullable=True)

    todos = Relationship("Todos", back_populates="owner")
    address = Relationship("Address", back_populates="user_address")


class Todos(Base):
    # creating a table name
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = Relationship("Users", back_populates="todos")


class Address(Base):
    __tablename__ = "address"

    id = Column(Integer, primary_key=True, index=True)
    apt_num = Column(Integer)
    address1 = Column(String)
    address2 = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    postalcode = Column(String)

    user_address = Relationship("Users", back_populates="address")
