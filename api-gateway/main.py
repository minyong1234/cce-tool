# main.py
# api-gateway: 외부 요청을 각 마이크로서비스로 라우팅
# 클라이언트는 api-gateway 하나만 알면 되고,
# 내부 서비스 주소는 api-gateway가 관리

import os
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response

app = FastAPI(
    title="API Gateway",
    description="CCE 툴 API Gateway — 요청 라우팅",
    version="1.0.0"
)

# 각 서비스의 내부 주소 (k3s ClusterIP Service 이름)
SERVICES = {
    "checklists": os.getenv("CHECKLIST_SERVICE_URL", "http://checklist-service.app.svc.cluster.local:8000"),
    "assets":     os.getenv("RESULT_SERVICE_URL",    "http://result-service.app.svc.cluster.local:8001"),
    "results":    os.getenv("RESULT_SERVICE_URL",    "http://result-service.app.svc.cluster.local:8001"),
    "scan":       os.getenv("SCAN_SERVICE_URL",      "http://scan-service.app.svc.cluster.local:8002"),
    "report":     os.getenv("REPORT_SERVICE_URL",    "http://report-service.app.svc.cluster.local:8003"),
}


async def _proxy(request: Request, service_url: str) -> Response:
    """
    요청을 그대로 대상 서비스로 전달(프록시)하고 응답을 반환
    """
    # 원본 요청의 경로와 쿼리스트링 유지
    path = request.url.path
    query = request.url.query
    target_url = f"{service_url}{path}"
    if query:
        target_url += f"?{query}"

    # 원본 요청의 body와 headers 그대로 전달
    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None)  # host 헤더는 제거 (대상 서비스 주소로 대체됨)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                timeout=30.0
            )
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type")
            )
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="서비스에 연결할 수 없습니다")
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="서비스 응답 시간 초과")


# ── 라우팅 규칙 ────────────────────────────────────────

@app.api_route("/checklists{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_checklist(request: Request, path: str):
    """점검 항목 관리 → checklist-service"""
    return await _proxy(request, SERVICES["checklists"])


@app.api_route("/assets{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_assets(request: Request, path: str):
    """자산 관리 → result-service"""
    return await _proxy(request, SERVICES["assets"])


@app.api_route("/results{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_results(request: Request, path: str):
    """점검 결과 관리 → result-service"""
    return await _proxy(request, SERVICES["results"])


@app.api_route("/scan{path:path}", methods=["GET", "POST"])
async def route_scan(request: Request, path: str):
    """점검 실행 & 스크립트 다운로드 → scan-service"""
    return await _proxy(request, SERVICES["scan"])


@app.api_route("/report{path:path}", methods=["GET"])
async def route_report(request: Request, path: str):
    """리포트 생성 → report-service"""
    return await _proxy(request, SERVICES["report"])


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "api-gateway"}
