import re
from konlpy.tag import Okt
from address_dict import ADDRESS_SET

ADDRESS_PATTERN = re.compile(r"[가-힣]+시 [가-힣]+구 [가-힣]+동")

_okt = None


def _get_okt():
    global _okt
    if _okt is None:
        _okt = Okt()
    return _okt


def detect_address(text: str) -> list[dict]:
    seen = set()
    results = []

    # 1. 정규식: "XX시 XX구 XX동" 패턴 탐지
    for match in ADDRESS_PATTERN.findall(text):
        if match not in seen:
            seen.add(match)
            results.append({"type": "주소", "value": match})

    # 2. KoNLPy 명사 추출 후 ADDRESS_SET 매칭
    for noun in _get_okt().nouns(text):
        if noun in ADDRESS_SET and noun not in seen:
            seen.add(noun)
            results.append({"type": "주소", "value": noun})

    return results


def mask_address(text: str) -> str:
    detected = detect_address(text)
    # 긴 값부터 교체해야 짧은 값이 이미 교체된 부분에 중복 적용되지 않음
    values = sorted({d["value"] for d in detected}, key=len, reverse=True)
    for value in values:
        text = text.replace(value, "***")
    return text
