// src/pages/ScanPage.jsx
// 점검 실행 페이지
// 1. 스크립트 다운로드
// 2. 결과 파일 업로드
// 3. PENDING 항목 Y/N/N/A 직접 입력

import { useEffect, useState } from "react";
import { getAssets, getResultsByAsset, uploadScanResult, updateResult, downloadScript } from "../api";

const RESULT_OPTIONS = ["Y", "N", "N/A"];

function ScanPage() {
  const [assets, setAssets]             = useState([]);
  const [selectedAsset, setSelectedAsset] = useState("");
  const [results, setResults]           = useState([]);
  const [file, setFile]                 = useState(null);
  const [uploading, setUploading]       = useState(false);
  const [message, setMessage]           = useState("");

  // 자산 목록 불러오기
  useEffect(() => {
    getAssets().then((res) => setAssets(res.data)).catch(console.error);
  }, []);

  // 자산 선택 시 점검 결과 불러오기
  const handleAssetChange = (e) => {
    const id = e.target.value;
    setSelectedAsset(id);
    if (id) {
      getResultsByAsset(id)
        .then((res) => setResults(res.data))
        .catch(console.error);
    } else {
      setResults([]);
    }
  };

  // 결과 파일 업로드
  const handleUpload = async () => {
    if (!selectedAsset || !file) {
      alert("자산을 선택하고 결과 파일을 첨부해주세요.");
      return;
    }
    setUploading(true);
    try {
      const res = await uploadScanResult(selectedAsset, file);
      setMessage(`✅ ${res.data.saved}개 항목 저장 완료`);
      // 결과 다시 불러오기
      const updated = await getResultsByAsset(selectedAsset);
      setResults(updated.data);
    } catch (e) {
      setMessage("❌ 업로드 실패: " + e.message);
    } finally {
      setUploading(false);
    }
  };

  // PENDING 항목 결과 직접 입력
  const handleResultChange = async (result, newValue) => {
    try {
      await updateResult(result.id, { ...result, result: newValue });
      setResults((prev) =>
        prev.map((r) => r.id === result.id ? { ...r, result: newValue } : r)
      );
    } catch (e) {
      alert("수정 실패: " + e.message);
    }
  };

  // PENDING 항목만 필터링
  const pendingResults = results.filter((r) => r.result === "PENDING");

  return (
    <div>
      <h1 style={{ fontSize: "22px", marginBottom: "24px" }}>점검 실행</h1>

      {/* 1. 스크립트 다운로드 */}
      <div style={{
        backgroundColor: "white", borderRadius: "12px",
        padding: "20px", marginBottom: "16px",
        boxShadow: "0 1px 4px rgba(0,0,0,0.08)"
      }}>
        <h3 style={{ margin: "0 0 8px", fontSize: "15px" }}>1단계 — 점검 스크립트 다운로드</h3>
        <p style={{ fontSize: "13px", color: "#64748b", margin: "0 0 12px" }}>
          스크립트를 점검 대상 서버에서 실행하세요.
          <br />
          실행 방법: <code>bash linux_scan.sh &gt; result.txt</code>
        </p>
        
         <a href={downloadScript()}
          download="linux_scan.sh"
          style={{
            display: "inline-block", padding: "10px 20px",
            backgroundColor: "#0f172a", color: "white",
            borderRadius: "6px", textDecoration: "none", fontSize: "13px"
          }}>
	  📥 linux_scan.sh 다운로드
         </a>
      </div>

      {/* 2. 결과 파일 업로드 */}
      <div style={{
        backgroundColor: "white", borderRadius: "12px",
        padding: "20px", marginBottom: "16px",
        boxShadow: "0 1px 4px rgba(0,0,0,0.08)"
      }}>
        <h3 style={{ margin: "0 0 12px", fontSize: "15px" }}>2단계 — 결과 파일 업로드</h3>
        <div style={{ display: "flex", gap: "12px", alignItems: "center", flexWrap: "wrap" }}>
          <select
            value={selectedAsset}
            onChange={handleAssetChange}
            style={{ padding: "8px 12px", border: "1px solid #e2e8f0", borderRadius: "6px", fontSize: "13px" }}
          >
            <option value="">자산 선택</option>
            {assets.map((a) => (
              <option key={a.id} value={a.id}>{a.hostname} ({a.ip})</option>
            ))}
          </select>
          <input
            type="file"
            accept=".txt"
            onChange={(e) => setFile(e.target.files[0])}
            style={{ fontSize: "13px" }}
          />
          <button
            onClick={handleUpload}
            disabled={uploading}
            style={{
              padding: "10px 20px", backgroundColor: "#3b82f6",
              color: "white", border: "none",
              borderRadius: "6px", fontSize: "13px", cursor: "pointer"
            }}
          >
            {uploading ? "업로드 중..." : "업로드 & 자동 판단"}
          </button>
        </div>
        {message && (
          <p style={{ marginTop: "12px", fontSize: "13px", color: "#3b82f6" }}>{message}</p>
        )}
      </div>

      {/* 3. PENDING 항목 직접 입력 */}
      {pendingResults.length > 0 && (
        <div style={{
          backgroundColor: "white", borderRadius: "12px",
          padding: "20px", boxShadow: "0 1px 4px rgba(0,0,0,0.08)"
        }}>
          <h3 style={{ margin: "0 0 4px", fontSize: "15px" }}>
            3단계 — 미확인 항목 직접 입력 ({pendingResults.length}개)
          </h3>
          <p style={{ fontSize: "12px", color: "#94a3b8", margin: "0 0 16px" }}>
            자동 판단이 어려운 항목입니다. 직접 확인 후 결과를 선택해주세요.
          </p>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
            <thead>
              <tr style={{ backgroundColor: "#f8fafc" }}>
                {["항목 코드", "현황", "결과 선택"].map((h) => (
                  <th key={h} style={{
                    padding: "10px 12px", textAlign: "left",
                    borderBottom: "1px solid #e2e8f0", color: "#64748b"
                  }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {pendingResults.map((r) => (
                <tr key={r.id} style={{ borderBottom: "1px solid #f1f5f9" }}>
                  <td style={{ padding: "10px 12px", fontWeight: "500" }}>{r.checklist_code}</td>
                  <td style={{ padding: "10px 12px", color: "#64748b", maxWidth: "300px" }}>
                    {r.current_status || "-"}
                  </td>
                  <td style={{ padding: "10px 12px" }}>
                    <div style={{ display: "flex", gap: "6px" }}>
                      {RESULT_OPTIONS.map((opt) => (
                        <button
                          key={opt}
                          onClick={() => handleResultChange(r, opt)}
                          style={{
                            padding: "4px 12px",
                            backgroundColor: opt === "Y" ? "#dcfce7" : opt === "N" ? "#fee2e2" : "#f1f5f9",
                            color: opt === "Y" ? "#16a34a" : opt === "N" ? "#ef4444" : "#64748b",
                            border: "none", borderRadius: "4px",
                            cursor: "pointer", fontSize: "12px", fontWeight: "500"
                          }}
                        >{opt}</button>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default ScanPage;
