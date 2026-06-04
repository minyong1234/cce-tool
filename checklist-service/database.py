# database.py
# DB 연결 관련 코드를 main.py에서 분리
# 다른 파일에서 순환 참조 없이 가져올 수 있음

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://cce_user:cce_password@localhost:5432/cce_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
