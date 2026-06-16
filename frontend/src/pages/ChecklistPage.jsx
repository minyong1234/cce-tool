// src/pages/ChecklistPage.jsx
// 점검 항목 목록 페이지 — 점검 기준 탭 + 점검 대상 서브탭 + 검색

import { useEffect, useState } from "react";
import { getChecklists } from "../api";

const SEVERITY_COLOR = {
  상: { bg: "#FCEBEB", text: "#791F1F" },
  중: { bg: "#FAEEDA", text: "#633806" },
  하: { bg: "#EAF3DE", text: "#27500A" },
};

const METHOD_COLOR = {
  auto:      { bg: "#EAF3DE", text: "#27500A" },
  interview: { bg: "#EEEDFE", text: "#3C3489" },
};

const STANDARD_STYLE = {
  "기반시설": { bg: "#EEEDFE", color: "#3C3489", label: "주요정보통신기반" },
  "클라우드": { bg: "#FAEEDA", color: "#633806", label: "클라우드" },
};

const TARGET_COLORS = [
  { bg: "#E6F1FB", color: "#0C447C" },
  { bg: "#FBEAF0", color: "#72243E" },
  { bg: "#E1F5EE", color: "#085041" },
  { bg: "#F1EFE8", color: "#444441" },
  { bg: "#EEEDFE", color: "#26215C" },
];

