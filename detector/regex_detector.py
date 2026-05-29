import re

# ── 계좌번호 패턴 ────────────────────────────────────────────────────────────
HYPHENATED_PATTERNS = [
    r"\b\d{3,6}-\d{2,6}-\d{5,8}\b",
    r"\b\d{3,4}-\d{4}-\d{4}-\d{1,3}\b",
    r"\b\d{3}-\d{6}-\d{2}-\d{3}\b",
    r"\b\d{8}-\d{2}\b",
    r"\b\d{3}-\d{8}\b",
    r"\b\d{4}-\d{4}-\d{4}\b",
]

UNHYPHENATED_PATTERNS = [
    r"\b(?:3333|3388|3355|3310|7777|9979)\d{9}\b",
    r"\b(?:1002|1005|1006|1007|1003|1004)\d{9}\b",
    r"\b(?:301|302|312|306|305|317|351|352|356|355)\d{10}\b",
    r"\b(?:100|110|120|130|140|150|155|160|180)\d{9}\b",
    r"\b(?:100|106|150|190|200|300|700)\d{9}\b",
    r"\b(?:100|110|120|190|530)\d{9}\b",
    r"\b(?:101|201|102|202|209|103|208|106|108|113|114|206)\d{9}\b",
    r"\b(?:013|020|019|011|022)\d{11}\b",
]

_ACCOUNT_REGEX = re.compile("|".join(HYPHENATED_PATTERNS + UNHYPHENATED_PATTERNS))

# ── PII 탐지 규칙 ────────────────────────────────────────────────────────────
_PII_RULES = {
    "주민등록번호": re.compile(r"\d{6}[-–]\d{7}"),
    "전화번호":     re.compile(r"0\d{1,2}[-.\s]?\d{3,4}[-.\s]?\d{4}"),
    "이메일":       re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"),
    "계좌번호":     _ACCOUNT_REGEX,
}


def mask_pii(text: str, token: str = "[REDACTED]") -> tuple[str, list[dict]]:
    """
    정규식 기반 PII 탐지 및 마스킹.

    Returns
    -------
    (masked_text, detected_list)
        detected_list : [{"유형": str, "원문": str}, ...]
    """
    if token == r"\*\*\*":
        token = "***"

    detected_list: list[dict] = []
    result = text

    for pii_type, regex in _PII_RULES.items():
        for m in regex.finditer(result):
            detected_list.append({"유형": pii_type, "원문": m.group(0)})
        result = regex.sub(token, result)

    return result, detected_list
