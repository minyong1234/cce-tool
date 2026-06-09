from fastapi import FastAPI
from routers import report as report_router

app = FastAPI(
    title="Report Service",
    description="CCE 점검 결과 Excel/PDF 리포트 생성 API",
    version="1.0.0"
)

app.include_router(
    report_router.router,
    prefix="/report",
    tags=["report"]
)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "report-service"}
