// 텍스트를 HTML로 변환 (줄바꿈 및 마크다운 처리)
function formatTextWithLineBreaks(text) {
  if (!text) return "";

  // 줄 단위로 분리
  const lines = text.split("\n");
  const processedLines = [];
  let inList = false;
  let prevLineType = null; // 이전 줄의 타입 (heading, list, text, empty)

  for (let i = 0; i < lines.length; i++) {
    let line = lines[i];
    const isBlank = !line.trim();

    // HTML 특수 문자 이스케이프 (마크다운 변환 전에 처리)
    const escaped = line.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");

    // 마크다운 헤딩 처리 (#, ##, ###) - 순서 중요: ###, ##, # 순서로 체크
    if (escaped.startsWith("### ")) {
      if (inList) {
        processedLines.push("</ul>");
        inList = false;
      }
      // 이전 줄이 텍스트였으면 줄바꿈 추가
      if (prevLineType === "text" && i > 0) {
        processedLines.push("<br>");
      }
      const content = escaped.replace(/^###\s+/, "");
      processedLines.push(`<h3>${content}</h3>`);
      prevLineType = "heading";
    } else if (escaped.startsWith("## ")) {
      if (inList) {
        processedLines.push("</ul>");
        inList = false;
      }
      if (prevLineType === "text" && i > 0) {
        processedLines.push("<br>");
      }
      const content = escaped.replace(/^##\s+/, "");
      processedLines.push(`<h2>${content}</h2>`);
      prevLineType = "heading";
    } else if (escaped.startsWith("# ") && !escaped.startsWith("##")) {
      // # 로 시작하지만 ##나 ###가 아닌 경우만
      if (inList) {
        processedLines.push("</ul>");
        inList = false;
      }
      if (prevLineType === "text" && i > 0) {
        processedLines.push("<br>");
      }
      const content = escaped.replace(/^#\s+/, "");
      processedLines.push(`<h1>${content}</h1>`);
      prevLineType = "heading";
    }
    // 리스트 항목 처리 (-)
    else if (escaped.match(/^-\s+/)) {
      if (!inList) {
        // 이전 줄이 텍스트였으면 줄바꿈 추가
        if (prevLineType === "text" && i > 0) {
          processedLines.push("<br>");
        }
        processedLines.push("<ul>");
        inList = true;
      }
      const content = escaped.replace(/^-\s+/, "");
      // **텍스트** 처리
      const boldContent = content.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
      processedLines.push(`<li>${boldContent}</li>`);
      prevLineType = "list";
    }
    // 빈 줄 처리
    else if (isBlank) {
      if (inList) {
        processedLines.push("</ul>");
        inList = false;
      }
      // 이전 줄이 빈 줄이 아니었으면 줄바꿈 추가
      if (prevLineType !== "empty" && prevLineType !== null) {
        processedLines.push("<br>");
      }
      prevLineType = "empty";
    }
    // 일반 텍스트
    else {
      if (inList) {
        processedLines.push("</ul>");
        inList = false;
      }
      // 이전 줄이 텍스트였으면 줄바꿈 추가
      if (prevLineType === "text" && i > 0) {
        processedLines.push("<br>");
      }
      // **텍스트** 처리
      const boldContent = escaped.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
      processedLines.push(boldContent);
      prevLineType = "text";
    }
  }

  // 리스트가 열려있으면 닫기
  if (inList) {
    processedLines.push("</ul>");
  }

  return processedLines.join("");
}
