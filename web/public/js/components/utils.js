/**
 * 공통 유틸리티 함수 모듈
 * 여러 파일에서 중복 사용되는 공통 함수들을 모아둔 모듈
 */

/**
 * HTML 이스케이프 함수
 * XSS 공격을 방지하기 위해 사용자 입력 데이터를 이스케이프 처리
 * @param {string|null|undefined} text - 이스케이프할 텍스트
 * @returns {string} 이스케이프된 HTML 문자열
 */
function escapeHtml(text) {
  if (text == null) {
    return "";
  }
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

/**
 * 색상 코드 유효성 검사
 * @param {string} color - 검사할 색상 코드 (#RRGGBB 형식)
 * @returns {boolean} 유효한 색상 코드인지 여부
 */
function validateColorCode(color) {
  if (!color || typeof color !== "string") {
    return false;
  }
  return /^#[0-9A-Fa-f]{6}$/.test(color);
}

/**
 * 숫자 포맷팅
 * @param {number} num - 포맷팅할 숫자
 * @param {number} decimals - 소수점 자릿수 (기본값: 0)
 * @returns {string} 포맷팅된 숫자 문자열
 */
function formatNumber(num, decimals = 0) {
  if (num == null || isNaN(num)) {
    return "0";
  }
  return Number(num).toFixed(decimals);
}

/**
 * 날짜 포맷팅
 * @param {Date|string|number} date - 포맷팅할 날짜
 * @param {string} format - 포맷 형식 (기본값: "YYYY-MM-DD HH:mm:ss")
 * @returns {string} 포맷팅된 날짜 문자열
 */
function formatDate(date, format = "YYYY-MM-DD HH:mm:ss") {
  if (!date) {
    return "";
  }

  const d = date instanceof Date ? date : new Date(date);
  if (isNaN(d.getTime())) {
    return "";
  }

  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  const hours = String(d.getHours()).padStart(2, "0");
  const minutes = String(d.getMinutes()).padStart(2, "0");
  const seconds = String(d.getSeconds()).padStart(2, "0");

  return format
    .replace("YYYY", year)
    .replace("MM", month)
    .replace("DD", day)
    .replace("HH", hours)
    .replace("mm", minutes)
    .replace("ss", seconds);
}

/**
 * 배열 정리 (중복 제거, 빈 값 제거, 공백 제거)
 * @param {Array} arr - 정리할 배열
 * @returns {Array} 정리된 배열
 */
function cleanArray(arr) {
  if (!Array.isArray(arr)) {
    return [];
  }
  return Array.from(
    new Set(
      arr
        .map((item) => (typeof item === "string" ? item.trim() : String(item).trim()))
        .filter((item) => item.length > 0)
    )
  );
}

/**
 * HTML 이스케이프 (escapeHtml 단축 별칭)
 * @param {string|null|undefined} str - 이스케이프할 문자열
 * @returns {string} 이스케이프된 HTML 문자열
 */
function esc(str) {
  return escapeHtml(str);
}

/**
 * Authorization 헤더 생성 (토큰 있으면 추가)
 * @param {boolean} [includeContentType=true] - Content-Type 헤더 포함 여부
 * @returns {object} 헤더 객체
 */
function getAuthHeaders(includeContentType = true) {
  const headers = {};
  if (includeContentType) {
    headers["Content-Type"] = "application/json";
  }
  const token = localStorage.getItem("auth_token");
  if (token) {
    headers["Authorization"] = "Bearer " + token;
  }
  return headers;
}

/**
 * 바이트 크기를 읽기 쉬운 형식으로 변환
 * @param {number} bytes - 바이트 크기
 * @returns {string} 포맷된 문자열 (예: "1.50 MB")
 */
function formatFileSize(bytes) {
  if (!bytes || bytes === 0) return "0 B";
  const units = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return (bytes / Math.pow(1024, i)).toFixed(2) + " " + units[i];
}
