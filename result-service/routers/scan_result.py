# routers/scan_result.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from models.scan_result import ScanResult
from database import get_db

router = APIRouter()

class ScanResultCreate(BaseModel):
    asset_id:       int
    checklist_code: str
    result:         str
    current_status: Optional[str] = None
    improvement:    Optional[str] = None
    score_total:    Optional[int] = None
    score_eval:     Optional[int] = None

class ScanResultResponse(BaseModel):
    id:             int
    asset_id:       int
    checklist_code: str
    result:         str
    current_status: Optional[str]
    improvement:    Optional[str]
    score_total:    Optional[int]
    score_eval:     Optional[int]

    class Config:
        from_attributes = True

@router.get("/", response_model=list[ScanResultResponse])
def get_all_results(db: Session = Depends(get_db)):
    return db.query(ScanResult).all()

@router.get("/asset/{asset_id}", response_model=list[ScanResultResponse])
def get_results_by_asset(asset_id: int, db: Session = Depends(get_db)):
    return db.query(ScanResult).filter(ScanResult.asset_id == asset_id).all()

@router.post("/", response_model=ScanResultResponse, status_code=201)
def create_result(data: ScanResultCreate, db: Session = Depends(get_db)):
    result = ScanResult(**data.model_dump())
    db.add(result)
    db.commit()
    db.refresh(result)
    return result

# ↓ 신규 추가 — 자산별 전체 점검 결과 삭제
@router.delete("/asset/{asset_id}", status_code=204)
def delete_results_by_asset(asset_id: int, db: Session = Depends(get_db)):
    deleted = db.query(ScanResult).filter(ScanResult.asset_id == asset_id).delete()
    if deleted == 0:
        raise HTTPException(status_code=404, detail="해당 자산의 점검 결과가 없습니다")
    db.commit()

@router.delete("/{result_id}", status_code=204)
def delete_result(result_id: int, db: Session = Depends(get_db)):
    result = db.query(ScanResult).filter(ScanResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="결과를 찾을 수 없습니다")
    db.delete(result)
    db.commit()

@router.put("/{result_id}", response_model=ScanResultResponse)
def update_result(result_id: int, data: ScanResultCreate, db: Session = Depends(get_db)):
    result = db.query(ScanResult).filter(ScanResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="결과를 찾을 수 없습니다")
    for key, value in data.model_dump().items():
        setattr(result, key, value)
    db.commit()
    db.refresh(result)
    return result
