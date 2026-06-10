// src/components/Sidebar.jsx
// 왼쪽 사이드 메뉴

import { NavLink } from "react-router-dom";

// 메뉴 목록 정의
const menus = [
  { path: "/dashboard",  label: "대시보드",       icon: "📊" },
  { path: "/assets",     label: "자산 관리",       icon: "🖥️" },
  { path: "/checklists", label: "점검 항목",       icon: "📋" },
  { path: "/scan",       label: "점검 실행",       icon: "🔍" },
  { path: "/report",     label: "리포트",          icon: "📄" },
];

function Sidebar() {
  return (
    <nav style={{
      width: "220px",
      minHeight: "100vh",
      backgroundColor: "#1e293b",
      color: "white",
      padding: "24px 0",
      flexShrink: 0,
    }}>

      {/* 로고 */}
      <div style={{ padding: "0 20px 24px", borderBottom: "1px solid #334155" }}>
        <h2 style={{ margin: 0, fontSize: "16px", color: "#38bdf8" }}>
          CCE 취약점 점검 툴
        </h2>
      </div>

      {/* 메뉴 목록 */}
      <ul style={{ listStyle: "none", padding: "12px 0", margin: 0 }}>
        {menus.map((menu) => (
          <li key={menu.path}>
            <NavLink
              to={menu.path}
              style={({ isActive }) => ({
                display: "flex",
                alignItems: "center",
                gap: "10px",
                padding: "12px 20px",
                color: isActive ? "#38bdf8" : "#cbd5e1",
                backgroundColor: isActive ? "#0f172a" : "transparent",
                textDecoration: "none",
                fontSize: "14px",
                borderLeft: isActive ? "3px solid #38bdf8" : "3px solid transparent",
              })}
            >
              <span>{menu.icon}</span>
              <span>{menu.label}</span>
            </NavLink>
          </li>
        ))}
      </ul>

    </nav>
  );
}

export default Sidebar;
