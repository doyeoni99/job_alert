import json
import os

from config import STATE_FILE

_DEFAULT_STATE = {
    "saramin": [],
    "incruit": [],
    "jasoseol_last_id": 0,
}

# 사이트별로 저장해 둘 최대 ID 개수 (파일이 무한히 커지지 않도록)
_MAX_SEEN_IDS = 1000


def load_state() -> dict:
    if not os.path.exists(STATE_FILE):
        return {"first_run": True, **_DEFAULT_STATE}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)
    for key, default in _DEFAULT_STATE.items():
        state.setdefault(key, default)
    state["first_run"] = False
    return state


def save_state(state: dict) -> None:
    state = dict(state)
    state.pop("first_run", None)
    for site in ("saramin", "incruit"):
        state[site] = state[site][-_MAX_SEEN_IDS:]
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
