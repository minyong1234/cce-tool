# models/scan_result.py
# 점검 결과 테이블 (Excel U_001~ 시트에 해당)

from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from models.asset import Base

class ScanResult(Base):
    """
    점검 결과 테이블
    자산(Asset) 하나당 점검 항목 수만큼 row가 생성됨
    예: 자산 1개 × 항목 36개 = 36개 row
    """
    __tablename__ = "scan_results"

    id             = Column(Integer, primary_key=True, index=True)
    asset_id       = Column(Integer, ForeignKey("assets.id"), nullable=False)
    checklist_code = Column(String(50), nullable=False)   # U-01, U-02 ...
    result         = Column(
        Enum("Y", "N", "N/A", name="result_enum"),
        nullable=False
    )                                                     # Y=양호, N=취약, N/A=해당없음
    current_status = Column(Text, nullable=True)          # 현황 (점검 명령어 결과)
    improvement    = Column(Text, nullable=True)          # 개선방안
    score_total    = Column(Integer, nullable=True)       # 전체점수
    score_eval     = Column(Integer, nullable=True)       # 평가점수

    # Asset과의 관계 설정 (asset.scan_results로 역참조 가능)
    asset = relationship("Asset", backref="scan_results")
