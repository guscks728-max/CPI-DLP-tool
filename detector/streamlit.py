import re
import pandas as pd
import streamlit as st

# ── 1. 페이지 초기 설정 ──────────────────────────────────────────────────
st.set_page_config(
    page_title="PII 마스킹 탐지 Tool",
    page_icon="🔐",
    layout="wide",
)

# ── 2. 레이아웃 강제 교정 및 요소 제거 커스텀 CSS ──────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght=400;500;700&display=swap');

/* 전체 기본 폰트 및 백그라운드 설정 */
html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif !important;
    background-color: #f4f5f7 !important;
}

/* [수정 포인트 1] 최상단 회색 라인의 빈 흰색 박스 및 공백 무조건 삭제 */
[data-testid="stHeader"] {
    display: none !important;
}
div[data-testid="stVerticalBlock"] > div[style*="border"] {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 !important;
}
.stAppViewBlockContainer {
    padding-top: 0rem !important;
}

/* 메인 대시보드 가로 너비 및 외곽 패널 디자인 */
.block-container {
    max-width: 1120px !important;
}
/*.dashboard-wrapper {
    background-color: #ffffff;
    border: 1px solid #e1e4e8;
    border-radius: 12px;
    padding: 2.5rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02);
}
*/

/* 타이틀 및 하단 구분선 (조금 더 진하게 처리) */
.dashboard-main-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #222222;
    margin-bottom: 1.8rem;
    padding-bottom: 0.8rem;
    border-bottom: 2px solid #b1b5c0 !important;
}

/* 섹션 타이틀 라벨 */
.panel-section-label {
    font-size: 0.95rem;
    font-weight: 700;
    color: #333333;
    margin-bottom: 0.6rem;
}

/* 입력창 및 결과창 스타일 고정 */
div[data-testid="stHorizontalBlock"] > div:nth-child(1) div[data-testid="stTextArea"] textarea {
    border: 1px solid #a7c7ff !important;
    background-color: #f0f6ff !important;
    font-size: 0.82rem !important;
    color: #333333 !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(2) div[data-testid="stTextArea"] textarea {
    font-size: 0.82rem !important;
    color: #333333 !important;
}

/* 마스킹 옵션 컨테이너 */
.custom-option-panel {
    background-color: #f8f9fa;
    border: 1px solid #dcdcdc;
    border-radius: 6px;
    padding: 10px 14px;
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
}
.custom-option-title {
    font-size: 0.82rem;
    font-weight: 600;
    color: #555555;
}

