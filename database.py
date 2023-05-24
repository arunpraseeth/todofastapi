from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# ONLY FOR SQLITE3 DATABASE:
# SQLALCHEMY_DATABASE_URL = "sqlite:///./todosapp.db"
# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})


# ONLY FOR POSTGRESQL DATABASE
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:test1234!@localhost/TodoApplicationDatabase"


# ONLY FOR MYSQL DATABASE
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:TRAVELWITHME@127.0.0.1:3306/TodoApplicationDatabase"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

# to maintain a database session
sessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

# to create database model
Base = declarative_base()
