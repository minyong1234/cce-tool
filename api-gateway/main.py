import os
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response

app = FastAPI(
    title="API Gateway",
    description="CCE 툴 API Gateway — 요청 라우팅",
    version="1.0.0"
)

SERVICES = {
    "checklists": os.getenv("CHECKLIST_SERVICE_URL", "http://checklist-service.app.svc.cluster.local:8000"),
    "assets":     os.getenv("RESULT_SERVICE_URL",    "http://result-service.app.svc.cluster.local:8001"),
    "results":    os.getenv("RESULT_SERVICE_URL",    "http://result-service.app.svc.cluster.local:8001"),
    "scan":       os.getenv("SCAN_SERVICE_URL",      "http://scan-service.app.svc.cluster.local:8002"),
    "report":     os.getenv("REPORT_SERVICE_URL",    "http://report-service.app.svc.cluster.local:8003"),
}


async def _proxy(request: Request, service_url: str) -> Response:
    path = request.url.path
    # /api prefix 제거
    if path.startswith("/api"):
        path = path[4:]
    # 경로 끝에 / 가 없으면 추가 (307 redirect 방지)
    if not path.endswith("/"):
        path = path + "/"
    query = request.url.query
    target_url = f"{service_url}{path}"
    if query:
        target_url += f"?{query}"
    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None)
    async with httpx.AsyncClient(follow_redirects=True) as client:
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

@app.api_route("/api/checklists{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_checklist(request: Request, path: str):
    return await _proxy(request, SERVICES["checklists"])

@app.api_route("/api/assets{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_assets(request: Request, path: str):
    return await _proxy(request, SERVICES["assets"])

@app.api_route("/api/results{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_results(request: Request, path: str):
    return await _proxy(request, SERVICES["results"])

@app.api_route("/api/scan{path:path}", methods=["GET", "POST"])
async def route_scan(request: Request, path: str):
    return await _proxy(request, SERVICES["scan"])

@app.api_route("/api/report{path:path}", methods=["GET"])
async def route_report(request: Request, path: str):
    return await _proxy(request, SERVICES["report"])

@app.get("/health")
def health_check2():
    return {"status": "ok", "service": "api-gateway"}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "api-gateway"}
