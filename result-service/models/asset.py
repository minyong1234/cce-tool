# models/asset.py
# 점검 대상 자산 정보 (Excel 자산목록 시트에 해당)

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Asset(Base):
    """
    점검 대상 자산 테이블
    Excel의 자산목록 시트 한 행 = DB의 한 row
    """
    __tablename__ = "assets"

    id       = Column(Integer, primary_key=True, index=True)
    code     = Column(String(20), unique=True, nullable=False)  # U_001, U_002 ...
    hostname = Column(String(200), nullable=False)               # 호스트명
    ip       = Column(String(50), nullable=False)                # IP 주소
    os       = Column(String(100), nullable=True)                # 운영체제
    version  = Column(String(50), nullable=True)                 # OS 버전
    purpose  = Column(String(200), nullable=True)                # 자산명/용도
    location = Column(String(200), nullable=True)                # 설치위치
    manager  = Column(String(100), nullable=True)                # 담당자
