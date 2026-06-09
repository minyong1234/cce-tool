# utils/pdf_report.py

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def generate_pdf_report(asset: dict, results: list) -> str:
    """
    asset: 자산 정보 딕셔너리
    results: 점검 결과 리스트
    반환: 생성된 PDF 파일 경로
    """
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"{output_dir}/{asset['code']}_{timestamp}.pdf"

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=30, leftMargin=30,
        topMargin=30, bottomMargin=30
    )

    # 한글 폰트 등록
    try:
        pdfmetrics.registerFont(
            TTFont("NanumGothic",
                   "/usr/share/fonts/truetype/nanum/NanumGothic.ttf")
        )
        font_name = "NanumGothic"
    except Exception:
        font_name = "Helvetica"

    styles = getSampleStyleSheet()
    korean_style = ParagraphStyle(
        "Korean", parent=styles["Normal"],
        fontName=font_name, fontSize=9
    )
    title_style = ParagraphStyle(
        "KoreanTitle", parent=styles["Title"],
        fontName=font_name, fontSize=16
    )

    elements = []

    # 제목
    elements.append(Paragraph("CCE 취약점 점검 결과 보고서", title_style))
    elements.append(Spacer(1, 20))

    # 자산 정보
    elements.append(Paragraph("1. 점검 대상 자산 정보", korean_style))
    elements.append(Spacer(1, 10))

    asset_data = [
        ["항목", "내용"],
        ["자산 코드",  asset.get("code", "")],
        ["호스트명",   asset.get("hostname", "")],
        ["IP 주소",   asset.get("ip", "")],
        ["OS",        asset.get("os", "")],
        ["용도",      asset.get("purpose", "")],
        ["담당자",    asset.get("manager", "")],
        ["점검일",    datetime.now().strftime("%Y-%m-%d")],
    ]

    asset_table = Table(asset_data, colWidths=[100, 300])
    asset_table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0),  colors.grey),
        ("TEXTCOLOR",   (0, 0), (-1, 0),  colors.whitesmoke),
        ("FONTNAME",    (0, 0), (-1, -1), font_name),
        ("FONTSIZE",    (0, 0), (-1, -1), 9),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN",       (0, 0), (-1, -1), "LEFT"),
        ("PADDING",     (0, 0), (-1, -1), 6),
    ]))
    elements.append(asset_table)
    elements.append(Spacer(1, 20))

    # 결과 요약
    total   = len(results)
    safe    = sum(1 for r in results if r["result"] == "Y")
    vuln    = sum(1 for r in results if r["result"] == "N")
    na      = sum(1 for r in results if r["result"] == "N/A")
    pending = sum(1 for r in results if r["result"] == "PENDING")

    elements.append(Paragraph("2. 점검 결과 요약", korean_style))
    elements.append(Spacer(1, 10))

    summary_data = [
        ["전체", "양호(Y)", "취약(N)", "해당없음(N/A)", "미확인(PENDING)"],
        [str(total), str(safe), str(vuln), str(na), str(pending)],
    ]

    summary_table = Table(summary_data, colWidths=[80, 80, 80, 100, 100])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0),  colors.grey),
        ("TEXTCOLOR",   (0, 0), (-1, 0),  colors.whitesmoke),
        ("FONTNAME",    (0, 0), (-1, -1), font_name),
        ("FONTSIZE",    (0, 0), (-1, -1), 9),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
        ("PADDING",     (0, 0), (-1, -1), 6),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    # 결과 상세
    elements.append(Paragraph("3. 점검 결과 상세", korean_style))
    elements.append(Spacer(1, 10))

    detail_data = [["항목 코드", "결과", "현황", "개선방안"]]
    for r in results:
        detail_data.append([
            r.get("checklist_code", ""),
            r.get("result", ""),
            Paragraph(r.get("current_status", "") or "", korean_style),
            Paragraph(r.get("improvement", "") or "", korean_style),
        ])

    detail_table = Table(detail_data, colWidths=[70, 50, 180, 180])
    detail_table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0),  colors.grey),
        ("TEXTCOLOR",   (0, 0), (-1, 0),  colors.whitesmoke),
        ("FONTNAME",    (0, 0), (-1, -1), font_name),
        ("FONTSIZE",    (0, 0), (-1, -1), 8),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN",       (0, 0), (1, -1),  "CENTER"),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING",     (0, 0), (-1, -1), 4),
        *[("BACKGROUND", (1, i+1), (1, i+1), colors.lightgreen)
          for i, r in enumerate(results) if r.get("result") == "Y"],
        *[("BACKGROUND", (1, i+1), (1, i+1), colors.salmon)
          for i, r in enumerate(results) if r.get("result") == "N"],
        *[("BACKGROUND", (1, i+1), (1, i+1), colors.lightyellow)
          for i, r in enumerate(results) if r.get("result") == "PENDING"],
    ]))
    elements.append(detail_table)

    doc.build(elements)
    return output_path
