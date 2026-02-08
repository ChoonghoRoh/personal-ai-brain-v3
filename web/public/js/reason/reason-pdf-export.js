/**
 * Reasoning Lab — PDF Export (Phase 10-3-3)
 * html2canvas + jsPDF를 이용한 결과 영역 PDF 내보내기.
 * 의존성: html2canvas, jsPDF (CDN)
 */
(function () {
  "use strict";

  /**
   * Reasoning 결과 영역을 PDF로 내보내기
   */
  async function exportResultsPDF() {
    var content = document.getElementById("results-content");
    if (!content || content.style.display === "none") {
      alert("내보낼 결과가 없습니다. Reasoning을 먼저 실행해 주세요.");
      return;
    }

    if (typeof html2canvas === "undefined" || typeof jspdf === "undefined") {
      alert("PDF 내보내기 라이브러리가 로드되지 않았습니다.");
      return;
    }

    var btn = document.getElementById("export-pdf-btn");
    var originalText = btn ? btn.textContent : "";
    if (btn) {
      btn.disabled = true;
      btn.textContent = "PDF 생성 중...";
    }

    try {
      // 툴바 숨기기 (PDF에 포함하지 않음)
      var toolbar = content.querySelector(".results-toolbar");
      if (toolbar) toolbar.style.display = "none";

      // details 요소들 모두 열기
      var detailsEls = content.querySelectorAll("details");
      var detailsStates = [];
      detailsEls.forEach(function (d) {
        detailsStates.push(d.open);
        d.open = true;
      });

      // 11-5-5: 다크 모드 PDF 대응 — 현재 테마에 맞는 배경색
      var isDark = document.documentElement.getAttribute("data-theme") === "dark";
      var bgColor = isDark ? "#1e293b" : "#ffffff";

      var canvas = await html2canvas(content, {
        scale: 2,
        useCORS: true,
        logging: false,
        backgroundColor: bgColor,
        windowWidth: content.scrollWidth,
      });

      // details 원래 상태 복원
      detailsEls.forEach(function (d, i) {
        d.open = detailsStates[i];
      });

      // 툴바 복원
      if (toolbar) toolbar.style.display = "";

      var imgData = canvas.toDataURL("image/png");
      var pdf = new jspdf.jsPDF({
        orientation: "portrait",
        unit: "mm",
        format: "a4",
      });

      var pageWidth = pdf.internal.pageSize.getWidth();
      var pageHeight = pdf.internal.pageSize.getHeight();
      var margin = 10;
      var contentWidth = pageWidth - margin * 2;
      var imgWidth = contentWidth;
      var imgHeight = (canvas.height * imgWidth) / canvas.width;

      // 여러 페이지 처리
      var yOffset = 0;
      var availableHeight = pageHeight - margin * 2;

      if (imgHeight <= availableHeight) {
        pdf.addImage(imgData, "PNG", margin, margin, imgWidth, imgHeight);
      } else {
        var totalPages = Math.ceil(imgHeight / availableHeight);
        for (var page = 0; page < totalPages; page++) {
          if (page > 0) pdf.addPage();
          var sourceY = (page * availableHeight * canvas.width) / imgWidth;
          var sourceHeight = (availableHeight * canvas.width) / imgWidth;
          if (sourceY + sourceHeight > canvas.height) {
            sourceHeight = canvas.height - sourceY;
          }

          var pageCanvas = document.createElement("canvas");
          pageCanvas.width = canvas.width;
          pageCanvas.height = sourceHeight;
          var ctx = pageCanvas.getContext("2d");
          ctx.drawImage(canvas, 0, sourceY, canvas.width, sourceHeight, 0, 0, canvas.width, sourceHeight);

          var pageImgData = pageCanvas.toDataURL("image/png");
          var pageImgHeight = (sourceHeight * imgWidth) / canvas.width;
          pdf.addImage(pageImgData, "PNG", margin, margin, imgWidth, pageImgHeight);
        }
      }

      // 파일명 생성
      var now = new Date();
      var filename =
        "reasoning-result-" +
        now.getFullYear() +
        String(now.getMonth() + 1).padStart(2, "0") +
        String(now.getDate()).padStart(2, "0") +
        "-" +
        String(now.getHours()).padStart(2, "0") +
        String(now.getMinutes()).padStart(2, "0") +
        ".pdf";

      pdf.save(filename);
    } catch (err) {
      console.error("PDF 내보내기 실패:", err);
      alert("PDF 내보내기 중 오류가 발생했습니다: " + (err.message || err));
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.textContent = originalText;
      }
    }
  }

  window.exportResultsPDF = exportResultsPDF;
})();
