/**
 * Ollama(로컬 LLM) 모델 목록 공통 모듈
 * /api/system/status 의 gpt4all(Ollama) 정보로 select 요소를 채움.
 * exaone 계열은 목록에서 제외 (공통 정책).
 */

/**
 * API에서 받은 모델 목록에서 제외할 패턴 (exaone 제거)
 */
const DEFAULT_EXCLUDE_PATTERN = /exaone/i;

/**
 * Ollama 모델 목록을 /api/system/status에서 가져와 지정한 select에 채움
 * 기본 옵션은 "모델명 (기본)" 형태로, 실제 모델 목록에 있는 이름으로 표기
 * @param {string} selectId - select 요소 id (예: "reason-model", "keyword-suggestion-model")
 * @param {Object} [options] - 옵션
 * @param {RegExp|boolean} [options.excludePattern] - 제외할 모델명 패턴. true면 exaone 제외, false면 제외 없음
 */
async function loadOllamaModelOptions(selectId, options = {}) {
  const select = document.getElementById(selectId);
  if (!select) return;
  const excludePattern = options.excludePattern === false ? null : options.excludePattern || DEFAULT_EXCLUDE_PATTERN;
  try {
    const res = await fetch("/api/system/status");
    const data = await res.json();
    let models = data.gpt4all?.models || [];
    if (excludePattern && typeof excludePattern.test === "function") {
      models = models.filter((m) => m && !excludePattern.test(String(m)));
    }
    const envDefault = (data.gpt4all?.model_name || "").trim();
    const envDefaultInList = envDefault && !DEFAULT_EXCLUDE_PATTERN.test(envDefault) && models.includes(envDefault);
    const displayDefaultName = envDefaultInList ? envDefault : models[0] || "";
    const firstOpt = select.options[0];
    if (firstOpt) {
      firstOpt.textContent = displayDefaultName ? `${displayDefaultName} (기본)` : "기본";
    }
    const existing = new Set();
    for (let i = 0; i < select.options.length; i++) {
      existing.add(select.options[i].value);
    }
    models.forEach(function (m) {
      if (!m || existing.has(m)) return;
      if (displayDefaultName && m === displayDefaultName) return;
      existing.add(m);
      const opt = document.createElement("option");
      opt.value = m;
      opt.textContent = m;
      select.appendChild(opt);
    });
  } catch (e) {
    console.debug("Ollama 모델 목록 로드 실패:", e);
  }
}