function ChecklistPage() {
  const [items, setItems]       = useState([]);
  const [loading, setLoading]   = useState(true);
  const [search, setSearch]     = useState("");
  const [activeStandard, setActiveStandard] = useState("전체");
  const [activeTarget, setActiveTarget]     = useState("전체");

  useEffect(() => {
    getChecklists()
      .then((res) => setItems(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleStandardChange = (standard) => {
    setActiveStandard(standard);
    setActiveTarget("전체");
  };

  const targetOptions = ["전체", ...new Set(
    items
      .filter((i) => activeStandard === "전체" || i.standard === activeStandard)
      .map((i) => {
        if (i.standard === "클라우드") return i.target.replace("클라우드-", "");
        return i.target;
      })
  )];

  const targetColorMap = {};
  [...new Set(items.map((i) => i.target))].forEach((t, idx) => {
    targetColorMap[t] = TARGET_COLORS[idx % TARGET_COLORS.length];
  });

  const filtered = items.filter((i) => {
    const matchStandard = activeStandard === "전체" || i.standard === activeStandard;
    const displayTarget = i.standard === "클라우드"
      ? i.target.replace("클라우드-", "")
      : i.target;
    const matchTarget = activeTarget === "전체" || displayTarget === activeTarget;
    const matchSearch = !search || i.title.includes(search) || i.code.includes(search);
    return matchStandard && matchTarget && matchSearch;
  });

  if (loading) return <p>로딩 중...</p>;

  const tabStyle = (active) => ({
    background: "none",
    border: "none",
    cursor: "pointer",
    padding: "10px 16px",
    fontSize: "13px",
    color: active ? "#534AB7" : "#64748b",
    borderBottom: active ? "2px solid #534AB7" : "2px solid transparent",
    fontWeight: active ? "500" : "400",
    whiteSpace: "nowrap",
  });

  const subTabStyle = (active) => ({
    background: active ? "#EEEDFE" : "none",
    border: `0.5px solid ${active ? "#AFA9EC" : "#e2e8f0"}`,
    cursor: "pointer",
    padding: "5px 12px",
    fontSize: "12px",
    color: active ? "#3C3489" : "#64748b",
    borderRadius: "20px",
    fontWeight: active ? "500" : "400",
    whiteSpace: "nowrap",
  });

  const cardStyle = {
    backgroundColor: "white",
    borderRadius: "12px",
    boxShadow: "0 1px 4px rgba(0,0,0,0.08)",
    overflow: "hidden",
  };

  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "24px" }}>
        <h1 style={{ fontSize: "22px", margin: 0 }}>점검 항목 목록</h1>
        <span style={{ fontSize: "13px", color: "#64748b" }}>{filtered.length}개 항목</span>
      </div>

      {/* 탭 + 서브탭 + 검색 */}
      <div style={{ ...cardStyle, marginBottom: "16px" }}>

        {/* 상단 탭 — 점검 기준 */}
        <div style={{ display: "flex", borderBottom: "1px solid #f1f5f9", overflowX: "auto" }}>
          {[
            { key: "전체",    label: "전체" },
            { key: "기반시설", label: "주요정보통신기반", icon: "ti-building" },
            { key: "클라우드", label: "클라우드",        icon: "ti-cloud" },
          ].map(({ key, label, icon }) => (
            <button key={key} onClick={() => handleStandardChange(key)} style={tabStyle(activeStandard === key)}>
              {icon && <i className={`ti ${icon}`} aria-hidden="true" style={{ fontSize: "14px", verticalAlign: "-2px", marginRight: "5px" }} />}
              {label}
            </button>
          ))}
        </div>

        {/* 서브탭 — 점검 대상 */}
        <div style={{ padding: "10px 16px", display: "flex", gap: "8px", flexWrap: "wrap", borderBottom: "1px solid #f1f5f9" }}>
          {targetOptions.map((t) => (
            <button key={t} onClick={() => setActiveTarget(t)} style={subTabStyle(activeTarget === t)}>
              {t}
            </button>
          ))}
        </div>

        {/* 검색 */}
        <div style={{ padding: "10px 16px" }}>
          <div style={{ position: "relative" }}>
            <i className="ti ti-search" aria-hidden="true" style={{ position: "absolute", left: "10px", top: "50%", transform: "translateY(-50%)", fontSize: "15px", color: "#94a3b8" }} />
            <input
              placeholder="항목 코드 또는 항목명 검색"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{
                width: "100%", padding: "7px 10px 7px 32px",
                border: "1px solid #e2e8f0", borderRadius: "6px",
                fontSize: "13px", boxSizing: "border-box",
                backgroundColor: "#f8fafc",
              }}
            />
          </div>
        </div>
      </div>

      {/* 테이블 */}
      <div style={cardStyle}>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
            <thead>
              <tr style={{ backgroundColor: "#f8fafc" }}>
                {["코드", "항목명", "분류", "점검 대상", "위험도", "점검방법"].map((h) => (
                  <th key={h} style={{
                    padding: "10px 14px", textAlign: "left",
                    borderBottom: "1px solid #e2e8f0",
                    fontSize: "11px", fontWeight: "500", color: "#64748b",
                    whiteSpace: "nowrap",
                  }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={6} style={{ padding: "32px", textAlign: "center", color: "#94a3b8", fontSize: "14px" }}>
                    항목이 없습니다
                  </td>
                </tr>
              ) : filtered.map((item) => {
                const stdStyle = STANDARD_STYLE[item.standard];
                const displayTarget = item.standard === "클라우드"
                  ? item.target.replace("클라우드-", "")
                  : item.target;
                const tColor = targetColorMap[item.target] || TARGET_COLORS[0];

                return (
                  <tr key={item.id} style={{ borderBottom: "1px solid #f1f5f9" }}>
                    <td style={{ padding: "10px 14px", fontWeight: "500", whiteSpace: "nowrap" }}>{item.code}</td>
                    <td style={{ padding: "10px 14px" }}>{item.title}</td>
                    <td style={{ padding: "10px 14px", color: "#64748b", fontSize: "12px", whiteSpace: "nowrap" }}>{item.category}</td>
                    <td style={{ padding: "10px 14px" }}>
                      <div style={{ display: "flex", gap: "4px", flexWrap: "wrap" }}>
                        {stdStyle && (
                          <span style={{
                            fontSize: "11px", padding: "2px 7px", borderRadius: "4px",
                            background: stdStyle.bg, color: stdStyle.color, whiteSpace: "nowrap",
                          }}>
                            {stdStyle.label}
                          </span>
                        )}
                        <span style={{
                          fontSize: "11px", padding: "2px 7px", borderRadius: "4px",
                          background: tColor.bg, color: tColor.color, whiteSpace: "nowrap",
                        }}>
                          {displayTarget}
                        </span>
                      </div>
                    </td>
                    <td style={{ padding: "10px 14px", textAlign: "center" }}>
                      <span style={{
                        fontSize: "11px", padding: "2px 8px", borderRadius: "20px",
                        backgroundColor: SEVERITY_COLOR[item.severity]?.bg,
                        color: SEVERITY_COLOR[item.severity]?.text,
                      }}>{item.severity}</span>
                    </td>
                    <td style={{ padding: "10px 14px", textAlign: "center" }}>
                      <span style={{
                        fontSize: "11px", padding: "2px 8px", borderRadius: "20px",
                        backgroundColor: METHOD_COLOR[item.check_method]?.bg,
                        color: METHOD_COLOR[item.check_method]?.text,
                      }}>{item.check_method}</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default ChecklistPage;
