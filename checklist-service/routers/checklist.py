# routers/checklist.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from models.checklist import ChecklistItem
from database import get_db              # ← main 대신 database에서 가져오기

router = APIRouter()

# --- 요청/응답 스키마 정의 ---
# Pydantic 모델: API로 받고 보내는 데이터 형식 정의

class ChecklistCreate(BaseModel):
    """점검 항목 생성 시 받는 데이터"""
    code:        str
    title:       str
    category:    str
    description: Optional[str] = None
    severity:    str  # "상", "중", "하"
    standard:    str  # "기반시설", "클라우드"

class ChecklistResponse(BaseModel):
    """점검 항목 조회 시 반환하는 데이터"""
    id:          int
    code:        str
    title:       str
    category:    str
    description: Optional[str]
    severity:    str
    standard:    str

    class Config:
        from_attributes = True  # SQLAlchemy 모델을 Pydantic으로 변환 허용


# --- API 엔드포인트 ---

@router.get("/", response_model=list[ChecklistResponse])
def get_all_checklists(db: Session = Depends(get_db)):
    return db.query(ChecklistItem).all()

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
    item = ChecklistItem(**data.model_dump())  # 받은 데이터로 DB 객체 생성
    db.add(item)
    db.commit()       # DB에 저장
    db.refresh(item)  # 저장된 데이터(id 포함) 다시 불러오기
    return item


@router.delete("/{item_id}", status_code=204)
def delete_checklist(item_id: int, db: Session = Depends(get_db)):
    """점검 항목 삭제"""
    item = db.query(ChecklistItem).filter(ChecklistItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="항목을 찾을 수 없습니다")
    db.delete(item)
    db.commit()
