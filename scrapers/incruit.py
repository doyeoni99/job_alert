"""
인크루트(incruit.com) 채용공고 검색 결과 스크래퍼.

robots.txt(https://www.incruit.com/robots.txt)를 확인한 결과, 이름이 지정된
크롤러(Google, Naver, Bing, GPTBot, ClaudeBot, anthropic-ai 등)에는 명시적으로
`Allow: /`가 적용되어 있고, 이름이 없는 일반 크롤러(`User-agent: *`)만
`Disallow: /`로 막혀 있다. Claude 계열 크롤러는 명시적으로 허용되어 있으므로
사용한다.

주의: 이 사이트는 EUC-KR 인코딩을 사용하며, 검색 결과 페이지에서 명시적인
페이지네이션 파라미터를 찾지 못해 한 번의 요청으로 오는 기본 결과(첫 페이지,
수 건~수십 건 수준)만 가져온다.
"""
import re

import requests
from bs4 import BeautifulSoup

from config import REQUEST_TIMEOUT, USER_AGENT
from filters import is_data_related, matches_entry_level

BASE_URL = "https://search.incruit.com"
SEARCH_URL = f"{BASE_URL}/list/search.asp"

# "데이터"를 EUC-KR로 percent-encoding한 값 (col=job: 채용공고 검색)
SEARCH_QUERY = "col=job&kw=%B5%A5%C0%CC%C5%CD"

_CAREER_SPAN_RE = re.compile(r"(신입|경력|무관)")


def fetch() -> list[dict]:
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(f"{SEARCH_URL}?{SEARCH_QUERY}", headers=headers, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    resp.encoding = "euc-kr"

    soup = BeautifulSoup(resp.text, "html.parser")
    results = []

    for row in soup.select("ul.c_row"):
        job_id = row.get("jobno")
        title_tag = row.select_one('div.cell_mid div.cl_top a[href*="jobpost.asp"]')
        if not job_id or not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        if not is_data_related(title):
            continue

        career_text = ""
        condition = row.select_one("div.cell_mid div.cl_md")
        if condition:
            for span in condition.find_all("span", recursive=False):
                text = span.get_text(strip=True)
                if _CAREER_SPAN_RE.search(text):
                    career_text = text
                    break
        if not matches_entry_level(career_text):
            continue

        company_tag = row.select_one("div.cell_first a.cpname")
        company = company_tag.get_text(strip=True) if company_tag else "회사명 미상"

        deadline = ""
        deadline_area = row.select_one("div.cell_last div.cl_btm")
        if deadline_area:
            first_span = deadline_area.find("span")
            if first_span:
                deadline = first_span.get_text(strip=True)

        url = title_tag.get("href", "")

        results.append({
            "id": job_id,
            "source": "인크루트",
            "title": title,
            "company": company,
            "career": career_text,
            "deadline": deadline,
            "url": url,
        })

    return results
