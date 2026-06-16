# routers/checklist.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from models.checklist import ChecklistItem
from database import get_db

router = APIRouter()

class ChecklistCreate(BaseModel):
    """점검 항목 생성 시 받는 데이터"""
    code:        str
    title:       str
    category:    str
    description: Optional[str] = None
    severity:    str
    standard:    str
    check_method: str

class ChecklistResponse(BaseModel):
    id:           int
    code:         str
    title:        str
    category:     str
    severity:     str
    standard:     str
    target:       str
    check_method: Optional[str] = None

    class Config:
        from_attributes = True

# --- API 엔드포인트 ---

@router.get("/", response_model=list[ChecklistResponse])
def get_all_checklists(db: Session = Depends(get_db)):
    return (
        db.query(ChecklistItem)
        .order_by(ChecklistItem.sort_order)   # ← checklist_data.py 순서대로
        .all()
    )

@router.get("/{item_id}", response_model=ChecklistResponse)
def get_checklist(item_id: int, db: Session = Depends(get_db)):
    """특정 점검 항목 조회"""
    item = db.query(ChecklistItem).filter(ChecklistItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="항목을 찾을 수 없습니다")
    return item

@router.post("/", response_model=ChecklistResponse, status_code=201)
def create_checklist(data: ChecklistCreate, db: Session = Depends(get_db)):
    """점검 항목 생성"""
    item = ChecklistItem(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.delete("/{item_id}", status_code=204)
def delete_checklist(item_id: int, db: Session = Depends(get_db)):
    """점검 항목 삭제"""
    item = db.query(ChecklistItem).filter(ChecklistItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="항목을 찾을 수 없습니다")
    db.delete(item)
    db.commit()
