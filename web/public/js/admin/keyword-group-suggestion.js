/**
 * 키워드 그룹 추천 모듈
 * 설명 기반 키워드 추천 기능을 제공하는 클래스
 */
class KeywordGroupSuggestion {
  constructor(manager) {
    this.manager = manager; // KeywordGroupManager 인스턴스 참조
  }

  /**
   * 추천 키워드 초기화
   */
  clearSuggestedKeywords() {
    const container = document.getElementById(this.manager.suggestedKeywordsContainerId);
    const keywordsList = document.getElementById(this.manager.suggestedKeywordsListId);

    container.style.display = "none";
    keywordsList.innerHTML = "";
    this.manager.selectedSuggestedKeywords.clear();
  }

  /**
   * 설명 기반 키워드 추천
   */
  async suggestKeywordsFromDescription() {
    const description = document.getElementById(this.manager.groupDescriptionInputId).value.trim();
    const errorDiv = document.getElementById(this.manager.suggestionErrorId);
    const successDiv = document.getElementById(this.manager.suggestionSuccessId);

    if (errorDiv) {
      errorDiv.style.display = "none";
      errorDiv.textContent = "";
    }
    if (successDiv) {
      successDiv.style.display = "none";
      successDiv.textContent = "";
    }

    if (!description) {
      if (errorDiv) {
        errorDiv.textContent = "설명을 먼저 입력해주세요.";
        errorDiv.style.display = "block";
        setTimeout(() => {
          errorDiv.scrollIntoView({ behavior: "smooth", block: "nearest" });
        }, 100);
      } else {
        showError("설명을 먼저 입력해주세요.");
      }
      return;
    }

    const btn = document.getElementById("suggest-keywords-btn");
    const container = document.getElementById(this.manager.suggestedKeywordsContainerId);
    const keywordsList = document.getElementById(this.manager.suggestedKeywordsListId);

    btn.disabled = true;
    btn.textContent = "⏳ 추천 중...";
    container.style.display = "none";
    keywordsList.innerHTML = "";

    const modelSelect = document.getElementById(this.manager.suggestionModelSelectId);
    const model = modelSelect && modelSelect.value ? modelSelect.value : undefined;

    try {
      const response = await fetch("/api/labels/groups/suggest-keywords", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description: description, model: model }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "키워드 추천 실패");
      }

      const data = await response.json();
      let keywords = data.keywords || [];
      const llmKeywords = data.llm_keywords || [];
      const similarKeywords = data.similar_keywords || [];
      const similarKeywordsWithScore = data.similar_keywords_with_score || [];
      const extractionMethod = data.extraction_method || "regex";  // "ollama" | "regex"

      // 문제 1: 영어 추천시 문장으로 나오는 문제 수정 - 키워드만 추출
      keywords = this.extractKeywordsOnly(keywords);

      if (keywords.length === 0) {
        if (errorDiv) {
          errorDiv.textContent = "추천할 키워드를 찾을 수 없습니다.";
          errorDiv.style.display = "block";
          setTimeout(() => {
            errorDiv.scrollIntoView({ behavior: "smooth", block: "nearest" });
          }, 100);
        } else {
          showError("추천할 키워드를 찾을 수 없습니다.");
        }
        return;
      }

      if (errorDiv) {
        errorDiv.style.display = "none";
      }
      if (successDiv) {
        successDiv.style.display = "none";
      }

      keywordsList.innerHTML = "";
      this.manager.selectedSuggestedKeywords.clear();

      // 문제 3: 기존 키워드 목록에 있는 아이템인 경우 매칭 유사도 % 표기
      keywords.forEach((keyword) => {
        const isSimilar = similarKeywords.includes(keyword);
        const similarityScore = this.getSimilarityScore(keyword, similarKeywordsWithScore);
        const chip = this.createSuggestedKeywordChip(keyword, isSimilar, similarityScore);
        keywordsList.appendChild(chip);
      });

      container.style.display = "block";

