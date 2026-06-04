# main.py

from fastapi import FastAPI
from database import engine          # database.py에서 가져오기
from models.checklist import Base
from routers import checklist as checklist_router

# 앱 시작 시 테이블 자동 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Checklist Service",
    description="CCE 점검 항목 관리 API",
    version="1.0.0"
)

app.include_router(
    checklist_router.router,
    prefix="/checklists",
    tags=["checklists"]
)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "checklist-service"}
