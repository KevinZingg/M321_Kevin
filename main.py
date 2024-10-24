# main.py
import logging
from datetime import timedelta

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jose import JWTError
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from database import SessionLocal, engine, Base
import auth
import models
import schemas
import os
from dotenv import load_dotenv

load_dotenv()


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up the Jinja2 templates directory
templates = Jinja2Templates(directory="templates")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Dependency to get DB session
def get_db():
    try:
        db = SessionLocal()
        yield db
    except OperationalError:
        logger.error("Database connection failed.")
        raise HTTPException(status_code=503, detail="Database is unavailable")
    finally:
        try:
            db.close()
        except:
            pass


# Utility function to get user by username
def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


# Authenticate user
def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not auth.verify_password(password, user.password_hash):
        return False
    return user


# Get current user dependency
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


# Registration endpoint
@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_email = db.query(models.User).filter(models.User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(
        username=user.username,
        password_hash=hashed_password,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name
    )
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
    except OperationalError:
        logger.error("Failed to commit new user to the database.")
        raise HTTPException(status_code=503, detail="Database is unavailable")
    return new_user


# Token endpoint
@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    # Update last_login
    user.last_login = func.now()
    try:
        db.commit()
    except OperationalError:
        logger.error("Failed to update last_login due to database unavailability.")
        raise HTTPException(status_code=503, detail="Database is unavailable")
    return {"access_token": access_token, "token_type": "bearer"}


# Protected route example
@app.get("/users/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    return {"status": "ok"}


# Home route
@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Startup event to create tables
@app.on_event("startup")
def startup_event():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")
    except OperationalError:
        logger.error("Could not connect to the database. Tables were not created.")


# Optional: Global exception handler for database errors
@app.exception_handler(OperationalError)
async def db_exception_handler(request: Request, exc: OperationalError):
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=503,
        content={"detail": "Database is unavailable"},
    )
