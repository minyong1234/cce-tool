from sqlalchemy import Column, Integer, String, Text, Enum
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class ChecklistItem(Base):
    """
    점검 항목 테이블
    PDF 기준 문서의 각 점검 항목 하나가 row 하나에 해당
    """
    __tablename__ = "checklist_items"

    id          = Column(Integer, primary_key=True, index=True)
    code        = Column(String(50), unique=True, nullable=False)  # 예: U-01
    title       = Column(String(200), nullable=False)              # 항목명
    category    = Column(String(100), nullable=False)              # 분류
    description = Column(Text, nullable=True)                      # 점검 내용
    severity    = Column(
        Enum("상", "중", "하", name="severity_enum"),
        nullable=False
    )
    standard    = Column(
        Enum("기반시설", "클라우드", name="standard_enum"),
        nullable=False
    )
