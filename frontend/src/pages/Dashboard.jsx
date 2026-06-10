// src/pages/Dashboard.jsx
// 점검 결과 통계 대시보드

import { useEffect, useState } from "react";
import {
  PieChart, Pie, Cell, Tooltip, Legend,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer
} from "recharts";
import { getResults, getAssets } from "../api";

// 결과값별 색상
const COLORS = {
  Y:       "#22c55e",  // 양호 — 초록
  N:       "#ef4444",  // 취약 — 빨강
  "N/A":   "#94a3b8",  // 해당없음 — 회색
  PENDING: "#f59e0b",  // 미확인 — 노랑
};

function Dashboard() {
  const [results, setResults]   = useState([]);
  const [assets, setAssets]     = useState([]);
  const [loading, setLoading]   = useState(true);

  useEffect(() => {
    // 컴포넌트가 마운트될 때 데이터 불러오기
    Promise.all([getResults(), getAssets()])
      .then(([resultsRes, assetsRes]) => {
        setResults(resultsRes.data);
        setAssets(assetsRes.data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>로딩 중...</p>;

  // 전체 결과 통계 계산
  const total   = results.length;
  const safe    = results.filter((r) => r.result === "Y").length;
  const vuln    = results.filter((r) => r.result === "N").length;
  const na      = results.filter((r) => r.result === "N/A").length;
  const pending = results.filter((r) => r.result === "PENDING").length;

  // 파이 차트 데이터
  const pieData = [
    { name: "양호(Y)",       value: safe,    color: COLORS.Y },
    { name: "취약(N)",       value: vuln,    color: COLORS.N },
    { name: "해당없음(N/A)", value: na,      color: COLORS["N/A"] },
    { name: "미확인",        value: pending, color: COLORS.PENDING },
  ].filter((d) => d.value > 0);

  // 자산별 취약 항목 수 바 차트 데이터
  const barData = assets.map((asset) => {
    const assetResults = results.filter((r) => r.asset_id === asset.id);
    return {
      name: asset.hostname || asset.code,
      취약: assetResults.filter((r) => r.result === "N").length,
      양호: assetResults.filter((r) => r.result === "Y").length,
      미확인: assetResults.filter((r) => r.result === "PENDING").length,
    };
  });

  return (
    <div>
      <h1 style={{ fontSize: "22px", marginBottom: "24px" }}>대시보드</h1>

      {/* 요약 카드 */}
      <div style={{ display: "flex", gap: "16px", marginBottom: "32px", flexWrap: "wrap" }}>
        {[
          { label: "전체 항목",  value: total,   color: "#3b82f6" },
          { label: "양호",       value: safe,    color: "#22c55e" },
          { label: "취약",       value: vuln,    color: "#ef4444" },
          { label: "미확인",     value: pending, color: "#f59e0b" },
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
      <div style={{ display: "flex", gap: "24px", flexWrap: "wrap" }}>

        {/* 파이 차트 */}
        <div style={{
          flex: "1", minWidth: "300px",
          backgroundColor: "white", borderRadius: "12px",
          padding: "20px", boxShadow: "0 1px 4px rgba(0,0,0,0.08)"
        }}>
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
          <div style={{
            flex: "2", minWidth: "300px",
            backgroundColor: "white", borderRadius: "12px",
            padding: "20px", boxShadow: "0 1px 4px rgba(0,0,0,0.08)"
          }}>
            <h3 style={{ margin: "0 0 16px", fontSize: "15px" }}>자산별 점검 결과</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={barData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" fontSize={12} />
                <YAxis fontSize={12} />
                <Tooltip />
                <Legend />
                <Bar dataKey="양호"  fill="#22c55e" />
                <Bar dataKey="취약"  fill="#ef4444" />
                <Bar dataKey="미확인" fill="#f59e0b" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

      </div>
    </div>
  );
}

export default Dashboard;
