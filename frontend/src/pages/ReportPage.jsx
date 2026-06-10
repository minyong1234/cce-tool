// src/pages/ReportPage.jsx
// 리포트 다운로드 페이지

import { useEffect, useState } from "react";
import { getAssets, downloadExcelReport, downloadPdfReport } from "../api";

function ReportPage() {
  const [assets, setAssets] = useState([]);

  useEffect(() => {
    getAssets().then((res) => setAssets(res.data)).catch(console.error);
  }, []);

  return (
    <div>
      <h1 style={{ fontSize: "22px", marginBottom: "24px" }}>리포트 다운로드</h1>

      <div style={{
        backgroundColor: "white", borderRadius: "12px",
        padding: "20px", boxShadow: "0 1px 4px rgba(0,0,0,0.08)"
      }}>
        {assets.length === 0 ? (
          <p style={{ color: "#94a3b8", fontSize: "13px" }}>
            등록된 자산이 없습니다. 먼저 자산을 등록하고 점검을 진행해주세요.
          </p>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
            <thead>
              <tr style={{ backgroundColor: "#f8fafc" }}>
                {["자산 코드", "호스트명", "IP", "담당자", "Excel", "PDF"].map((h) => (
                  <th key={h} style={{
                    padding: "10px 12px", textAlign: "left",
                    borderBottom: "1px solid #e2e8f0", color: "#64748b"
                  }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {assets.map((a) => (
                <tr key={a.id} style={{ borderBottom: "1px solid #f1f5f9" }}>
                  <td style={{ padding: "10px 12px" }}>{a.code}</td>
                  <td style={{ padding: "10px 12px" }}>{a.hostname}</td>
                  <td style={{ padding: "10px 12px" }}>{a.ip}</td>
                  <td style={{ padding: "10px 12px" }}>{a.manager}</td>
                  <td style={{ padding: "10px 12px" }}>
                    
                      href={downloadExcelReport(a.id)}
                      style={{
                        padding: "6px 14px", backgroundColor: "#dcfce7",
                        color: "#16a34a", borderRadius: "6px",
                        textDecoration: "none", fontSize: "12px"
                      }}
                    <a>📊 Excel</a>
                  </td>
                  <td style={{ padding: "10px 12px" }}>
                    
                      href={downloadPdfReport(a.id)}
                      style={{
                        padding: "6px 14px", backgroundColor: "#fee2e2",
                        color: "#ef4444", borderRadius: "6px",
                        textDecoration: "none", fontSize: "12px"
                      }}
                   <a>📄 PDF</a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default ReportPage;
