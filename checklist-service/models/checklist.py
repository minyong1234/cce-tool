from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class ChecklistItem(Base):
    __tablename__ = "checklist_items"

    id           = Column(Integer, primary_key=True, index=True)
    code         = Column(String(50), unique=True, nullable=False)
    title        = Column(String(200), nullable=False)
    category     = Column(String(100), nullable=False)
    severity     = Column(Enum("상", "중", "하", name="severity_enum"), nullable=False)
    standard     = Column(Enum("기반시설", "클라우드", name="standard_enum"), nullable=False)
    target       = Column(String(100), nullable=False)
    check_method = Column(                            # ← 추가
        Enum("auto", "interview", name="check_method_enum"),
        nullable=False,
        default="interview"
    )
