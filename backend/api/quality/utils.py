"""
Quality API utility functions
"""

import re
from typing import List


def escape_like(s: str) -> str:
    """Escape special characters for SQL LIKE/ILIKE patterns."""
    return re.sub(r'([%_\\])', r'\\\1', s)


# ── Q&A 콘텐츠 필터링 ──

# 광고/스팸 키워드
_SPAM_KEYWORDS: List[str] = [
    "광고", "홍보", "클릭", "무료체험", "할인", "이벤트", "쿠폰",
    "대출", "보험", "카지노", "도박", "성인", "비아그라", "다이어트",
    "재테크", "투자수익", "부업", "알바", "수익보장", "고수익",
    "텔레그램", "카톡방", "오픈채팅", "구매대행", "직구",
]

# URL 패턴 (http/https, www, .com/.net/.kr 등)
_URL_PATTERN = re.compile(
    r'(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.(com|net|org|kr|co\.kr|io|xyz|shop|store|click|top|biz)[/\s]?)',
    re.IGNORECASE,
)

# 전화번호 패턴 (010-xxxx-xxxx, 02-xxx-xxxx 등)
_PHONE_PATTERN = re.compile(
    r'(0\d{1,2}[-.\s]?\d{3,4}[-.\s]?\d{4})',
)

# 이메일 패턴
_EMAIL_PATTERN = re.compile(
    r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
)


def validate_qna_content(text: str) -> str | None:
    """Q&A 콘텐츠 필터링. 위반 시 사유 문자열 반환, 정상이면 None."""
    if not text or not text.strip():
        return "내용을 입력해주세요"

    lower = text.lower()

    # 광고/스팸 키워드 검사
    for kw in _SPAM_KEYWORDS:
        if kw in lower:
            return f"허용되지 않는 내용이 포함되어 있습니다 (금지어: {kw})"

    # URL 검사
    if _URL_PATTERN.search(text):
        return "외부 링크(URL)는 작성할 수 없습니다"

    # 전화번호 검사
    if _PHONE_PATTERN.search(text):
        return "전화번호는 작성할 수 없습니다"

    # 이메일 검사
    if _EMAIL_PATTERN.search(text):
        return "이메일 주소는 작성할 수 없습니다"

    return None
