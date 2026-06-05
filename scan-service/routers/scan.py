# routers/scan.py

import os
import httpx
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from parsers.linux import parse_result_file, judge_result

router = APIRouter()

RESULT_SERVICE_URL = os.getenv(
    "RESULT_SERVICE_URL",
    "http://result-service.app.svc.cluster.local:8001"
)

@router.get("/scripts/linux")
def download_script():
    """점검 대상 서버에서 실행할 Shell 스크립트 다운로드"""
    script_path = "scripts/linux_scan.sh"
    if not os.path.exists(script_path):
        raise HTTPException(status_code=404, detail="스크립트 파일을 찾을 수 없습니다")
    return FileResponse(
        script_path,
        media_type="application/x-sh",
        filename="linux_scan.sh"
    )

@router.post("/upload")
async def upload_scan_result(
    asset_id: int = Form(...),
    file: UploadFile = File(...)
):
    """점검 결과 파일 업로드 & 자동 판단 & result-service에 저장"""
    content = await file.read()
    text = content.decode("utf-8")

    parsed = parse_result_file(text)
    if not parsed:
        raise HTTPException(status_code=400, detail="결과 파일 형식이 올바르지 않습니다")

    saved_count = 0
    errors = []

    async with httpx.AsyncClient() as client:
        for code, value in parsed.items():
            judgment = judge_result(code, value)
            try:
                response = await client.post(
                    f"{RESULT_SERVICE_URL}/results",
                    json={
                        "asset_id": asset_id,
                        "checklist_code": code,
                        "result": judgment["result"],
                        "current_status": value,
                        "improvement": judgment["improvement"]
                    }
                )
                if response.status_code == 201:
                    saved_count += 1
                else:
                    errors.append(f"{code}: 저장 실패")
            except Exception as e:
                errors.append(f"{code}: {str(e)}")

    return {
        "message": f"{saved_count}개 항목 저장 완료",
        "asset_id": asset_id,
        "total_items": len(parsed),
        "saved": saved_count,
        "errors": errors
    }
