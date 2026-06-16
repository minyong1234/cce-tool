# models/scan_result.py
from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from models.asset import Base

class ScanResult(Base):
    __tablename__ = "scan_results"

    id             = Column(Integer, primary_key=True, index=True)
    asset_id       = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)  # CASCADE 추가
    checklist_code = Column(String(50), nullable=False)
    result         = Column(
        Enum("Y", "N", "N/A", "PENDING", name="result_enum"),
        nullable=False
    )
    current_status = Column(Text, nullable=True)
    improvement    = Column(Text, nullable=True)
    score_total    = Column(Integer, nullable=True)
    score_eval     = Column(Integer, nullable=True)

    asset = relationship("Asset", backref="scan_results", passive_deletes=True)  # passive_deletes 추가
