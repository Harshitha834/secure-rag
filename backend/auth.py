from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import bcrypt
import os
from dotenv import load_dotenv
from sqlalchemy import Integer, LargeBinary, create_engine, Column, String
from sqlalchemy.orm import declarative_base,sessionmaker

db_url = os.getenv("DATABASE_URL", "sqlite:///./users.db")
engine = create_engine(db_url)

Base = declarative_base()

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY","fallback-only-for-dev")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def _hash(pw: str) -> bytes:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt())

def verify_password(plain: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(LargeBinary)
    role = Column(String)

Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

def register_user(username: str, password: str, role: str) -> dict:
    if session.query(User).filter_by(username=username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_pw = _hash(password)
    user = User(username=username, password=hashed_pw, role=role)
    session.add(user)
    session.commit()
    return {"username": username, "role": role}

def authenticate_user(username: str, password: str) -> Optional[dict]:
    user = session.query(User).filter_by(username=username).first()
    if not user or not verify_password(password, user.password):
        return None
    return {"username": user.username, "role": user.role}

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = session.query(User).filter_by(username=username).first()
    if user is None:
        raise credentials_exception
    return {"username": username, "role": role}