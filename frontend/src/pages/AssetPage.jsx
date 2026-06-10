// src/pages/AssetPage.jsx
// 자산 관리 페이지 — 자산 등록, 목록 조회, 삭제

import { useEffect, useState } from "react";
import { getAssets, createAsset, deleteAsset } from "../api";

// 빈 자산 폼 초기값
const EMPTY_FORM = {
  code: "", hostname: "", ip: "",
  os: "", version: "", purpose: "",
  location: "", manager: "",
};

function AssetPage() {
  const [assets, setAssets]   = useState([]);
  const [form, setForm]       = useState(EMPTY_FORM);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving]   = useState(false);

  // 자산 목록 불러오기
  const fetchAssets = () => {
    getAssets()
      .then((res) => setAssets(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchAssets(); }, []);

  // 입력값 변경 처리
  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  // 자산 등록
  const handleSubmit = async () => {
    if (!form.code || !form.hostname || !form.ip) {
      alert("자산 코드, 호스트명, IP는 필수 입력입니다.");
      return;
    }
    setSaving(true);
    try {
      await createAsset(form);
      setForm(EMPTY_FORM);
      fetchAssets();
    } catch (e) {
      alert("자산 등록 실패: " + e.message);
    } finally {
      setSaving(false);
    }
  };

  // 자산 삭제
  const handleDelete = async (id) => {
    if (!window.confirm("삭제하시겠습니까?")) return;
    await deleteAsset(id);
    fetchAssets();
  };

  // 입력 필드 목록
  const fields = [
    { name: "code",     label: "자산 코드 *",  placeholder: "U_001" },
    { name: "hostname", label: "호스트명 *",    placeholder: "web-server-01" },
    { name: "ip",       label: "IP 주소 *",    placeholder: "192.168.0.1" },
    { name: "os",       label: "OS",           placeholder: "Ubuntu 22.04" },
    { name: "version",  label: "버전",          placeholder: "22.04" },
    { name: "purpose",  label: "용도",          placeholder: "웹 서버" },
    { name: "location", label: "설치 위치",     placeholder: "서울 IDC" },
    { name: "manager",  label: "담당자",        placeholder: "홍길동" },
  ];

  return (
    <div>
      <h1 style={{ fontSize: "22px", marginBottom: "24px" }}>자산 관리</h1>

      {/* 자산 등록 폼 */}
      <div style={{
        backgroundColor: "white", borderRadius: "12px",
        padding: "20px", marginBottom: "24px",
        boxShadow: "0 1px 4px rgba(0,0,0,0.08)"
      }}>
        <h3 style={{ margin: "0 0 16px", fontSize: "15px" }}>자산 등록</h3>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "12px" }}>
          {fields.map((f) => (
            <div key={f.name}>
              <label style={{ fontSize: "12px", color: "#64748b", display: "block", marginBottom: "4px" }}>
                {f.label}
              </label>
              <input
                name={f.name}
                value={form[f.name]}
                onChange={handleChange}
                placeholder={f.placeholder}
                style={{
                  width: "100%", padding: "8px 10px",
                  border: "1px solid #e2e8f0", borderRadius: "6px",
                  fontSize: "13px", boxSizing: "border-box"
                }}
              />
            </div>
          ))}
        </div>
        <button
          onClick={handleSubmit}
          disabled={saving}
          style={{
            marginTop: "16px", padding: "10px 24px",
            backgroundColor: "#3b82f6", color: "white",
            border: "none", borderRadius: "6px",
            fontSize: "14px", cursor: "pointer"
          }}
        >
          {saving ? "등록 중..." : "자산 등록"}
        </button>
      </div>

      {/* 자산 목록 테이블 */}
      <div style={{
        backgroundColor: "white", borderRadius: "12px",
        padding: "20px", boxShadow: "0 1px 4px rgba(0,0,0,0.08)"
      }}>
        <h3 style={{ margin: "0 0 16px", fontSize: "15px" }}>자산 목록</h3>
        {loading ? <p>로딩 중...</p> : (
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
            <thead>
              <tr style={{ backgroundColor: "#f8fafc" }}>
                {["코드", "호스트명", "IP", "OS", "용도", "담당자", "삭제"].map((h) => (
                  <th key={h} style={{ padding: "10px 12px", textAlign: "left", borderBottom: "1px solid #e2e8f0", color: "#64748b" }}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {assets.length === 0 ? (
                <tr><td colSpan={7} style={{ padding: "20px", textAlign: "center", color: "#94a3b8" }}>등록된 자산이 없습니다</td></tr>
              ) : assets.map((a) => (
                <tr key={a.id} style={{ borderBottom: "1px solid #f1f5f9" }}>
                  <td style={{ padding: "10px 12px" }}>{a.code}</td>
                  <td style={{ padding: "10px 12px" }}>{a.hostname}</td>
                  <td style={{ padding: "10px 12px" }}>{a.ip}</td>
                  <td style={{ padding: "10px 12px" }}>{a.os}</td>
                  <td style={{ padding: "10px 12px" }}>{a.purpose}</td>
                  <td style={{ padding: "10px 12px" }}>{a.manager}</td>
                  <td style={{ padding: "10px 12px" }}>
                    <button
                      onClick={() => handleDelete(a.id)}
                      style={{
                        padding: "4px 10px", backgroundColor: "#fee2e2",
                        color: "#ef4444", border: "none",
                        borderRadius: "4px", cursor: "pointer", fontSize: "12px"
                      }}
                    >삭제</button>
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

export default AssetPage;
