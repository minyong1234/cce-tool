// src/pages/ChecklistPage.jsx
// 점검 항목 목록 페이지 — 필터링, 검색 기능 포함

import { useEffect, useState } from "react";
import { getChecklists } from "../api";

// 위험도별 색상
const SEVERITY_COLOR = {
  상: { bg: "#fee2e2", text: "#ef4444" },
  중: { bg: "#fef9c3", text: "#ca8a04" },
  하: { bg: "#dcfce7", text: "#16a34a" },
};

// 점검 방법별 색상
const METHOD_COLOR = {
  auto:      { bg: "#dbeafe", text: "#2563eb" },
  interview: { bg: "#f3e8ff", text: "#7c3aed" },
};

function ChecklistPage() {
  const [items, setItems]         = useState([]);
  const [filtered, setFiltered]   = useState([]);
  const [loading, setLoading]     = useState(true);
  const [search, setSearch]       = useState("");
  const [filterTarget, setFilterTarget]     = useState("전체");
  const [filterSeverity, setFilterSeverity] = useState("전체");
  const [filterMethod, setFilterMethod]     = useState("전체");

  useEffect(() => {
    getChecklists()
      .then((res) => {
        setItems(res.data);
        setFiltered(res.data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  // 필터 적용
  useEffect(() => {
    let result = items;
    if (search)
      result = result.filter((i) =>
        i.title.includes(search) || i.code.includes(search)
      );
    if (filterTarget !== "전체")
      result = result.filter((i) => i.target === filterTarget);
    if (filterSeverity !== "전체")
      result = result.filter((i) => i.severity === filterSeverity);
    if (filterMethod !== "전체")
      result = result.filter((i) => i.check_method === filterMethod);
    setFiltered(result);
  }, [search, filterTarget, filterSeverity, filterMethod, items]);

  // 점검 대상 목록 (중복 제거)
  const targets = ["전체", ...new Set(items.map((i) => i.target))];

  if (loading) return <p>로딩 중...</p>;

  return (
    <div>
      <h1 style={{ fontSize: "22px", marginBottom: "24px" }}>
        점검 항목 목록 ({filtered.length}개)
      </h1>

      {/* 필터 영역 */}
      <div style={{
        backgroundColor: "white", borderRadius: "12px",
        padding: "16px 20px", marginBottom: "16px",
        boxShadow: "0 1px 4px rgba(0,0,0,0.08)",
        display: "flex", gap: "12px", flexWrap: "wrap", alignItems: "center"
      }}>
        <input
          placeholder="항목 코드 또는 항목명 검색"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{
            padding: "8px 12px", border: "1px solid #e2e8f0",
            borderRadius: "6px", fontSize: "13px", minWidth: "220px"
          }}
        />
        {[
          { label: "점검 대상", value: filterTarget,   setter: setFilterTarget,   options: targets },
          { label: "위험도",    value: filterSeverity, setter: setFilterSeverity, options: ["전체", "상", "중", "하"] },
          { label: "점검 방법", value: filterMethod,   setter: setFilterMethod,   options: ["전체", "auto", "interview"] },
        ].map((f) => (
          <select
            key={f.label}
            value={f.value}
            onChange={(e) => f.setter(e.target.value)}
            style={{
              padding: "8px 12px", border: "1px solid #e2e8f0",
              borderRadius: "6px", fontSize: "13px"
            }}
          >
            {f.options.map((o) => <option key={o}>{o}</option>)}
          </select>
        ))}
      </div>

      {/* 항목 테이블 */}
      <div style={{
        backgroundColor: "white", borderRadius: "12px",
        padding: "20px", boxShadow: "0 1px 4px rgba(0,0,0,0.08)"
      }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
          <thead>
            <tr style={{ backgroundColor: "#f8fafc" }}>
              {["코드", "항목명", "분류", "점검 대상", "위험도", "점검 방법"].map((h) => (
                <th key={h} style={{
                  padding: "10px 12px", textAlign: "left",
                  borderBottom: "1px solid #e2e8f0", color: "#64748b"
                }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr><td colSpan={6} style={{ padding: "20px", textAlign: "center", color: "#94a3b8" }}>항목이 없습니다</td></tr>
            ) : filtered.map((item) => (
              <tr key={item.id} style={{ borderBottom: "1px solid #f1f5f9" }}>
                <td style={{ padding: "10px 12px", fontWeight: "500" }}>{item.code}</td>
                <td style={{ padding: "10px 12px" }}>{item.title}</td>
                <td style={{ padding: "10px 12px", color: "#64748b" }}>{item.category}</td>
                <td style={{ padding: "10px 12px", color: "#64748b" }}>{item.target}</td>
                <td style={{ padding: "10px 12px" }}>
                  <span style={{
                    padding: "2px 8px", borderRadius: "20px", fontSize: "11px",
                    backgroundColor: SEVERITY_COLOR[item.severity]?.bg,
                    color: SEVERITY_COLOR[item.severity]?.text
                  }}>{item.severity}</span>
                </td>
                <td style={{ padding: "10px 12px" }}>
                  <span style={{
                    padding: "2px 8px", borderRadius: "20px", fontSize: "11px",
                    backgroundColor: METHOD_COLOR[item.check_method]?.bg,
                    color: METHOD_COLOR[item.check_method]?.text
                  }}>{item.check_method}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ChecklistPage;
