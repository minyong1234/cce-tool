# routers/report.py

import os
import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from utils.excel_report import generate_excel_report
from utils.pdf_report import generate_pdf_report

router = APIRouter()

RESULT_SERVICE_URL = os.getenv(
    "RESULT_SERVICE_URL",
    "http://result-service.app.svc.cluster.local:8001"
)


async def _fetch_asset_and_results(asset_id: int) -> tuple:
    """result-service에서 자산 정보와 점검 결과 조회"""
    async with httpx.AsyncClient() as client:
        asset_res = await client.get(
            f"{RESULT_SERVICE_URL}/assets/{asset_id}"
        )
        if asset_res.status_code != 200:
            raise HTTPException(status_code=404, detail="자산을 찾을 수 없습니다")

        results_res = await client.get(
            f"{RESULT_SERVICE_URL}/results/asset/{asset_id}"
        )
        if results_res.status_code != 200:
            raise HTTPException(status_code=404, detail="점검 결과를 찾을 수 없습니다")

    return asset_res.json(), results_res.json()


@router.get("/excel/{asset_id}")
async def download_excel_report(asset_id: int):
    """Excel 리포트 생성 후 다운로드"""
    asset, results = await _fetch_asset_and_results(asset_id)
    if not results:
        raise HTTPException(status_code=404, detail="점검 결과가 없습니다")

    file_path = generate_excel_report(asset, results)
    return FileResponse(
        path=file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"cce_report_{asset['code']}.xlsx"
    )


@router.get("/pdf/{asset_id}")
async def download_pdf_report(asset_id: int):
    """PDF 리포트 생성 후 다운로드"""
    asset, results = await _fetch_asset_and_results(asset_id)
    if not results:
        raise HTTPException(status_code=404, detail="점검 결과가 없습니다")

    file_path = generate_pdf_report(asset, results)
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=f"cce_report_{asset['code']}.pdf"
    )
