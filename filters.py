import re

from config import DATA_KEYWORDS, ENTRY_LEVEL_KEYWORDS

_YEARS_REQUIRED_RE = re.compile(r"경력\s*\d+\s*년")


def is_data_related(text: str) -> bool:
    lowered = text.lower()
    return any(kw.lower() in lowered for kw in DATA_KEYWORDS)


def matches_entry_level(career_text: str) -> bool:
    """career_text가 명시적으로 제공되는 사이트(사람인)에서 사용.
    '신입' 또는 '무관'이 포함된 경우에만 통과."""
    return any(kw in career_text for kw in ENTRY_LEVEL_KEYWORDS)


def is_probably_entry_level_or_unspecified(text: str) -> bool:
    """career 필드가 따로 없는 사이트(잡코리아, 자소설닷컴)에서 제목만 보고
    판단. '경력 N년'처럼 연차가 명시되어 있고 '무관'이 없으면 제외,
    그 외에는 통과시킨다(기본 포함)."""
    if _YEARS_REQUIRED_RE.search(text) and "무관" not in text:
        return False
    return True
