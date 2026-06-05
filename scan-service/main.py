# main.py

from fastapi import FastAPI
from routers import scan as scan_router

app = FastAPI(
    title="Scan Service",
    description="CCE 점검 스크립트 제공 및 결과 분석 API",
    version="1.0.0"
)

app.include_router(
    scan_router.router,
    prefix="/scan",
    tags=["scan"]
)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "scan-service"}
