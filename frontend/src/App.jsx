// src/App.jsx
// 페이지 라우팅 설정
// React Router를 사용해서 URL에 따라 다른 페이지를 보여줌

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import ChecklistPage from "./pages/ChecklistPage";
import AssetPage from "./pages/AssetPage";
import ScanPage from "./pages/ScanPage";
import ReportPage from "./pages/ReportPage";

function App() {
  return (
    <BrowserRouter>
      <div style={{ display: "flex", minHeight: "100vh" }}>

        {/* 왼쪽 사이드바 */}
        <Sidebar />

        {/* 오른쪽 메인 콘텐츠 */}
        <main style={{ flex: 1, padding: "24px", backgroundColor: "#f5f7fa" }}>
          <Routes>
            {/* 기본 경로는 대시보드로 이동 */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard"  element={<Dashboard />} />
            <Route path="/checklists" element={<ChecklistPage />} />
            <Route path="/assets"     element={<AssetPage />} />
            <Route path="/scan"       element={<ScanPage />} />
            <Route path="/report"     element={<ReportPage />} />
          </Routes>
        </main>

      </div>
    </BrowserRouter>
  );
}

export default App;
