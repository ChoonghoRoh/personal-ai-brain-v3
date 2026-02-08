# LLM 단독 서버 설계 (하드웨어별 최적화)

**대상 하드웨어**: CPU Intel i5-8400 / RAM 32GB / M.2 256GB / GPU Radeon R7 270X 2GB  
**용도**: LLM 전용 서버 — Backend·n8n 등 다른 호스트에서 `OLLAMA_BASE_URL`로 접속해 추론·키워드 추출에 사용.

---

## 1. 하드웨어 요약 및 제약

| 항목 | 스펙 | LLM 서버 관점 |
|------|------|----------------|
| **CPU** | i5-8400 (6C/6T) | CPU 추론에 적합. 7B~13B Q4 추론 가능. |
| **RAM** | 32GB | 7B~13B Q4 여유 있음. 32B는 부족할 수 있음. |
| **저장** | M.2 256GB | OS + Ollama + 모델 1~2개(Q4) 수용 가능. |
| **GPU** | R7 270X 2GB | VRAM 부족 → **CPU 위주** 설계 권장. |

- **결론**: GPU는 실질적으로 미사용. **CPU + 32GB RAM** 기준으로 OS·서버·모델을 선택.

---

## 2. OS 설계 (최적화)

### 2.1 추천: 경량 Linux 서버

- **데스크톱 미사용** — GUI 없이 서버만 올려 RAM·CPU를 LLM에 집중.
- **장기 지원(LTS)** — 보안·패치 유지가 쉬운 배포판 권장.

| 우선순위 | OS | 비고 |
|----------|-----|------|
| **1** | **Ubuntu Server LTS** (22.04 / 24.04) | 문서·Ollama 안내 많음, 설치 간단. |
| 2 | Debian (Bookworm) — minimal | 더 경량, 설정은 조금 더 직접. |
| 3 | Rocky Linux / AlmaLinux | RHEL 계열 선호 시. |

- **설치 시**: "Minimal" 또는 "Server" 옵션 선택, 데스크톱 패키지 그룹 제외.
- **선택**: SSH 서버만 설치해 원격 관리. 물리 접근이 있으면 GUI 없이 운영.

### 2.2 OS 튜닝 (선택)

- **스왑**: 32GB RAM이면 스왑 4~8GB 정도만 두어 OOM 완화 (M.2이므로 스왑 성능 괜찮음).
- **transparent huge pages**: 기본값으로 두어도 무방. 문제 시 `echo never > /sys/kernel/mm/transparent_hugepage/enabled` 등 검토.
- **서비스 최소화**: 불필요한 서비스 비활성화해 CPU/메모리 절약.

---

## 3. 서버 소프트웨어 (LLM 런타임)

### 3.1 추천: Ollama

- **이유**: Backend가 이미 `OLLAMA_BASE_URL` / `OLLAMA_MODEL`로 연동 중. 추가 개발 없이 단독 서버만 올리면 됨.
- **설치**: 공식 스크립트 권장.

```bash
# Ubuntu/Debian
curl -fsSL https://ollama.com/install.sh | sh
```

- **서비스**: `ollama serve`가 systemd로 등록되어 부팅 시 자동 기동 (기본 포트 11434).
- **방화벽**: 다른 호스트에서 접속할 경우 `11434/tcp` 허용.

```bash
# ufw 예시
sudo ufw allow 11434/tcp
sudo ufw enable
```

### 3.2 모델 저장 경로

- 기본: `~/.ollama` (실행 사용자 홈). M.2 256GB면 OS 파티션에 두면 됨.
- 디스크 여유 확인: `df -h` 로 `/` 또는 해당 경로 여유 확인 (모델당 수 GB~수십 GB).

### 3.3 대안 런타임

- **LocalAI**: OpenAI 호환 API 필요 시 검토. Backend 쪽에서 URL만 바꾸면 됨.
- **llama.cpp (server)**: 직접 빌드·실행 가능. Ollama가 관리·버전 업데이트가 편해 우선 추천.

---

## 4. LLM 모델 설계 (32GB RAM, CPU 위주)

### 4.1 기본 추천 (1개 모델)

| 용도 | 모델 | 크기(대략) | 비고 |
|------|------|------------|------|
| **기본** | **qwen2.5:7b** | ~4.7GB | 다국어(한국어), 추론·키워드에 적합. 32GB에서 여유. |
| **한국어 강화** | **EEVE-Korean 10.8B** | ~11GB | 한국어 품질 우선. 32GB에서 가능, 다른 프로세스 최소화 권장. |
| **경량** | **exaone3.5:2.4b** | ~1.6GB | 가장 가벼움. 응답 속도 우선 시. |

- **단일 모델로 운영 시**: **qwen2.5:7b** 권장. 품질·메모리·속도 균형이 좋음.
- **한국어만 극대화**: **EEVE-Korean 10.8B** (`bnksys/yanolja-eeve-korean-instruct-10.8b`).

### 4.2 모델 2개 동시 보유 (선택)

- 256GB 중 OS + Ollama + **2개 모델** 가능 (예: qwen2.5:7b + exaone3.5:2.4b).
- 동시에 **1개만 로드**해서 사용. 전환은 Backend의 `OLLAMA_MODEL`만 바꾸면 됨.
- 32B급은 32GB RAM에서 추론 시 부족할 수 있어 **비추천**.

### 4.3 설치 예시 (Ollama 서버에서)

```bash
# 기본 추천
ollama pull qwen2.5:7b

# 한국어 품질 우선
ollama pull bnksys/yanolja-eeve-korean-instruct-10.8b
```

---

## 5. 연동 (Backend 쪽 설정)

- **Backend가 있는 호스트** (Docker 또는 로컬)에서:
  - `OLLAMA_BASE_URL=http://LLM서버IP:11434`
  - `OLLAMA_MODEL=qwen2.5:7b` (또는 EEVE 10.8B 등)
- **Docker Compose**: backend 서비스 환경 변수에 위 두 값 설정.
- **동작 확인**: `curl http://LLM서버IP:11434/api/tags` 로 모델 목록 확인.

---

## 6. 요약 체크리스트

| 단계 | 내용 |
|------|------|
| **OS** | Ubuntu Server LTS (또는 Debian minimal) — 데스크톱 미설치 |
| **런타임** | Ollama (`install.sh` → systemd 자동 기동) |
| **방화벽** | 11434/tcp 허용 (다른 호스트 접속 시) |
| **모델** | 1차: **qwen2.5:7b**, 한국어 우선: **EEVE-Korean 10.8B** |
| **연동** | Backend: `OLLAMA_BASE_URL`, `OLLAMA_MODEL` 설정 |

이 설계는 "i5-8400 / 32GB RAM / M.2 256GB / R7 270X 2GB"를 **LLM 단독 서버**로 쓰는 경우에 맞춘 최소·실무용 구성입니다. GPU는 고려하지 않고 CPU+RAM 기준으로 모델을 선택했습니다.
