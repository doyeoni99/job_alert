import sys

from config import MAX_ITEMS_PER_SITE
from notifier import send_job_alert
from scrapers import incruit, jasoseol, saramin
from storage import load_state, save_state

# (표시용 이름, state 저장 키, fetch 함수)
SIMPLE_SOURCES = [
    ("사람인", "saramin", saramin.fetch),
    ("인크루트", "incruit", incruit.fetch),
]


def _split_new(jobs: list[dict], seen_ids: list[str]) -> tuple[list[dict], list[str]]:
    seen_set = set(seen_ids)
    new_jobs = [j for j in jobs if j["id"] not in seen_set][:MAX_ITEMS_PER_SITE]
    new_ids = [j["id"] for j in new_jobs]
    return new_jobs, new_ids


def main() -> int:
    state = load_state()
    exit_code = 0
    jobs_by_source: dict[str, list[dict]] = {}
    new_ids_by_key: dict[str, list[str]] = {}
    counts = []

    for display_name, key, fetch_fn in SIMPLE_SOURCES:
        try:
            jobs = fetch_fn()
        except Exception as e:
            print(f"[{display_name}] 수집 실패: {e}", file=sys.stderr)
            jobs = []
            exit_code = 1

        new_jobs, new_ids = _split_new(jobs, state[key])
        jobs_by_source[display_name] = new_jobs
        new_ids_by_key[key] = new_ids
        counts.append(f"{display_name} {len(new_jobs)}")

    try:
        jasoseol_jobs, new_jasoseol_last_id = jasoseol.fetch(state["jasoseol_last_id"])
    except Exception as e:
        print(f"[자소설닷컴] 수집 실패: {e}", file=sys.stderr)
        jasoseol_jobs, new_jasoseol_last_id = [], state["jasoseol_last_id"]
        exit_code = 1

    # 자소설닷컴은 last_id 기준으로 이미 신규만 수집되므로 그대로 사용
    new_jasoseol = jasoseol_jobs[:MAX_ITEMS_PER_SITE]
    jobs_by_source["자소설닷컴"] = new_jasoseol
    counts.append(f"자소설닷컴 {len(new_jasoseol)}")

    total_new = sum(len(v) for v in jobs_by_source.values())
    print(f"신규 공고: {' / '.join(counts)} (총 {total_new}건)")

    if total_new > 0:
        try:
            send_job_alert(jobs_by_source)
        except Exception as e:
            print(f"이메일 발송 실패: {e}", file=sys.stderr)
            exit_code = 1

    for _, key, _ in SIMPLE_SOURCES:
        state[key] = state[key] + new_ids_by_key[key]
    state["jasoseol_last_id"] = new_jasoseol_last_id
    save_state(state)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
