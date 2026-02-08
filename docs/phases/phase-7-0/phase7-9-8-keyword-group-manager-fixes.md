# Phase 7.9.8: keyword-group-manager.js 테스트 결과 수정 사항

**수정일**: 2026-01-10  
**상태**: ✅ 완료

---

## 📋 수정된 문제점

### 1. 영어 추천시 문장으로 나오는 문제 ✅

**문제**: 설명 기반 키워드 추천 실행시 영어 추천시 문장으로 나오는 문제

**원인**: LLM이 문장 형태로 키워드를 반환하는 경우, 프론트엔드에서 키워드만 추출하지 않음

**수정 내용**:
- `keyword-group-suggestion.js`에 `extractKeywordsOnly()` 메서드 추가
- 쉼표나 줄바꿈으로 구분된 키워드 추출
- 문장 끝의 마침표, 설명 제거
- 2글자 이상의 키워드만 추출

**수정 파일**:
- `web/public/js/keyword-group-suggestion.js`

**코드 변경**:
```javascript
extractKeywordsOnly(keywords) {
  const extracted = [];
  keywords.forEach((item) => {
    if (!item) return;
    
    // 문장 형태인 경우 쉼표나 줄바꿈으로 분리
    const cleaned = item.trim();
    if (cleaned.includes(',') || cleaned.includes('\n')) {
      const parts = cleaned.split(/[,\n]/);
      parts.forEach((part) => {
        const kw = part.trim();
        if (kw.length >= 2 && !kw.match(/^[^\w가-힣]+$/)) {
          const cleanKw = kw.replace(/[\.。]$/, '').trim();
          if (cleanKw.length >= 2) {
            extracted.push(cleanKw);
          }
        }
      });
    } else {
      const cleanKw = cleaned.replace(/[\.。]$/, '').trim();
      if (cleanKw.length >= 2) {
        extracted.push(cleanKw);
      }
    }
  });
  
  return [...new Set(extracted)];
}
```

---

### 2. 저장 클릭시 선택된 키워드가 등록되지 않는 문제 ✅

**문제**: 저장 클릭시 선택된 키워드가 등록되지 않는 문제

**원인**: 그룹 수정 시 선택된 키워드를 추가하지 않음

**수정 내용**:
- `keyword-group-crud.js`의 `handleCreateGroup()` 메서드 수정
- 그룹 수정 시에도 선택된 키워드를 추가하도록 처리
- 그룹 생성 시에는 기존 로직 유지

**수정 파일**:
- `web/public/js/keyword-group-crud.js`

**코드 변경**:
```javascript
if (this.manager.editingGroupId) {
  await this.updateGroup(this.manager.editingGroupId, name, description || null, validColor);
  // 문제 2: 수정 시에도 선택된 키워드 추가
  const suggestedKeywords = Array.from(this.manager.selectedSuggestedKeywords);
  if (suggestedKeywords.length > 0) {
    try {
      await this.manager.matching.addKeywordsToGroup(this.manager.editingGroupId, suggestedKeywords);
      showSuccess(`그룹이 수정되었고 ${suggestedKeywords.length}개의 키워드가 추가되었습니다.`);
    } catch (keywordError) {
      console.error("키워드 추가 실패:", keywordError);
      showSuccess("그룹이 수정되었습니다. (키워드 추가 실패)");
    }
  }
} else {
  await this.createGroup(name, description || null, validColor);
}
```

---

### 3. 키워드 추천시 기존 키워드 목록에 있는 아이템인 경우 매칭 유사도 % 표기 ✅

**문제**: 키워드 추천시 기존 키워드 목록에 있는 아이템인 경우 매칭 유사도 % 표기

**원인**: 백엔드 API에서 유사도 점수를 반환하지 않음

**수정 내용**:
1. **백엔드 API 수정** (`backend/routers/labels.py`):
   - `calculate_similarity()` 함수 추가
   - 유사도 점수 계산 (0.0 ~ 1.0)
   - `similar_keywords_with_score` 필드 추가

2. **프론트엔드 수정** (`web/public/js/keyword-group-suggestion.js`):
   - `getSimilarityScore()` 메서드 추가
   - `createSuggestedKeywordChip()` 메서드에 유사도 점수 표시 추가
   - 유사도가 있는 경우 "유사 XX%" 형태로 표시

