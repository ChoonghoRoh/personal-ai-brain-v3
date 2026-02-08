// 1) 이전 Execute Command 노드의 stdout(파일 목록 문자열)

const stdout = String($node["CMD_ListPhaseFiles"].json.stdout || "");
const rulesText = String($node["CMD_LoadPhaseRules"].json.stdout || "");
const hasRules = rulesText && !/(MISSING)/.test(rulesText);


// 2) 줄 단위로 파일명 배열
const files = stdout
  .split("\n")
  .map(s => s.trim())
  .filter(Boolean);

// 3) phaseFileBase 가져오기 (SET_PhaseId에서 넘겨준 값)
const phaseFileBase = String($node["SET_PhaseId"].json.phaseFileBase || "").trim();

// 4) 정규식 헬퍼
const escRe = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const base = escRe(phaseFileBase);

const hasRe = (re) => files.some(f => re.test(f));

// 5) 네 규칙 반영한 패턴들
const RE_PLAN  = new RegExp(`^${base}-plan\\.md$`);
const RE_TODO  = new RegExp(`^${base}-todo-list\\.md$`);
const RE_FINAL = new RegExp(`^${base}-final-summary-report\\.md$`);

// task change/test: ^phaseFileBase(-[0-9]+)?-.*-(change-report|test-report)\.md$
const RE_TASK_REPORT = new RegExp(`^${base}(-[0-9]+)?-.*-(change-report|test-report)\\.md$`);

// (선택) 체크리스트/유저테스트 결과도 base 기준으로 묶고 싶으면 아래처럼
const RE_CHECKLIST = new RegExp(`^${base}(-[0-9]+)?-.*-(user-test-checklist|test-checklist)\\.md$`);

const RE_USER_TEST_RESULTS = new RegExp(`^${base}(-[0-9]+)?(-.*)?-user-test-results\\.md$`);
// 6) 결과
const result = {
  files,
  phaseFileBase,

  hasPlan: hasRe(RE_PLAN),
  hasTodo: hasRe(RE_TODO),
  hasChecklist: hasRe(RE_CHECKLIST),
  hasUserTestResults: hasRe(RE_USER_TEST_RESULTS),

  hasFinalSummary: hasRe(RE_FINAL),
  needFinalSummary: hasRe(RE_USER_TEST_RESULTS) && !hasRe(RE_FINAL),

  hasTaskReports: hasRe(RE_TASK_REPORT),

  // ✅ 추가
  hasRules,
  rulesText,
};

return [{ json: result }];
