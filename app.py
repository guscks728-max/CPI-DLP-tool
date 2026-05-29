import sys
import os
import streamlit as st

# ── 0. 모듈 경로 설정 ─────────────────────────────────────────────────────────
_base         = os.path.dirname(os.path.abspath(__file__))
_detector_dir = os.path.join(_base, "detector")
for _p in [_base, _detector_dir]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from regex_detector import mask_pii
from report import make_report, calc_risk

try:
    from detector.nlp_detector import detect_address
    _NLP_AVAILABLE = True
except Exception:
    _NLP_AVAILABLE = False

# ── 1. 페이지 초기 설정 ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="PII 마스킹 탐지 Tool",
    page_icon="🔐",
    layout="wide",
)

# ── 2. 커스텀 CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght=400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif !important;
    background-color: #f4f5f7 !important;
}
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
.block-container {
    max-width: 1120px !important;
}
.dashboard-wrapper {
    background-color: #ffffff;
    border: 1px solid #e1e4e8;
    border-radius: 12px;
    padding: 2.5rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02);
}
.dashboard-main-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #222222;
    margin-bottom: 1.8rem;
    padding-bottom: 0.8rem;
    border-bottom: 2px solid #b1b5c0 !important;
}
.panel-section-label {
    font-size: 0.95rem;
    font-weight: 700;
    color: #333333;
    margin-bottom: 0.6rem;
}
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
.stat-item-label { font-size: 0.82rem; font-weight: 500; color: #666666; margin-bottom: 6px; }
.stat-item-counter { font-size: 1.6rem; font-weight: 700; }
.text-danger-red { color: #eb4d4b; }
.text-warning-orange { color: #f0932b; }
.danger-status-banner { font-size: 0.95rem; font-weight: 700; margin-bottom: 0.8rem; }
div.stButton > button {
    border-radius: 6px !important;
    font-size: 0.85rem !important;
    padding: 6px 14px !important;
    white-space: nowrap !important;
    word-break: keep-all !important;
}
div.stButton > button[data-testid="baseButton-primary"] {
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
#MainMenu {visibility: hidden !important;}
header {visibility: hidden !important;}
footer {visibility: hidden !important;}
[data-testid="stToolbar"] {display: none !important;}
[data-testid="stDecoration"] {display: none !important;}
.stDeployButton {display: none !important;}
section[data-testid="stSidebar"] {display: none !important;}
[data-testid="stAppViewContainer"] > .main > div:first-child {padding-top: 0 !important;}
div[data-testid="stVerticalBlock"] > div:first-child > div[style] {display: none !important;}
.stApp header {display: none !important;}
.stApp > header {display: none !important;}
</style>
""", unsafe_allow_html=True)

# ── 3. 세션 상태 초기화 ───────────────────────────────────────────────────────
for _key, _default in [
    ("masked_txt",    ""),
    ("detected_list", []),
    ("original_txt",  ""),
]:
    if _key not in st.session_state:
        st.session_state[_key] = _default

# ── 4. 메인 UI ────────────────────────────────────────────────────────────────
st.markdown('<div class="dashboard-main-title">🔐 PII 마스킹 탐지 Tool</div>', unsafe_allow_html=True)

col_left, col_right = st.columns(2, gap="large")

with col_left:
    st.markdown('<div class="panel-section-label">① 원문 입력</div>', unsafe_allow_html=True)
    user_input = st.text_area(
        label="Input",
        placeholder="텍스트를 넣어주거나 직접 입력하세요.",
        height=180,
        label_visibility="collapsed",
    )

    ctrl_col1, ctrl_col2 = st.columns([4, 6])
    with ctrl_col1:
        st.caption(f"{len(user_input)} / 3,000자")
    with ctrl_col2:
        btn_space1, btn_space2 = st.columns(2)
        with btn_space1:
            if st.button("🔄 초기화", use_container_width=True):
                st.session_state.masked_txt    = ""
                st.session_state.detected_list = []
                st.session_state.original_txt  = ""
                st.rerun()
        with btn_space2:
            btn_trigger = st.button("🚀 마스킹하기", type="primary", use_container_width=True)

    st.markdown("""
    <div class="custom-option-panel">
        <div class="custom-option-title">⚙️ 마스킹 옵션</div>
    </div>
    """, unsafe_allow_html=True)

    token_choice = st.radio(
        label="Token",
        options=["[REDACTED]", r"\*\*\*", "■■■"],
        horizontal=True,
        label_visibility="collapsed",
    )

with col_right:
    st.markdown('<div class="panel-section-label">④ 마스킹 결과</div>', unsafe_allow_html=True)
    if st.session_state.masked_txt:
        st.text_area(
            label="Output",
            value=st.session_state.masked_txt,
            height=180,
            label_visibility="collapsed",
        )
        st.write("")
        st.download_button(
            label="📋 결과 복사하기",
            data=st.session_state.masked_txt,
            file_name="masked_output.txt",
            use_container_width=True,
        )
    else:
        st.text_area(
            label="Output Empty",
            placeholder="원문을 입력하고 [마스킹하기] 버튼을 누르면 정제된 결과가 여기에 출력됩니다.",
            height=180,
            label_visibility="collapsed",
            disabled=True,
        )
        st.write("")
        st.button("📋 결과 복사하기", disabled=True, use_container_width=True)

# ── 5. 이벤트 처리 ────────────────────────────────────────────────────────────
if btn_trigger:
    if user_input.strip():
        actual_token = "***" if token_choice == r"\*\*\*" else token_choice

        # ① regex_detector: 정규식 1차 탐지
        masked_text, detected_list = mask_pii(user_input, actual_token)

        # ② nlp_detector: KoNLPy 2차 탐지 (주소)
        if _NLP_AVAILABLE:
            try:
                already_found = {d["원문"] for d in detected_list}
                for r in detect_address(user_input):
                    if r["value"] not in already_found:
                        detected_list.append({"유형": r["type"], "원문": r["value"]})
                        masked_text = masked_text.replace(r["value"], actual_token)
                        already_found.add(r["value"])
            except Exception:
                pass

        st.session_state.masked_txt    = masked_text
        st.session_state.detected_list = detected_list
        st.session_state.original_txt  = user_input
        st.rerun()
    else:
        st.warning("분석할 원문 텍스트를 입력해 주세요.")


# # ── 6. 파이프라인 명세 ────────────────────────────────────────────────────────
# st.markdown("""
# <div class="pipeline-flex-line">
#     <span class="pipeline-main-tag">🔧 처리 파이프라인</span>
#     <span class="pipeline-step-badge">① 원문 입력 및 붙여넣기</span>
#     <span class="pipeline-arrow">→</span>
#     <span class="pipeline-step-badge blue">② regex 1차 탐지</span>
#     <span class="pipeline-arrow">→</span>
#     <span class="pipeline-step-badge yellow">③ KoNLPy 2차 탐지</span>
#     <span class="pipeline-arrow">→</span>
#     <span class="pipeline-step-badge pink">④ 마스킹 출력</span>
# </div>
# """, unsafe_allow_html=True)


# ── 7. 탐지 통계 리포트 ───────────────────────────────────────────────────────
st.markdown('<div class="panel-section-label">📊 탐지 통계 리포트</div>', unsafe_allow_html=True)

has_run       = bool(st.session_state.original_txt)
detected_list = st.session_state.detected_list

# detected_list → 유형별 카운트
current_stats: dict[str, int] = {}
for d in detected_list:
    current_stats[d["유형"]] = current_stats.get(d["유형"], 0) + 1
merged_addr_name = current_stats.get("주소", 0)

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
        <div class="stat-item-label">주소</div>
        <div class="stat-item-counter text-warning-orange">{merged_addr_name}</div>
    </div>
</div>
""", unsafe_allow_html=True)

if has_run:
    if detected_list:
        # ③ report: calc_risk() — 위험도 배너
        risk = calc_risk(st.session_state.original_txt, detected_list)
        if "🔴" in risk["위험도_등급"]:
            banner_color = "#eb4d4b"
        elif "🟡" in risk["위험도_등급"]:
            banner_color = "#f0932b"
        else:
            banner_color = "#16a34a"

        st.markdown(
            f'<div class="danger-status-banner" style="color: {banner_color};">'
            f'{risk["위험도_등급"]} | 마스킹 비율 {risk["마스킹_비율"]}% — {risk["위험도_설명"]}'
            f'</div>',
            unsafe_allow_html=True,
        )

        # ③ report: make_report() — 상세 테이블
        report_df = make_report(detected_list)
        if not report_df.empty:
            st.dataframe(report_df, use_container_width=True, hide_index=True)
    else:
        st.markdown(
            '<div class="danger-status-banner" style="color: #16a34a;">'
            '🟢 안전 | 탐지된 위험 요소가 없습니다.'
            '</div>',
            unsafe_allow_html=True,
        )
else:
    st.markdown(
        '<div class="danger-status-banner" style="color: #888888; font-weight: 500;">'
        '🔍 원문을 검사하면 상세 탐지 리포트가 여기에 생성됩니다.'
        '</div>',
        unsafe_allow_html=True,
    )

# ── 8. 푸터 ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align: center; font-size: 0.75rem; color: #a0aec0; margin-top: 2.5rem;
            border-top: 1px solid #f0f2f5; padding-top: 1rem;">
    ⓘ 본 서비스는 No-Log 보안 원칙에 따라 작동하며,
    입력하신 기밀 정보는 브라우저 세션 외부에 절대 저장되지 않습니다.
</div>
""", unsafe_allow_html=True)
