from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# notes for self: create_engine- creates connection to database
# declarative_base- helps create base classes
# sessionmaker- creaates database sessions (temp. workspaces for database)
# relationship- defines connections between different database models

database_url = "sqlite:///contracts.db"
engine = create_engine(database_url, connect_args={"check_same_thread": False})
# create connection to the database
# connect_args allows database to be accessed from multiple threads

session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# creates a session

Base = declarative_base()
# creates base class for all other (sqlalchemy) databases to inherit from and use as python classes

def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()
# creates a new session for each request
# try and finally makes sure that it's closed when finished
# yield enables it to be used and then automatically closed
# this is the function that will be called once a session is opened in FastAPI