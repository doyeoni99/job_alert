"""
자소설닷컴(jasoseol.com) 채용공고 스크래퍼.

robots.txt(https://jasoseol.com/robots.txt)는 전체 허용(Allow: /) 정책이며
/recruit 경로도 제한되어 있지 않음을 확인하고 사용한다.

이 사이트의 채용 목록 페이지(/recruit)는 캘린더형 위젯으로 클라이언트에서
데이터를 불러오는 방식이라 키워드 검색이 불가능하다. 대신 사이트맵
(sitemap/employment_companies.xml)에서 최근 등록된 공고 ID 목록을 가져와
개별 상세 페이지(/recruit/{id})를 순회하며 제목을 키워드로 필터링한다.
"""
import html
import re
import time

import requests
from bs4 import BeautifulSoup

from config import REQUEST_TIMEOUT, USER_AGENT
from filters import is_data_related, is_probably_entry_level_or_unspecified

BASE_URL = "https://jasoseol.com"
SITEMAP_URL = f"{BASE_URL}/sitemap/employment_companies.xml"

_RECRUIT_LOC_RE = re.compile(r"<loc>https://jasoseol\.com/recruit/(\d+)</loc>")
_TITLE_RE = re.compile(r"^(?P<company>.+?)\s*채용공고\s*-\s*(?P<position>.+?)\s*\|")

# 한 번 실행에 상세 페이지를 확인할 최대 개수 (사이트 부하 및 실행 시간 제한)
MAX_DETAIL_FETCH = 80
REQUEST_DELAY_SEC = 0.3


def _get_recent_ids(headers: dict) -> list[int]:
    resp = requests.get(SITEMAP_URL, headers=headers, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    ids = {int(m) for m in _RECRUIT_LOC_RE.findall(resp.text)}
    return sorted(ids, reverse=True)


def _fetch_detail(job_id: int, headers: dict) -> dict | None:
    url = f"{BASE_URL}/recruit/{job_id}"
    try:
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    except requests.RequestException:
        return None
    if resp.status_code != 200:
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    if not soup.title or not soup.title.string:
        return None

    title_text = html.unescape(soup.title.string.strip())
    m = _TITLE_RE.match(title_text)
    if not m:
        return None

    return {
        "id": str(job_id),
        "source": "자소설닷컴",
        "title": m.group("position").strip(),
        "company": m.group("company").strip(),
        "career": "",
        "deadline": "",
        "url": url,
    }


def fetch(last_seen_id: int) -> tuple[list[dict], int]:
    headers = {"User-Agent": USER_AGENT}
    ids = _get_recent_ids(headers)
    if not ids:
        return [], last_seen_id

    max_id = ids[0]
    candidate_ids = [i for i in ids if i > last_seen_id][:MAX_DETAIL_FETCH]

    results = []
    for job_id in candidate_ids:
        detail = _fetch_detail(job_id, headers)
        time.sleep(REQUEST_DELAY_SEC)
        if not detail:
            continue
        if not is_data_related(detail["title"]):
            continue
        if not is_probably_entry_level_or_unspecified(detail["title"]):
            continue
        results.append(detail)

    return results, max_id
