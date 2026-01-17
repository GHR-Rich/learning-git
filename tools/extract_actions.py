import csv
import re
from pathlib import Path

import yaml  # pip install pyyaml

CONFIG = Path("config/actions.yaml")
INPUT = Path("data/notes.txt")
OUTPUT = Path("data/actions.csv")

PRIORITY_RE = re.compile(r"\bP([1-3])\b", re.IGNORECASE)
ACCOUNT_RE = re.compile(r"\bAccount:\s*([^-\n]+)", re.IGNORECASE)
OWNER_RE = re.compile(r"\bOwner:\s*([^)]+)", re.IGNORECASE)
DUE_RE = re.compile(r"\bDue:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})\b", re.IGNORECASE)


def load_config() -> dict:
    if not CONFIG.exists():
        raise FileNotFoundError(f"Missing config file: {CONFIG}")
    with CONFIG.open() as f:
        return yaml.safe_load(f) or {}


def is_action(line: str, cfg: dict) -> bool:
    s = line.strip()
    if not s:
        return False

    s_lower = s.lower()
    keywords = tuple((cfg.get("action_keywords") or []))
    prefixes = tuple((cfg.get("action_prefixes") or []))

    if any(k.lower() in s_lower for k in keywords):
        return True
    if any(s.startswith(p) for p in prefixes):
        return True
    return False


def normalize_priority(p_num: str) -> str:
    # P1 highest
    return f"P{p_num}"


def confidence_for_line(line: str) -> str:
    # Very simple heuristic: explicit "Action:" or checkbox implies high confidence
    l = line.lower()
    if "action:" in l or l.strip().startswith("- [ ]") or l.strip().startswith("todo:"):
        return "High"
    # keyword-only matches are medium
    return "Medium"


def extract_fields(line: str) -> dict:
    priority = ""
    account = ""
    owner = ""
    due_date = ""

    m = PRIORITY_RE.search(line)
    if m:
        priority = normalize_priority(m.group(1))

    m = ACCOUNT_RE.search(line)
    if m:
        account = m.group(1).strip()

    m = OWNER_RE.search(line)
    if m:
        owner = m.group(1).strip()

    m = DUE_RE.search(line)
    if m:
        due_date = m.group(1).strip()

    return {
        "priority": priority,
        "account": account,
        "owner": owner,
        "due_date": due_date,
    }


def main() -> None:
    if not INPUT.exists():
        raise FileNotFoundError(f"Missing input file: {INPUT}")

    cfg = load_config()
    rows = []

    for idx, line in enumerate(INPUT.read_text().splitlines(), start=1):
        if is_action(line, cfg):
            fields = extract_fields(line)
            rows.append({
                "action": line.strip(),
                "owner": fields["owner"],
                "due_date": fields["due_date"],
                "account": fields["account"],
                "priority": fields["priority"],
                "confidence": confidence_for_line(line),
                "source_line": idx,
            })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["action", "owner", "due_date", "account", "priority", "confidence", "source_line"]
    with OUTPUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} actions to {OUTPUT}")


if __name__ == "__main__":
    main()
