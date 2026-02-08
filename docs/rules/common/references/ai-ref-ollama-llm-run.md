# Ollama(LLM) 실행

이 프로젝트는 Ollama를 **호스트의 localhost**에서 실행하고, Backend(Docker)는 `host.docker.internal:11434`로 접속합니다.

## 1. Ollama 설치 (호스트)

- **macOS**: [ollama.com](https://ollama.com) 에서 앱 다운로드 후 설치  
  또는 터미널: `brew install ollama`
- **Linux**: `curl -fsSL https://ollama.com/install.sh | sh`
- **Windows**: [ollama.com](https://ollama.com) 에서 설치 프로그램 다운로드

설치 후 터미널에서 `ollama` 명령이 동작하는지 확인:

```bash
ollama --version
```

## 2. LLM 서버 실행

### 방법 A: Ollama 앱 (macOS/Windows)

- Ollama 앱을 실행하면 자동으로 `ollama serve`가 떠서 `localhost:11434`에서 대기합니다.

### 방법 B: 터미널에서 서버만 실행

```bash
ollama serve
```

- 포트: **11434** (기본값)
- 종료: `Ctrl+C`

## 3. 모델 내려받기 및 사용

```bash
# 기본 모델 (qwen2.5:7b — 추론·키워드 추천에 적합)
ollama pull qwen2.5:7b

# 한국어 instruct 모델 (12GB+ RAM 권장)
ollama pull bnksys/yanolja-eeve-korean-instruct-10.8b
```

- `.env` / `.env.example` 의 `OLLAMA_MODEL` 과 맞추면 Backend가 해당 모델을 사용합니다.
- **참고**: `exaone3.5:2.4b` 는 일부 환경에서 "model runner has unexpectedly stopped" 오류로 동작하지 않을 수 있어, 기본값은 `qwen2.5:7b` 로 지정되어 있습니다.

## 4. 동작 확인

- **대시보드**: http://localhost:8000/dashboard → 로컬 LLM(Ollama) 상태에서 “사용 가능” 및 “🧪 테스트” 확인
- **스크립트** (호스트에서, Ollama 미실행 시 자동 기동 + 모델 검증):

```bash
# 프로젝트 루트에서
python3 scripts/llm_server_check.py --url http://localhost:11434 --start-if-missing --check-model
```

- `ollama` 가 PATH에 없으면 “No such file or directory: 'ollama'” 가 나옵니다. 위 1번처럼 Ollama를 먼저 설치하세요.

## 5. Backend와의 연결

- **Backend(Docker)** 는 `.env` 의 `OLLAMA_BASE_URL=http://host.docker.internal:11434` 로 호스트의 Ollama에 접속합니다.
- Backend를 **호스트에서 직접** 실행할 때는 `OLLAMA_BASE_URL=http://localhost:11434` 로 두면 됩니다.

요약: **호스트에서 Ollama 설치 → `ollama serve` 또는 Ollama 앱 실행 → 필요 시 `ollama pull <모델>` → 대시보드 또는 `llm_server_check.py` 로 확인.**