/* 처리 파이프라인 컴포넌트 */
.pipeline-flex-line {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: 8px;
    font-size: 0.8rem;
    color: #888888;
    background-color: #f8f9fa;
    padding: 12px 16px;
    border-radius: 8px;
    margin: 2rem 0;
    border: 1px solid #eaeaea;
}
.pipeline-main-tag { font-weight: 700; color: #444444; margin-right: 4px; white-space: nowrap; }
.pipeline-arrow { white-space: nowrap; }
.pipeline-step-badge {
    padding: 5px 12px;
    border-radius: 6px;
    border: 1px solid #e1e4e8;
    background-color: #ffffff;
    white-space: nowrap;
}
.pipeline-step-badge.blue   { border-color: #a7c7ff; background-color: #f0f6ff; color: #2563eb; font-weight: 500; }
.pipeline-step-badge.yellow { border-color: #fef08a; background-color: #fefcbf; color: #b45309; font-weight: 500; }
.pipeline-step-badge.pink   { border-color: #fbcfe8; background-color: #fdf2f8; color: #db2777; font-weight: 500; }

/* 탐지 통계 리포트 5열 배열 그리드 */
.statistics-grid-layout {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin-top: 0.8rem;
    margin-bottom: 2rem;
}
.stat-item-card {
    border: 1px solid #e1e4e8;
    border-radius: 8px;
    padding: 1.2rem 0.2rem;
    text-align: center;
    background-color: #ffffff;
}
.stat-item-label {
    font-size: 0.82rem;
    font-weight: 500;
    color: #666666;
    margin-bottom: 6px;
}
.stat-item-counter {
    font-size: 1.6rem;
    font-weight: 700;
}
.text-danger-red { color: #eb4d4b; }
.text-warning-orange { color: #f0932b; }
.danger-status-banner { font-size: 0.95rem; font-weight: 700; margin-bottom: 0.8rem; }

/* ── 위젯 기본 버튼 마진 및 줄바꿈 강제 방지 설정 ── */
div.stButton > button {
    border-radius: 6px !important;
    font-size: 0.85rem !important;
    padding: 6px 14px !important;
    white-space: nowrap !important; /* 확대해도 글자가 아래로 안 떨어지게 방지 */
    word-break: keep-all !important;
}

/* [수정 포인트 2] 마스킹하기 버튼 - 완벽한 파란색(Blue) 강제 매칭 및 고정 */
div.stButton > button[data-testid="baseButton-primary"],
div.stButton > button:has(div[data-testid="stMarkdownContainer"] p:contains("마스킹하기")) {
    background-color: #2563eb !important;
    border-color: #2563eb !important;
    color: #ffffff !important;
    font-weight: 500 !important;
    width: 100% !important;
    box-shadow: 0 2px 4px rgba(37, 99, 235, 0.15) !important;
}
div.stButton > button[data-testid="baseButton-primary"]:hover {
    background-color: #1d4ed8 !important;
    border-color: #1d4ed8 !important;
}
</style>
""", unsafe_allow_html=True)

# ── 3. 백엔드 알고리즘 작동부 ───────────────────────────────────────────────
PII_RULES = {
    "주민등록번호": re.compile(r"\d{6}[-–]\d{7}"),
    "전화번호": re.compile(r"0\d{1,2}[-.\s]?\d{3,4}[-.\s]?\d{4}"),
    "이메일": re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"),
    "계좌번호": re.compile(r"\d{3,6}[-–]\d{2,6}[-–]\d{3,6}"),
    "주소": re.compile(
        r"(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)"
        r"(?:특별시|광역시|특별자치시|도)?[\s]+"
        r"(?:[가-힣]+[시|군|구])?[\s]*"
        r"(?:[가-힣A-Za-z0-9]+[로|길|읍|면|동|리])?[\s]*"
        r"(?:\d+[-–]?\d*번지|\d+)?"
    ),
}

SURNAMES = ["김", "이", "박", "최", "정", "강", "조", "윤", "장", "임", "한", "오", "서", "신", "홍"]
NAME_REG = re.compile(rf"(?<![가-힣])(?:{'|'.join(SURNAMES)})[가-힣]{{1,2}}(?=[은|는|이|가|을|를|과|와|에|,\s]|$)")

def run_pii_engine(text: str, token: str) -> tuple[str, dict[str, int]]:
    stats = {k: 0 for k in PII_RULES}
    stats["이름"] = 0
    result = text

    for pii_type, regex in PII_RULES.items():
        matches = regex.findall(result)
        if matches:
            stats[pii_type] += len(matches)
            result = regex.sub(token, result)

    names = set(NAME_REG.findall(text))
    if names:
        stats["이름"] += len(names)
        for name in names:
            result = re.sub(rf"(?<![가-힣]){name}(?![가-힣])", token, result)

    return result, stats

# ── 4. 세션 데이터 보존 ──────────────────────────────────────────────────────
if "masked_txt" not in st.session_state:
    st.session_state.masked_txt = ""
if "stats_map" not in st.session_state:
    st.session_state.stats_map = {}

# ── 5. 메인 UI 본문 렌더링 ───────────────────────────────────────────────────
st.markdown('<div class="dashboard-wrapper">', unsafe_allow_html=True)
st.markdown('<div class="dashboard-main-title">🔐 PII 마스킹 탐지 Tool</div>', unsafe_allow_html=True)

col_left, col_right = st.columns(2, gap="large")

with col_left:
    st.markdown('<div class="panel-section-label">① 원문 입력</div>', unsafe_allow_html=True)
    user_input = st.text_area(
        label="Input",
        placeholder="텍스트를 넣어주거나 직접 입력하세요.",
        height=180,
        label_visibility="collapsed"
    )

    # 두 버튼의 너비를 넉넉히 확보하여 글자가 잘리는 현상 차단
    ctrl_col1, ctrl_col2 = st.columns([4, 6])
    with ctrl_col1:
        st.caption(f"{len(user_input)} / 3,000자")
    with ctrl_col2:
        btn_space1, btn_space2 = st.columns(2)
        with btn_space1:
            if st.button("🔄 초기화", use_container_width=True):
                st.session_state.masked_txt = ""
                st.session_state.stats_map = {}
                st.rerun()
        with btn_space2:
            # 피그마에 매칭되는 진짜 파란색 버튼 구성
            btn_trigger = st.button("🚀 마스킹하기", type="primary", use_container_width=True)

    # 마스킹 옵션 박스
    st.markdown("""
    <div class="custom-option-panel">
        <div class="custom-option-title">⚙️ 마스킹 옵션</div>
    </div>
    """, unsafe_allow_html=True)

    token_choice = st.radio(
        label="Token",
        options=["[REDACTED]", "***", "■■■"],
        horizontal=True,
        label_visibility="collapsed"
    )

with col_right:
    st.markdown('<div class="panel-section-label">④ 마스킹 결과</div>', unsafe_allow_html=True)
    if st.session_state.masked_txt:
        st.text_area(
            label="Output",
            value=st.session_state.masked_txt,
            height=180,
            label_visibility="collapsed"
        )
        st.write("")
        st.download_button(
            label="📋 결과 복사하기",
            data=st.session_state.masked_txt,
            file_name="masked_output.txt",
            use_container_width=True
        )
    else:
        st.text_area(
            label="Output Empty",
            placeholder="원문을 입력하고 [마스킹하기] 버튼을 누르면 정제된 결과가 여기에 출력됩니다.",
            height=180,
            label_visibility="collapsed",
            disabled=True
        )
        st.write("")
        st.button("📋 결과 복사하기", disabled=True, use_container_width=True)

# ── 6. 이벤트 컨트롤 처리 ────────────────────────────────────────────────────
if btn_trigger:
    if user_input.strip():
        m_txt, m_stat = run_pii_engine(user_input, token_choice)
        st.session_state.masked_txt = m_txt
        st.session_state.stats_map = m_stat
        st.rerun()
    else:
        st.warning("분석할 원문 텍스트를 입력해 주세요.")

# ── 7. 파이프라인 명세 선형 배치 ───────────────────────────────────────────────
st.markdown("""
<div class="pipeline-flex-line">
    <span class="pipeline-main-tag">🔧 처리 파이프라인</span>
    <span class="pipeline-step-badge">① 원문 입력 및 붙여넣기</span>
    <span class="pipeline-arrow">→</span>
    <span class="pipeline-step-badge blue">② regex 1차 탐지</span>
    <span class="pipeline-arrow">→</span>
    <span class="pipeline-step-badge yellow">③ KoNLPy 2차 탐지</span>
    <span class="pipeline-arrow">→</span>
    <span class="pipeline-step-badge pink">④ 마스킹 출력</span>
</div>
""", unsafe_allow_html=True)

# ── 8. 탐지 통계 리포트 ──────────────────────────────────────────────────────
st.markdown('<div class="panel-section-label">📊 탐지 통계 리포트</div>', unsafe_allow_html=True)

current_stats = st.session_state.stats_map if st.session_state.stats_map else {k: 0 for k in PII_RULES}
if "이름" not in current_stats: current_stats["이름"] = 0

merged_addr_name = current_stats.get("주소", 0) + current_stats.get("이름", 0)
total_count = sum(current_stats.values())

st.markdown(f"""
<div class="statistics-grid-layout">
    <div class="stat-item-card">
        <div class="stat-item-label">주민등록번호</div>
        <div class="stat-item-counter text-danger-red">{current_stats.get("주민등록번호", 0)}</div>
    </div>
    <div class="stat-item-card">
        <div class="stat-item-label">전화번호</div>
        <div class="stat-item-counter text-danger-red">{current_stats.get("전화번호", 0)}</div>
    </div>
    <div class="stat-item-card">
        <div class="stat-item-label">이메일</div>
        <div class="stat-item-counter text-danger-red">{current_stats.get("이메일", 0)}</div>
    </div>
    <div class="stat-item-card">
        <div class="stat-item-label">계좌번호</div>
        <div class="stat-item-counter text-warning-orange">{current_stats.get("계좌번호", 0)}</div>
    </div>
    <div class="stat-item-card">
        <div class="stat-item-label">주소 및 이름</div>
        <div class="stat-item-counter text-warning-orange">{merged_addr_name}</div>
    </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.stats_map:
    if total_count == 0:
        banner_text, banner_color = "🟢 안전 | 탐지된 위험 요소가 없습니다.", "#16a34a"
    elif total_count <= 2:
        banner_text, banner_color = f"🟡 보통 | 총 {total_count}건의 개인정보 위험 요소가 탐지되었습니다.", "#f0932b"
    else:
        banner_text, banner_color = f"🔴 위험 | 총 {total_count}건의 개인정보가 탐지되었습니다!", "#eb4d4b"

    st.markdown(f'<div class="danger-status-banner" style="color: {banner_color};">{banner_text}</div>', unsafe_allow_html=True)

    rows = []
    for k, v in st.session_state.stats_map.items():
        if v > 0:
            rows.append({"PII 유형": k, "탐지 건수": f"{v}건"})
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
else:
    st.markdown('<div class="danger-status-banner" style="color: #888888; font-weight: 500;">🔍 원문을 검사하면 상세 탐지 리포트가 여기에 생성됩니다.</div>', unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; font-size: 0.75rem; color: #a0aec0; margin-top: 2.5rem; border-top: 1px solid #f0f2f5; padding-top: 1rem;">
    ⓘ 본 서비스는 No-Log 보안 원칙에 따라 작동하며, 입력하신 기밀 정보는 브라우저 세션 외부에 절대 저장되지 않습니다.
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)