// src/api/index.js
// 백엔드 API 호출 함수 모음
// axios를 사용해서 api-gateway를 통해 각 서비스에 요청

import axios from "axios";

// api-gateway 주소
// 개발 중: 서버 공인 IP, 배포 후: 같은 도메인
const BASE_URL = import.meta.env.VITE_API_URL || "http://27.96.146.162/";

const api = axios.create({
  baseURL: BASE_URL + "/api",  // ← /api prefix 추가
  timeout: 10000,
});

// ── 점검 항목 API ─────────────────────────────
export const getChecklists = () =>
  api.get("/checklists/");

export const getChecklistsByTarget = (target) =>
  api.get(`/checklists/?target=${target}`);

// ── 자산 API ──────────────────────────────────
export const getAssets = () =>
  api.get("/assets/");

export const createAsset = (data) =>
  api.post("/assets/", data);

export const deleteAsset = (id) =>
  api.delete(`/assets/${id}`);

// ── 점검 결과 API ─────────────────────────────
export const getResults = () =>
  api.get("/results/");

export const getResultsByAsset = (assetId) =>
  api.get(`/results/asset/${assetId}`);

export const updateResult = (resultId, data) =>
  api.put(`/results/${resultId}`, data);

// ── 점검 실행 API ─────────────────────────────
export const uploadScanResult = (assetId, file) => {
  // 파일 업로드는 FormData 형식으로 전송
  const formData = new FormData();
  formData.append("asset_id", assetId);
  formData.append("file", file);
  return api.post("/scan/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const downloadScript = () =>
  `${BASE_URL}/scan/scripts/linux`;

// ── 리포트 API ────────────────────────────────
export const downloadExcelReport = (assetId) =>
  `${BASE_URL}/report/excel/${assetId}`;

export const downloadPdfReport = (assetId) =>
  `${BASE_URL}/report/pdf/${assetId}`;
