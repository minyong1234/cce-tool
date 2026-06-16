// src/pages/Dashboard.jsx
// 점검 결과 통계 대시보드

import { useEffect, useState } from "react";
import {
  PieChart, Pie, Cell, Tooltip, Legend,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer
} from "recharts";
import { getResults, getAssets, getChecklists } from "../api";

const COLORS = {
  Y:       "#22c55e",
  N:       "#ef4444",
  "N/A":   "#94a3b8",
  PENDING: "#f59e0b",
};

const STANDARD_STYLE = {
  "기반시설": { bg: "#EEEDFE", color: "#3C3489", label: "주요정보통신기반" },
  "클라우드": { bg: "#FAEEDA", color: "#633806", label: "클라우드" },
};

const TARGET_STYLE = { bg: "#E6F1FB", color: "#0C447C" };

function Dashboard() {
  const [results,    setResults]    = useState([]);
  const [assets,     setAssets]     = useState([]);
  const [checklists, setChecklists] = useState([]);
  const [loading,    setLoading]    = useState(true);

  useEffect(() => {
    Promise.all([getResults(), getAssets(), getChecklists()])
      .then(([rRes, aRes, cRes]) => {
        setResults(rRes.data);
        setAssets(aRes.data);
        setChecklists(cRes.data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>로딩 중...</p>;

  const checklistMap = {};
  checklists.forEach((c) => {
    checklistMap[c.code] = { standard: c.standard, target: c.target };
  });

  const total   = results.length;
  const safe    = results.filter((r) => r.result === "Y").length;
  const vuln    = results.filter((r) => r.result === "N").length;
  const na      = results.filter((r) => r.result === "N/A").length;
  const pending = results.filter((r) => r.result === "PENDING").length;

  const pieData = [
    { name: "양호(Y)",       value: safe,    color: COLORS.Y },
    { name: "취약(N)",       value: vuln,    color: COLORS.N },
    { name: "해당없음(N/A)", value: na,      color: COLORS["N/A"] },
    { name: "미확인",        value: pending, color: COLORS.PENDING },
  ];

  const barData = assets.map((asset) => {
    const ar = results.filter((r) => r.asset_id === asset.id);
    return {
      name:     asset.hostname || asset.code,
      양호:     ar.filter((r) => r.result === "Y").length,
      취약:     ar.filter((r) => r.result === "N").length,
      미확인:   ar.filter((r) => r.result === "PENDING").length,
      해당없음: ar.filter((r) => r.result === "N/A").length,
    };
  });

  const assetRows = assets.map((asset) => {
    const ar = results.filter((r) => r.asset_id === asset.id);
    const firstCode = ar[0]?.checklist_code;
    const meta = firstCode ? checklistMap[firstCode] : null;
    const createdAt = asset.created_at
      ? new Date(asset.created_at).toLocaleDateString("ko-KR", {
          year: "numeric", month: "2-digit", day: "2-digit",
        })
      : "-";
    return {
      id:       asset.id,
      hostname: asset.hostname || asset.code,
      ip:       asset.ip,
      standard: meta?.standard ?? null,
      target:   meta?.target   ?? null,
      safe:     ar.filter((r) => r.result === "Y").length,
      vuln:     ar.filter((r) => r.result === "N").length,
      pending:  ar.filter((r) => r.result === "PENDING").length,
      na:       ar.filter((r) => r.result === "N/A").length,
      createdAt,
    };
  });

  const cardStyle = {
    backgroundColor: "white",
    borderRadius: "12px",
    padding: "20px",
    boxShadow: "0 1px 4px rgba(0,0,0,0.08)",
  };

  const headerCellStyle = {
    fontSize: "11px",
    fontWeight: "500",
    color: "#64748b",
    padding: "8px 12px",
  };

  const cellStyle = {
    fontSize: "13px",
    padding: "10px 12px",
    verticalAlign: "middle",
  };

  return (
    <div>
      <h1 style={{ fontSize: "22px", marginBottom: "24px" }}>대시보드</h1>

      {/* 요약 카드 */}
      <div style={{ display: "flex", gap: "16px", marginBottom: "32px", flexWrap: "wrap" }}>
        {[
          { label: "자산 총 수량",  value: assets.length, color: "#7c3aed" },
          { label: "양호",          value: safe,           color: "#22c55e" },
          { label: "취약",          value: vuln,           color: "#ef4444" },
          { label: "미확인",        value: pending,        color: "#f59e0b" },
          { label: "해당없음(N/A)", value: na,             color: "#94a3b8" },
        ].map((card) => (
          <div key={card.label} style={{
            flex: "1", minWidth: "120px",
            backgroundColor: "white",
            borderRadius: "12px",
            padding: "20px",
            boxShadow: "0 1px 4px rgba(0,0,0,0.08)",
            borderTop: `4px solid ${card.color}`,
          }}>
            <p style={{ margin: "0 0 8px", fontSize: "13px", color: "#64748b" }}>
              {card.label}
            </p>
            <p style={{ margin: 0, fontSize: "28px", fontWeight: "bold", color: card.color }}>
              {card.value}
            </p>
          </div>
        ))}
      </div>

      {/* 차트 영역 */}
      <div style={{ display: "flex", gap: "24px", flexWrap: "wrap", marginBottom: "32px" }}>

        {/* 파이 차트 */}
        <div style={{ flex: "1", minWidth: "300px", ...cardStyle }}>
          <h3 style={{ margin: "0 0 16px", fontSize: "15px" }}>전체 결과 비율</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80}>
                {pieData.map((entry) => (
                  <Cell key={entry.name} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* 바 차트 */}
        {barData.length > 0 && (
          <div style={{ flex: "2", minWidth: "300px", ...cardStyle }}>
            <h3 style={{ margin: "0 0 16px", fontSize: "15px" }}>자산별 점검 결과</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={barData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" fontSize={12} />
                <YAxis fontSize={12} />
                <Tooltip />
                <Legend />
                <Bar dataKey="양호"     fill="#22c55e" />
                <Bar dataKey="취약"     fill="#ef4444" />
                <Bar dataKey="미확인"   fill="#f59e0b" />
                <Bar dataKey="해당없음" fill="#94a3b8" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* 자산별 점검 현황 리스트 */}
      <div style={cardStyle}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "16px" }}>
          <h3 style={{ margin: 0, fontSize: "15px" }}>자산별 점검 현황</h3>
          <span style={{ fontSize: "13px", color: "#64748b" }}>총 {assets.length}개 자산</span>
        </div>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
            <thead>
              <tr style={{ backgroundColor: "#f8fafc" }}>
                {["자산명", "IP", "점검 유형", "양호", "취약", "미확인", "해당없음", "등록일"].map((h) => (
                  <th key={h} style={{
                    ...headerCellStyle,
                    textAlign: ["양호","취약","미확인","해당없음"].includes(h) ? "center" : "left",
                    whiteSpace: "nowrap"
                  }}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {assetRows.map((row, i) => {
                const stdStyle = row.standard ? STANDARD_STYLE[row.standard] : null;
                return (
                  <tr key={row.id} style={{ borderTop: i === 0 ? "none" : "1px solid #f1f5f9" }}>
                    <td style={{ ...cellStyle, fontWeight: "500" }}>{row.hostname}</td>
                    <td style={{ ...cellStyle, color: "#64748b" }}>{row.ip}</td>
                    <td style={{ ...cellStyle }}>
                      <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
                        {stdStyle && (
                          <span style={{
                            fontSize: "11px", padding: "2px 8px", borderRadius: "4px",
                            background: stdStyle.bg, color: stdStyle.color, whiteSpace: "nowrap",
                          }}>
                            {stdStyle.label}
                          </span>
                        )}
                        {row.target && (
                          <span style={{
                            fontSize: "11px", padding: "2px 8px", borderRadius: "4px",
                            background: TARGET_STYLE.bg, color: TARGET_STYLE.color, whiteSpace: "nowrap",
                          }}>
                            {row.target}
                          </span>
                        )}
                        {!stdStyle && !row.target && (
                          <span style={{ fontSize: "12px", color: "#94a3b8" }}>-</span>
                        )}
                      </div>
                    </td>
                    <td style={{ ...cellStyle, textAlign: "center", color: "#15803d", fontWeight: "500" }}>{row.safe}</td>
                    <td style={{ ...cellStyle, textAlign: "center", color: "#b91c1c", fontWeight: "500" }}>{row.vuln}</td>
                    <td style={{ ...cellStyle, textAlign: "center", color: "#b45309", fontWeight: "500" }}>{row.pending}</td>
                    <td style={{ ...cellStyle, textAlign: "center", color: "#64748b" }}>{row.na}</td>
                    <td style={{ ...cellStyle, color: "#64748b", whiteSpace: "nowrap" }}>{row.createdAt}</td>
                  </tr>
                );
              })}
              {assetRows.length === 0 && (
                <tr>
                  <td colSpan={8} style={{ textAlign: "center", padding: "32px", color: "#94a3b8", fontSize: "14px" }}>
                    등록된 자산이 없습니다
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
