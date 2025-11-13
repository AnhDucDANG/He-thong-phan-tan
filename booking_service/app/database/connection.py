import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Tạo engine từ URL trong settings
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
)

# Session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

# Declarative base cho models
Base = declarative_base()


def get_db():
    """Dependency: yield db session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Tạo các bảng (Base.metadata.create_all)"""
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Warning: Could not create tables: {e}")