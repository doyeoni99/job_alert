"""
사람인(saramin.co.kr) 채용공고 검색 결과 스크래퍼.

robots.txt(https://www.saramin.co.kr/robots.txt) 기준 검색 결과 경로는
크롤링 제한 대상이 아님을 확인하고 사용한다.
"""
import re

import requests
from bs4 import BeautifulSoup

from config import REQUEST_TIMEOUT, USER_AGENT
from filters import is_data_related, matches_entry_level

BASE_URL = "https://www.saramin.co.kr"
SEARCH_URL = f"{BASE_URL}/zf_user/search/recruit"

# "데이터"만 검색해서 넓게 가져온 뒤, 제목을 DATA_KEYWORDS로 다시 걸러낸다.
SEARCH_KEYWORD = "데이터"

_CAREER_SPAN_RE = re.compile(r"(신입|경력|무관)")


def fetch() -> list[dict]:
    params = {
        "searchType": "search",
        "searchword": SEARCH_KEYWORD,
        "recruitPageCount": 100,
    }
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(SEARCH_URL, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    results = []

    for item in soup.select("div.item_recruit"):
        rec_idx = item.get("value")
        title_tag = item.select_one("h2.job_tit a")
        if not rec_idx or not title_tag:
            continue

        title = (title_tag.get("title") or title_tag.get_text(strip=True)).strip()
        if not is_data_related(title):
            continue

        career_text = ""
        condition = item.select_one("div.job_condition")
        if condition:
            for span in condition.find_all("span", recursive=False):
                text = span.get_text(strip=True)
                if _CAREER_SPAN_RE.search(text):
                    career_text = text
                    break
        if not matches_entry_level(career_text):
            continue

        company_tag = item.select_one("div.area_corp strong.corp_name")
        company = company_tag.get_text(strip=True) if company_tag else "회사명 미상"

        deadline_tag = item.select_one("div.job_date span.date")
        deadline = deadline_tag.get_text(strip=True) if deadline_tag else ""

        href = title_tag.get("href", "")
        url = href if href.startswith("http") else BASE_URL + href

        results.append({
            "id": rec_idx,
            "source": "사람인",
            "title": title,
            "company": company,
            "career": career_text,
            "deadline": deadline,
            "url": url,
        })

    return results
