# routers/asset.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from models.asset import Asset
from database import get_db

router = APIRouter()

class AssetCreate(BaseModel):
    code:     str
    hostname: str
    ip:       str
    os:       Optional[str] = None
    version:  Optional[str] = None
    purpose:  Optional[str] = None
    location: Optional[str] = None
    manager:  Optional[str] = None

class AssetResponse(BaseModel):
    id:       int
    code:     str
    hostname: str
    ip:       str
    os:       Optional[str]
    version:  Optional[str]
    purpose:  Optional[str]
    location: Optional[str]
    manager:  Optional[str]

    class Config:
        from_attributes = True

@router.get("/", response_model=list[AssetResponse])
def get_all_assets(db: Session = Depends(get_db)):
    """전체 자산 목록 조회"""
    return db.query(Asset).all()

@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    """특정 자산 조회"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="자산을 찾을 수 없습니다")
    return asset

@router.post("/", response_model=AssetResponse, status_code=201)
def create_asset(data: AssetCreate, db: Session = Depends(get_db)):
    """자산 등록"""
    asset = Asset(**data.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset

@router.delete("/{asset_id}", status_code=204)
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    """자산 삭제"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="자산을 찾을 수 없습니다")
    db.delete(asset)
    db.commit()
