from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json
import bcrypt

DATABASE_URL = "sqlite:///./game.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    wins = Column(Integer, default=0)
    hero_attack = Column(Integer, default=1)
    hero_buff = Column(Integer, default=0)

    currency_name = Column(String, nullable=True, default=None)
    currency_value = Column(Float, default=0.001)
    investor_trust = Column(Float, default=1.0)
    economy_data_json = Column(String, nullable=True, default=None)

Base.metadata.create_all(bind=engine)

def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain: str, hashed: str) -> bool:
    plain_bytes = plain.encode('utf-8')
    hashed_bytes = hashed.encode('utf-8')
    return bcrypt.checkpw(plain_bytes, hashed_bytes)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()