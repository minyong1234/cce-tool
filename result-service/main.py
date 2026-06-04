# main.py

from fastapi import FastAPI
from database import engine
from models.asset import Base as AssetBase
from models.scan_result import Base as ResultBase
from routers import asset as asset_router
from routers import scan_result as result_router

# 두 테이블 모두 자동 생성
AssetBase.metadata.create_all(bind=engine)
ResultBase.metadata.create_all(bind=engine)

app = FastAPI(
    title="Result Service",
    description="CCE 점검 결과 저장 및 조회 API",
    version="1.0.0"
)

app.include_router(
    asset_router.router,
    prefix="/assets",
    tags=["assets"]
)

app.include_router(
    result_router.router,
    prefix="/results",
    tags=["results"]
)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "result-service"}