      const methodLabel = extractionMethod === "ollama"
        ? "Ollama(로컬 LLM)"
        : "정규식 기반 (Ollama 미실행/미설치)";
      let message = `${keywords.length}개의 키워드가 추천되었습니다. [${methodLabel}]`;
      if (llmKeywords.length > 0 && similarKeywords.length > 0) {
        message += ` — 새 키워드: ${llmKeywords.length}개, 유사 키워드: ${similarKeywords.length}개`;
      } else if (similarKeywords.length > 0) {
        message += ` — 유사 키워드 ${similarKeywords.length}개 포함`;
      } else if (llmKeywords.length > 0) {
        message += ` — 새 키워드 ${llmKeywords.length}개`;
      }

      const successMsgDiv = document.getElementById(this.manager.suggestionSuccessId);
      if (successMsgDiv) {
        successMsgDiv.textContent = message;
        successMsgDiv.style.display = "block";
        setTimeout(() => {
          successMsgDiv.scrollIntoView({ behavior: "smooth", block: "nearest" });
        }, 100);
      } else {
        showSuccess(message);
      }
    } catch (error) {
      console.error("키워드 추천 실패:", error);
      if (errorDiv) {
        errorDiv.textContent = error.message || "키워드 추천 중 오류가 발생했습니다.";
        errorDiv.style.display = "block";
        setTimeout(() => {
          errorDiv.scrollIntoView({ behavior: "smooth", block: "nearest" });
        }, 100);
      } else {
        showError(error.message || "키워드 추천 중 오류가 발생했습니다.");
      }
    } finally {
      btn.disabled = false;
      btn.textContent = "💡 설명 기반 키워드 추천";
    }
  }

  /**
   * 키워드만 추출 (문장에서 키워드 분리)
   */
  extractKeywordsOnly(keywords) {
    const extracted = [];
    
    // 제거할 안내 문구 패턴
    const introPatterns = [
      /^.*?다음과\s*같습니다?[:\s]*/i,
      /^.*?키워드는\s*다음과\s*같습니다?[:\s]*/i,
      /^.*?관련\s*키워드는\s*다음과\s*같습니다?[:\s]*/i,
      /^.*?키워드[는은이]?\s*[:\s]*/i,
      /^.*?추천\s*키워드[는은이]?\s*[:\s]*/i,
      /^.*?다음\s*키워드[는은이]?\s*[:\s]*/i,
      /^.*?예시[는은이]?\s*[:\s]*/i,
      /^.*?예\s*[:\s]*/i,
    ];
    
    keywords.forEach((item) => {
      if (!item) return;
      
      let cleaned = item.trim();
      
      // 안내 문구 제거
      introPatterns.forEach((pattern) => {
        cleaned = cleaned.replace(pattern, '');
      });
      
      // 문장 형태인 경우 쉼표나 줄바꿈으로 분리
      if (cleaned.includes(',') || cleaned.includes('\n')) {
        const parts = cleaned.split(/[,\n]/);
        parts.forEach((part) => {
          const kw = this.cleanKeyword(part.trim());
          if (kw && kw.length >= 2) {
            extracted.push(kw);
          }
        });
      } else {
        // 단일 키워드인 경우
        const kw = this.cleanKeyword(cleaned);
        if (kw && kw.length >= 2) {
          extracted.push(kw);
        }
      }
    });
    
    // 중복 제거
    return [...new Set(extracted)];
  }

  /**
   * 키워드 정리 (블릿, 번호, 마침표 등 제거)
   */
  cleanKeyword(keyword) {
    if (!keyword) return null;
    
    // 앞뒤 공백 제거
    let cleaned = keyword.trim();
    
    // 블릿 및 번호 제거 (예: "1. ", "2. ", "- ", "• ", "○ ", "■ " 등)
    cleaned = cleaned.replace(/^[\d]+[\.\)]\s*/, ''); // "1. ", "2) " 등
    cleaned = cleaned.replace(/^[-•○●■□▲△]\s*/, ''); // "- ", "• " 등
    cleaned = cleaned.replace(/^[a-zA-Z][\.\)]\s*/i, ''); // "a. ", "A) " 등
    
    // 문장 끝의 마침표, 쉼표 제거
    cleaned = cleaned.replace(/[\.。，,]$/, '');
    
    // 앞뒤 공백 다시 제거
    cleaned = cleaned.trim();
    
    // 안내 문구가 포함된 경우 제거
    const introWords = [
      '다음과 같습니다',
      '키워드는',
      '관련 키워드는',
      '추천 키워드는',
      '다음 키워드는',
      '예시',
      '예',
    ];
    
    introWords.forEach((word) => {
      const regex = new RegExp(`^${word}[:\s]*`, 'i');
      cleaned = cleaned.replace(regex, '');
    });
    
    // 특수문자만 있는 경우 제거
    if (cleaned.match(/^[^\w가-힣]+$/)) {
      return null;
    }
    
    return cleaned;
  }

  /**
   * 유사도 점수 가져오기
   */
  getSimilarityScore(keyword, similarKeywordsWithScore) {
    if (!similarKeywordsWithScore || similarKeywordsWithScore.length === 0) {
      return null;
    }
    const found = similarKeywordsWithScore.find((item) => item.keyword === keyword);
    return found ? found.score : null;
  }

  /**
   * 추천 키워드 칩 생성
   */
  createSuggestedKeywordChip(keyword, isSimilar, similarityScore = null) {
    const chip = document.createElement("div");
    chip.className = "keyword-chip";
    chip.dataset.keyword = keyword;
    chip.style.cssText =
      "display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; background: white; border: 2px solid #e5e7eb; border-radius: 16px; cursor: pointer; font-size: 13px; transition: all 0.2s";

    // 문제 3: 기존 키워드 목록에 있는 아이템인 경우 매칭 유사도 % 표기
    let badge = "";
    if (isSimilar) {
      if (similarityScore !== null && similarityScore !== undefined) {
        const scorePercent = Math.round(similarityScore * 100);
        badge = `<span style="font-size: 10px; background: #fef3c7; color: #92400e; padding: 2px 6px; border-radius: 10px; margin-right: 4px">유사 ${scorePercent}%</span>`;
      } else {
        badge = '<span style="font-size: 10px; background: #fef3c7; color: #92400e; padding: 2px 6px; border-radius: 10px; margin-right: 4px">유사</span>';
      }
    }

    const keywordText = document.createElement("span");
    keywordText.innerHTML = badge + escapeHtml(keyword);
    keywordText.style.flex = "1";
    keywordText.onclick = (e) => {
      e.stopPropagation();
      this.toggleSuggestedKeyword(keyword, chip);
    };

    const deleteBtn = document.createElement("button");
    deleteBtn.innerHTML = "×";
    deleteBtn.style.cssText =
      "background: none; border: none; color: #666; cursor: pointer; font-size: 16px; line-height: 1; padding: 0; width: 16px; height: 16px; display: flex; align-items: center; justify-content: center; border-radius: 50%; transition: all 0.2s";
    deleteBtn.onclick = (e) => {
      e.stopPropagation();
      this.removeSuggestedKeyword(keyword, chip);
    };
    deleteBtn.onmouseenter = () => {
      deleteBtn.style.background = "#fee2e2";
      deleteBtn.style.color = "#991b1b";
    };
    deleteBtn.onmouseleave = () => {
      deleteBtn.style.background = "none";
      deleteBtn.style.color = "#666";
    };

    chip.appendChild(keywordText);
    chip.appendChild(deleteBtn);
    return chip;
  }

  /**
   * 추천 키워드 토글
   */
  toggleSuggestedKeyword(keyword, chip) {
    if (this.manager.selectedSuggestedKeywords.has(keyword)) {
      this.manager.selectedSuggestedKeywords.delete(keyword);
      chip.style.background = "white";
      chip.style.borderColor = "#e5e7eb";
    } else {
      this.manager.selectedSuggestedKeywords.add(keyword);
      chip.style.background = "#eff6ff";
      chip.style.borderColor = "#2563eb";
    }
  }

  /**
   * 추천 키워드 제거
   */
  removeSuggestedKeyword(keyword, chip) {
    this.manager.selectedSuggestedKeywords.delete(keyword);
    chip.remove();
    const keywordsList = document.getElementById(this.manager.suggestedKeywordsListId);
    if (keywordsList && keywordsList.children.length === 0) {
      document.getElementById(this.manager.suggestedKeywordsContainerId).style.display = "none";
    }
  }
}