**수정 파일**:
- `backend/routers/labels.py`
- `web/public/js/keyword-group-suggestion.js`

**백엔드 코드 변경**:
```python
def calculate_similarity(keyword_name: str, description: str) -> float:
    """간단한 유사도 계산 (0.0 ~ 1.0)"""
    keyword_lower = keyword_name.lower()
    desc_lower = description.lower()
    
    # 완전 일치
    if keyword_lower == desc_lower:
        return 1.0
    
    # 설명에 키워드가 완전히 포함
    if keyword_lower in desc_lower:
        return 0.9
    
    # 키워드가 설명에 완전히 포함
    if desc_lower in keyword_lower:
        return 0.8
    
    # 단어 단위 일치
    keyword_words = set(word for word in keyword_lower.split() if len(word) >= 2)
    desc_words = set(word for word in desc_lower.split() if len(word) >= 2)
    if keyword_words and desc_words:
        common_words = keyword_words.intersection(desc_words)
        if common_words:
            return min(0.7, len(common_words) / max(len(keyword_words), len(desc_words)))
    
    # 부분 일치 (2글자 이상)
    if len(keyword_lower) >= 2 and keyword_lower in desc_lower:
        return 0.6
    
    # 문자 단위 유사도 (간단한 Jaccard 유사도)
    keyword_chars = set(keyword_lower)
    desc_chars = set(desc_lower)
    if keyword_chars and desc_chars:
        intersection = keyword_chars.intersection(desc_chars)
        union = keyword_chars.union(desc_chars)
        if union:
            jaccard = len(intersection) / len(union)
            if jaccard > 0.3:  # 최소 임계값
                return jaccard * 0.5
    
    return 0.0
```

**프론트엔드 코드 변경**:
```javascript
getSimilarityScore(keyword, similarKeywordsWithScore) {
  if (!similarKeywordsWithScore || similarKeywordsWithScore.length === 0) {
    return null;
  }
  const found = similarKeywordsWithScore.find((item) => item.keyword === keyword);
  return found ? found.score : null;
}

createSuggestedKeywordChip(keyword, isSimilar, similarityScore = null) {
  // ...
  let badge = "";
  if (isSimilar) {
    if (similarityScore !== null && similarityScore !== undefined) {
      const scorePercent = Math.round(similarityScore * 100);
      badge = `<span style="font-size: 10px; background: #fef3c7; color: #92400e; padding: 2px 6px; border-radius: 10px; margin-right: 4px">유사 ${scorePercent}%</span>`;
    } else {
      badge = '<span style="font-size: 10px; background: #fef3c7; color: #92400e; padding: 2px 6px; border-radius: 10px; margin-right: 4px">유사</span>';
    }
  }
  // ...
}
```

---

## ✅ 테스트 결과

### 수정 전 문제점
1. ❌ 영어 추천시 문장으로 나옴
2. ❌ 저장 클릭시 선택된 키워드가 등록되지 않음
3. ❌ 유사도 표시 없음

### 수정 후 결과
1. ✅ 키워드만 추출되어 표시됨
2. ✅ 저장 클릭시 선택된 키워드가 정상적으로 등록됨
3. ✅ 기존 키워드 목록에 있는 아이템인 경우 유사도 % 표시됨

---

## 📊 변경 통계

- **수정 파일 수**: 3개
  - `web/public/js/keyword-group-suggestion.js`
  - `web/public/js/keyword-group-crud.js`
  - `backend/routers/labels.py`
- **추가 메서드**: 3개
  - `extractKeywordsOnly()` - 키워드 추출
  - `getSimilarityScore()` - 유사도 점수 가져오기
  - `calculate_similarity()` - 유사도 계산 (백엔드)
- **수정된 기능**: 3개
  - 키워드 추출 로직
  - 그룹 수정 시 키워드 추가
  - 유사도 표시

---

## 🎯 향후 개선 사항

1. **유사도 계산 정확도 향상**: 더 정교한 유사도 알고리즘 적용 (예: Levenshtein 거리, TF-IDF 등)
2. **키워드 추출 정확도 향상**: NLP 라이브러리 활용 (예: spaCy, NLTK)
3. **성능 최적화**: 대량의 키워드 처리 시 성능 개선
