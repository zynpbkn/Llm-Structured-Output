import os, sys, json, time, logging
from uuid import uuid4
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from app.llm_chain import extract_ticket

load_dotenv()  # load GOOGLE_API_KEY

# --- configure logger ---
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True, parents=True)

logger = logging.getLogger("week05")
logger.setLevel(logging.INFO)

# console handler
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)

# file handler
fh = logging.FileHandler(logs_dir / "run.log", encoding="utf-8")
fh.setLevel(logging.INFO)

# formatter
formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
ch.setFormatter(formatter)
fh.setFormatter(formatter)

logger.addHandler(ch)
logger.addHandler(fh)
# -------------------------

def main():
    if len(sys.argv) < 2:
        logger.error("Usage: python -m app.main /path/to/support_tickets_minimal.csv")
        sys.exit(1)

    csv_path = sys.argv[1]
    df = pd.read_csv(csv_path)

    if not {"user_id", "sikayet"}.issubset(df.columns):
        logger.error(f"Expected columns user_id and sikayet. Found: {list(df.columns)}")
        sys.exit(1)

    out_path = logs_dir / "outputs.jsonl"
    run_id = str(uuid4())
    max_retries = 2

    with open(out_path, "a", encoding="utf-8") as fout:
        for _, row in df.iterrows():
            source_id = str(row["user_id"])
            ticket_text = str(row["sikayet"])

            attempts = 0
            while True:
                try:
                    result = extract_ticket(ticket_text)
                    payload = result.model_dump()
                    # log to console/file (pretty JSON one-liner)
                    logger.info("row %s: %s", source_id, json.dumps(payload, ensure_ascii=False))
                    # append JSONL with metadata
                    fout.write(json.dumps({
                        "run_meta": {"run_id": run_id, "source_id": source_id, "ts": time.time()},
                        "data": payload
                    }, ensure_ascii=False) + "\n")
                    break
                except Exception as e:
                    if attempts >= max_retries:
                        logger.error("row %s failed permanently: %s", source_id, e)
                        break
                    attempts += 1
                    logger.warning("row %s failed (attempt %d), retrying: %s", source_id, attempts, e)
                    time.sleep(1.5 ** attempts)

    logger.info("Done. Wrote logs to %s", out_path)

if __name__ == "__main__":
    main()
