# 🔐 CPI DLP PII 마스킹 Tool

한국어 텍스트에서 개인식별정보(PII)를 자동 탐지하고 마스킹하는 Streamlit 기반 웹 앱입니다.

---

## 주요 기능

- **2단계 탐지 파이프라인**
  - 1단계: 정규식(Regex) 기반 탐지 — 주민등록번호, 전화번호, 이메일, 계좌번호
  - 2단계: KoNLPy NLP 기반 탐지 — 한국 주소
- **마스킹 토큰 선택** — `[REDACTED]` / `***` / `■■■`
- **탐지 통계 리포트** — 유형별 탐지 수, 위험도 등급(🔴/🟡🟢), 마스킹 비율
- **No-Log 보안 원칙** — 입력 데이터는 브라우저 세션 외부에 저장되지 않음

---

## 탐지 항목

| 유형 | 예시 |
|------|------|
| 주민등록번호 | `900101-1234567` |
| 전화번호 | `010-1234-5678` |
| 이메일 | `user@example.com` |
| 계좌번호 | `110-123-456789` (주요 은행 형식) |
| 주소 | `서울시 강남구 테헤란로 123` |

---

## 실행 방법

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

> KoNLPy 사용을 위해 Java(JDK 8+)가 설치되어 있어야 합니다.

### 2. 앱 실행

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

---

## 프로젝트 구조

```
CPI-DLP-tool/
├── app.py                  # Streamlit 메인 앱
├── requirements.txt
└── detector/
    ├── regex_detector.py   # 정규식 기반 PII 탐지/마스킹
    ├── nlp_detector.py     # KoNLPy 기반 주소 탐지
    ├── address_dict.py     # 한국 행정구역 사전
    ├── report.py           # 위험도 산정 및 리포트 생성
    └── streamlit.py        # UI 컴포넌트
```

---

## 기술 스택

- **Frontend/Backend**: [Streamlit](https://streamlit.io/)
- **NLP**: [KoNLPy](https://konlpy.org/)
- **데이터 처리**: pandas

---

## 라이선스

본 프로젝트는 내부 DLP(Data Loss Prevention) 용도로 제작되었습니다.
