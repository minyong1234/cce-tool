# main.py

import os
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.checklist import Base
from routers import checklist as checklist_router

# --- DB 연결 설정 ---
# 환경변수에서 DB 주소를 가져옴
# k3s 배포 시 ConfigMap에서 주입됨
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://cce_user:cce_password@localhost:5432/cce_db"  # 로컬 기본값
)

# DB 엔진 생성 (실제 DB와의 연결 담당)
engine = create_engine(DATABASE_URL)

# 세션 팩토리 생성 (DB 작업할 때마다 세션을 열고 닫음)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 앱 시작 시 테이블 자동 생성
Base.metadata.create_all(bind=engine)

# --- FastAPI 앱 생성 ---
app = FastAPI(
    title="Checklist Service",
    description="CCE 점검 항목 관리 API",
    version="1.0.0"
)

# DB 세션을 라우터에서 쓸 수 있도록 의존성 주입 함수
def get_db():
    """
    API 요청마다 DB 세션을 열고, 요청이 끝나면 자동으로 닫아줌
    yield 키워드로 요청 처리 중에만 세션을 유지
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 라우터 등록 (실제 API 엔드포인트들)
app.include_router(
    checklist_router.router,
    prefix="/checklists",  # 모든 엔드포인트 앞에 /checklists 붙음
    tags=["checklists"]
)

# 헬스체크 엔드포인트 (k3s가 서비스 상태 확인할 때 사용)
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "checklist-service"}
