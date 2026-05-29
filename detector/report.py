import pandas as pd


# ──────────────────────────────────────────────
# 1. PII 종류별 탐지 통계 리포트
# ──────────────────────────────────────────────

def make_report(detected_list: list[dict]) -> pd.DataFrame:
    """
    탐지된 PII 목록을 받아 종류별 건수 통계 DataFrame을 반환한다.

    Parameters
    ----------
    detected_list : list[dict]
        다른 모듈(re, KoNLPy)에서 탐지한 결과 리스트.
        각 원소는 {"유형": str, "원문": str} 형태여야 한다.

        예)
        [
            {"유형": "전화번호",    "원문": "010-1234-5678"},
            {"유형": "이메일",      "원문": "hong@gmail.com"},
            {"유형": "주민등록번호","원문": "[RRN Omitted]"},
        ]

    Returns
    -------
    pd.DataFrame
        columns: ["PII 유형", "탐지 건수"]
        마지막 행은 합계 행.
    """
    if not detected_list:
        empty = pd.DataFrame(columns=["PII 유형", "탐지 건수"])
        return empty

    df = pd.DataFrame(detected_list)

    # 유형별 집계 → 내림차순 정렬
    report = (
        df.groupby("유형")
          .size()
          .reset_index(name="탐지 건수")
          .rename(columns={"유형": "PII 유형"})
          .sort_values("탐지 건수", ascending=False)
          .reset_index(drop=True)
    )

    # 합계 행 추가
    total_row = pd.DataFrame([{
        "PII 유형": "합계",
        "탐지 건수": report["탐지 건수"].sum()
    }])
    report = pd.concat([report, total_row], ignore_index=True)

    return report


# ──────────────────────────────────────────────
# 2. 본문 대비 마스킹 비율 기반 위험도 산출
# ──────────────────────────────────────────────

def calc_risk(original_text: str, detected_list: list[dict]) -> dict:
    """
    원문과 탐지 결과를 받아 마스킹 비율을 계산하고,
    비율에 따라 위험도 등급(색상)을 나눈다.

    Parameters
    ----------
    original_text : str
        사용자가 붙여넣은 원본 텍스트 전체.
    detected_list : list[dict]
        make_report()와 동일한 형식의 탐지 결과 리스트.

    Returns
    -------
    dict
        {
            "마스킹_비율":  float,   # 0.0 ~ 100.0 (%)
            "위험도_등급":  str,     # "🔴 높음" / "🟡 보통" / "🟢 낮음"
            "위험도_설명":  str,     # 사용자에게 보여줄 한 줄 메시지
        }
    """
    total_chars  = len(original_text)
    masked_chars = sum(len(d["원문"]) for d in detected_list)

    # 마스킹 비율 계산 (소수점 1자리)
    mask_ratio = (
        round(masked_chars / total_chars * 100, 1)
        if total_chars > 0 else 0.0
    )

    # 마스킹 비율에 따른 위험도 산정 (기준 수치는 필요에 따라 조정 가능)
    if mask_ratio >= 15.0:
        risk_level = "🔴 높음"
        risk_desc  = "본문 대비 마스킹 비율이 매우 높습니다. 다수의 개인정보가 포함되어 주의가 필요합니다."
    elif mask_ratio >= 5.0:
        risk_level = "🟡 보통"
        risk_desc  = "일부 개인정보가 감지되었습니다. 마스킹 결과를 확인 후 사용하세요."
    else:
        risk_level = "🟢 낮음"
        risk_desc  = "개인정보 위험이 낮습니다. 마스킹 결과를 한 번 더 확인해 주세요."

    return {
        "마스킹_비율": mask_ratio,
        "위험도_등급": risk_level,
        "위험도_설명": risk_desc,
    }


# ──────────────────────────────────────────────
# 3. 콘솔 출력 헬퍼
# ──────────────────────────────────────────────

def print_report(report: pd.DataFrame, risk: dict) -> None:
    """터미널 데모용 출력 함수"""
    print("\n" + "=" * 40)
    print("         PII 탐지 리포트")
    print("=" * 40)
    print(report.to_string(index=False))
    print("-" * 40)
    print(f"  마스킹 비율  : {risk['마스킹_비율']} %")
    print(f"  위험도 등급  : {risk['위험도_등급']}")
    print(f"  메시지       : {risk['위험도_설명']}")
    print("=" * 40 + "\n")
