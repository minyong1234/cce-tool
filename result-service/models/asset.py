# models/asset.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Asset(Base):
    __tablename__ = "assets"

    id         = Column(Integer, primary_key=True, index=True)
    code       = Column(String(20), unique=True, nullable=False)
    hostname   = Column(String(200), nullable=False)
    ip         = Column(String(50), nullable=False)
    os         = Column(String(100), nullable=True)
    version    = Column(String(50), nullable=True)
    purpose    = Column(String(200), nullable=True)
    location   = Column(String(200), nullable=True)
    manager    = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)  # 등록일 추가
