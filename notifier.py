import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import EMAIL_ADDRESS, EMAIL_PASSWORD, EMAIL_TO, SMTP_HOST, SMTP_PORT


def _build_html(jobs_by_source: dict[str, list[dict]]) -> str:
    parts = ["<h2>오늘의 데이터 관련 신입/경력무관 채용공고</h2>"]
    for source, jobs in jobs_by_source.items():
        if not jobs:
            continue
        parts.append(f"<h3>{source} ({len(jobs)}건)</h3><ul>")
        for job in jobs:
            deadline = f" · 마감 {job['deadline']}" if job.get("deadline") else ""
            career = f" · {job['career']}" if job.get("career") else ""
            parts.append(
                "<li>"
                f"<a href=\"{job['url']}\">{job['title']}</a>"
                f" - {job['company']}{career}{deadline}"
                "</li>"
            )
        parts.append("</ul>")
    return "\n".join(parts)


def send_job_alert(jobs_by_source: dict[str, list[dict]]) -> None:
    total = sum(len(jobs) for jobs in jobs_by_source.values())
    if total == 0:
        return

    if not EMAIL_ADDRESS or not EMAIL_PASSWORD or not EMAIL_TO:
        raise RuntimeError(
            "EMAIL_ADDRESS / EMAIL_PASSWORD / EMAIL_TO 환경변수가 설정되지 않았습니다."
        )

    msg = MIMEMultipart("alternative")
    today = datetime.now().strftime("%Y-%m-%d")
    msg["Subject"] = f"[채용알림봇] {today} 신규 데이터 직무 공고 {total}건"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_TO

    html_body = _build_html(jobs_by_source)
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, [EMAIL_TO], msg.as_string())
