# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuration for the remote MySQL server
MYSQL_USERNAME = "backend_user"           # Newly created MySQL user
MYSQL_PASSWORD = "secure_password"   
MYSQL_HOST = "10.3.32.11"      # Replace with your MySQL server's IP or domain
MYSQL_PORT = "3306"               # Default MySQL port
MYSQL_DATABASE = "todo_app"

# Construct the database URL
DATABASE_URL = f"mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

# Create the SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True  # Helps with handling dropped connections
)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our ORM models
Base = declarative_base()
