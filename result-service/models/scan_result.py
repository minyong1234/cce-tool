# models/scan_result.py

from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from models.asset import Base

class ScanResult(Base):
    __tablename__ = "scan_results"

    id             = Column(Integer, primary_key=True, index=True)
    asset_id       = Column(Integer, ForeignKey("assets.id"), nullable=False)
    checklist_code = Column(String(50), nullable=False)
    result         = Column(
        Enum("Y", "N", "N/A", "PENDING", name="result_enum"),  # ← PENDING 추가
        nullable=False
    )
    current_status = Column(Text, nullable=True)   # 명령어 실행 결과값
    improvement    = Column(Text, nullable=True)   # 개선방안
    score_total    = Column(Integer, nullable=True)
    score_eval     = Column(Integer, nullable=True)

    asset = relationship("Asset", backref="scan_results")
