import csv
from pathlib import Path

INPUT = Path("data/notes.txt")
OUTPUT = Path("data/actions.csv")

ACTION_KEYWORDS = ("follow up", "send", "review", "schedule", "confirm", "action:")

def is_action(line: str) -> bool:
    s = line.strip().lower()
    return any(k in s for k in ACTION_KEYWORDS)

def main() -> None:
    if not INPUT.exists():
        raise FileNotFoundError(f"Missing input file: {INPUT}")

    rows = []
    for line in INPUT.read_text().splitlines():
        if line.strip() and is_action(line):
            rows.append({"action": line.strip(), "owner": "", "due_date": ""})

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["action", "owner", "due_date"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} actions to {OUTPUT}")

if __name__ == "__main__":
    main()
