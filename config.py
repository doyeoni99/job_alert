import os

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
REQUEST_TIMEOUT = 15

# 데이터 관련 직무로 판단할 키워드 (제목 기준, 대소문자 무시).
# "데이터"라는 단어 자체를 기본으로 넓게 잡는다 - 자소설닷컴처럼 제목이
# "OO 신입사원 모집"처럼 짧고 포괄적인 사이트에서는 "데이터분석"류의
# 구체적인 복합어로는 거의 걸러지지 않기 때문. 영문 표기는 별도로 추가.
DATA_KEYWORDS = [
    "데이터",
    "data analyst", "data scientist", "data engineer", "data analysis", "data science",
]

# 신입/경력무관으로 판단할 키워드 (career 필드 또는 제목에 포함되면 통과)
ENTRY_LEVEL_KEYWORDS = ["신입", "무관"]

# 이메일 발신/수신 설정 (GitHub Actions Secrets 또는 로컬 환경변수로 주입)
EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")
EMAIL_TO = os.environ.get("EMAIL_TO", EMAIL_ADDRESS)

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465

STATE_FILE = os.path.join(os.path.dirname(__file__), "data", "seen.json")

# 사이트별로 한 번 실행에 보낼 최대 신규 공고 수 (이메일이 너무 길어지지 않도록 제한)
MAX_ITEMS_PER_SITE = 30
