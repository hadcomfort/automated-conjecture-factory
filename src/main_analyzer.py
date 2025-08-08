# src/main_analyzer.py

import json
import os
import re
import time
import logging
import traceback
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError

# --- Import Core Modules ---
from core.conjecture_engine import (
    test_polynomial_conjecture,
    test_linear_recurrence_conjecture,
    test_exponential_conjecture
)
from core.target_finder import fetch_b_file_data
from core.reporting import create_pr_for_finding


# -------------------------
# Configuration via env vars
# -------------------------

def _get_env_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "y", "on")

def _get_env_int(name: str, default: int, min_value: Optional[int] = None) -> int:
    val = os.getenv(name)
    if val is None:
        return default
    try:
        iv = int(val)
        if min_value is not None and iv < min_value:
            return default
        return iv
    except Exception:
        return default

def _get_env_float(name: str, default: float, min_value: Optional[float] = None) -> float:
    val = os.getenv(name)
    if val is None:
        return default
    try:
        fv = float(val)
        if min_value is not None and fv < min_value:
            return default
        return fv
    except Exception:
        return default

def _get_env_list(name: str, default: List[str]) -> List[str]:
    val = os.getenv(name)
    if not val:
        return default
    return [x.strip() for x in val.split(",") if x.strip()]

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
# Timeout per test in seconds
TEST_TIMEOUT_SEC = _get_env_int("TEST_TIMEOUT_SEC", 60, min_value=1)
# Which tests to run, in order; default preserves your original order
ENABLE_TESTS = _get_env_list("ENABLE_TESTS", ["poly", "rec", "exp"])
# Simple fetch retry policy
MAX_FETCH_RETRIES = _get_env_int("MAX_FETCH_RETRIES", 3, min_value=1)
FETCH_RETRY_BASE_SLEEP = _get_env_float("FETCH_RETRY_BASE_SLEEP", 1.0, min_value=0.0)
# Disk cache controls
CACHE_ENABLED = _get_env_bool("CACHE_ENABLED", True)
CACHE_TTL_HOURS = _get_env_int("CACHE_TTL_HOURS", 720, min_value=1)  # default 30 days
CACHE_DIR = os.path.join("data", "cache", "sequence_data")
# Dry run skips PR creation (logs instead)
DRY_RUN = _get_env_bool("DRY_RUN", False)


# -------------------------
# Helpers: logging, cache, validation
# -------------------------

def setup_logging() -> None:
    # Avoid duplicate handlers if imported-run; keep behavior close to original
    root = logging.getLogger()
    if root.handlers:
        for h in list(root.handlers):
            root.removeHandler(h)

    root.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # File handler
    fh = logging.FileHandler('project_log.log', mode='a', encoding='utf-8')
    fh.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    fh.setFormatter(formatter)
    root.addHandler(fh)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    ch.setFormatter(formatter)
    root.addHandler(ch)

def ensure_dir(path: str) -> None:
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        # Non-fatal
        logging.debug("Failed to create directory: %s", path)

def is_valid_oeis_id(s: str) -> bool:
    # Accepts standard OEIS IDs like A000045, allow any digit length after A
    return bool(re.fullmatch(r"A\d{3,}", s.strip()))

def cache_path_for(oeis_id: str) -> str:
    return os.path.join(CACHE_DIR, f"{oeis_id}.json")

def load_from_cache(oeis_id: str) -> Optional[Any]:
    if not CACHE_ENABLED:
        return None
    path = cache_path_for(oeis_id)
    if not os.path.exists(path):
        return None
    try:
        mtime = datetime.fromtimestamp(os.path.getmtime(path))
        if datetime.now() - mtime > timedelta(hours=CACHE_TTL_HOURS):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.debug("Cache load failed for %s: %s", oeis_id, e)
        return None

def save_to_cache(oeis_id: str, data: Any) -> None:
    if not CACHE_ENABLED:
        return
    try:
        ensure_dir(CACHE_DIR)
        with open(cache_path_for(oeis_id), "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception as e:
        logging.debug("Cache save failed for %s: %s", oeis_id, e)

def fetch_sequence_data_with_retries(oeis_id: str) -> Optional[Any]:
    # Use cache first
    cached = load_from_cache(oeis_id)
    if cached is not None:
        logging.info("Loaded %s from cache.", oeis_id)
        return cached

    # Fetch with retries
    last_err = None
    for attempt in range(1, MAX_FETCH_RETRIES + 1):
        try:
            data = fetch_b_file_data(oeis_id)
            if data:
                save_to_cache(oeis_id, data)
                return data
            else:
                last_err = RuntimeError("Empty or falsy data returned")
        except Exception as e:
            last_err = e
        sleep_s = FETCH_RETRY_BASE_SLEEP * (2 ** (attempt - 1))
        logging.warning("Fetch attempt %d/%d for %s failed: %s. Retrying in %.1fs",
                        attempt, MAX_FETCH_RETRIES, oeis_id, last_err, sleep_s)
        time.sleep(sleep_s)

    logging.error("Failed to fetch data for %s after %d attempts. Last error: %s",
                  oeis_id, MAX_FETCH_RETRIES, last_err)
    return None


# -------------------------
# Test execution helpers
# -------------------------

def get_test_callable(name: str):
    key = name.lower()
    if key in ("poly", "polynomial"):
        return "polynomial", test_polynomial_conjecture
    if key in ("rec", "recurrence", "linrec", "linear"):
        return "linear_recurrence", test_linear_recurrence_conjecture
    if key in ("exp", "exponential"):
        return "exponential", test_exponential_conjecture
    return None, None

def run_test_with_timeout(label: str, fn, sequence_data: Any, timeout_sec: int) -> Dict[str, Any]:
    # Run test in separate thread to allow timeout; return a result dict even on error
    def _invoke():
        return fn(sequence_data)

    with ThreadPoolExecutor(max_workers=1) as ex:
        fut = ex.submit(_invoke)
        try:
            result = fut.result(timeout=timeout_sec)
            # Enforce result shape with a default if function returns unexpected type
            if not isinstance(result, dict):
                return {"status": "error", "error": f"{label} returned non-dict", "raw": str(result)}
            return result
        except TimeoutError:
            return {"status": "error", "error": f"{label} timed out after {timeout_sec}s"}
        except Exception:
            return {"status": "error", "error": f"{label} raised exception", "trace": traceback.format_exc()}


# -------------------------
# Main
# -------------------------

def main():
    """
    Main orchestrator to analyze candidate sequences for conjectures.

    Improvements:
    - Optional disk cache for fetched sequence data with TTL (env: CACHE_ENABLED, CACHE_TTL_HOURS)
    - Fetch retries with backoff (env: MAX_FETCH_RETRIES, FETCH_RETRY_BASE_SLEEP)
    - Per-test timeouts and exception isolation (env: TEST_TIMEOUT_SEC)
    - Run tests concurrently per sequence while preserving reporting order (env: ENABLE_TESTS)
    - Optional dry-run that skips PR creation (env: DRY_RUN)
    """
    setup_logging()
    run_id = f"run-{int(time.time())}"
    logging.info("Starting main analyzer (processing all candidates every run)... run_id=%s", run_id)

    # --- Load Candidate Sequences ---
    candidates_path = os.path.join("data", "candidate_sequences.json")
    try:
        with open(candidates_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        if isinstance(raw, dict):
            # If someone supplied {"candidates": [...]} shape
            candidate_ids = raw.get("candidates", [])
        elif isinstance(raw, list):
            candidate_ids = raw
        else:
            logging.error("Unexpected JSON structure in %s. Expected list or dict.", candidates_path)
            return
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error("Could not load candidates from %s: %s", candidates_path, e)
        return

    # Normalize, validate, and de-duplicate while preserving order
    seen = set()
    normalized_ids = []
    for cid in candidate_ids:
        if not isinstance(cid, str):
            continue
        cid = cid.strip()
        if not is_valid_oeis_id(cid):
            logging.warning("Skipping invalid OEIS id: %r", cid)
            continue
        if cid in seen:
            continue
        seen.add(cid)
        normalized_ids.append(cid)

    logging.info("Loaded %d candidate sequences from %s (%d after validation/dedup).",
                 len(candidate_ids), candidates_path, len(normalized_ids))

    # Determine tests to run and stable reporting order
    tests_plan = []
    for t in ENABLE_TESTS:
        label, fn = get_test_callable(t)
        if label and fn:
            tests_plan.append((t, label, fn))
    if not tests_plan:
        logging.warning("No tests enabled by ENABLE_TESTS. Nothing to do.")
        return

    # Metrics
    totals = {
        "candidates_total": len(normalized_ids),
        "candidates_processed": 0,
        "fetch_success": 0,
        "fetch_failed": 0,
        "verified_total": 0,
        "verified_by_test": {lbl: 0 for _, lbl, _ in tests_plan},
        "errors_by_test": {lbl: 0 for _, lbl, _ in tests_plan},
    }
    t_start = time.time()

    # --- Process Each Candidate ---
    for oeis_id in normalized_ids:
        logging.info("--- Analyzing sequence: %s ---", oeis_id)
        per_seq_start = time.time()

        sequence_data = fetch_sequence_data_with_retries(oeis_id)
        if not sequence_data:
            logging.warning("Could not fetch data for %s. Skipping.", oeis_id)
            totals["fetch_failed"] += 1
            continue

        totals["fetch_success"] += 1

        # Run all enabled tests concurrently per sequence
        results: Dict[str, Dict[str, Any]] = {}
        with ThreadPoolExecutor(max_workers=len(tests_plan)) as ex:
            futures = {}
            for t_key, label, fn in tests_plan:
                futures[ex.submit(run_test_with_timeout, label, fn, sequence_data, TEST_TIMEOUT_SEC)] = (t_key, label)
            for fut in as_completed(futures):
                t_key, label = futures[fut]
                try:
                    res = fut.result()
                except Exception:
                    res = {"status": "error", "error": f"{label} future raised", "trace": traceback.format_exc()}
                results[label] = res

        any_verified = False

        # Report outcomes in deterministic original order: poly -> rec -> exp
        for _, label, _ in tests_plan:
            res = results.get(label, {"status": "error", "error": "missing result"})
            status = res.get("status")
            if status == "verified":
                totals["verified_total"] += 1
                totals["verified_by_test"][label] = totals["verified_by_test"].get(label, 0) + 1
                logging.info("[%s] Verified conjecture for %s.", label, oeis_id)
                if DRY_RUN:
                    logging.info("DRY_RUN=1 -> skipping PR creation for %s (%s).", oeis_id, label)
                else:
                    try:
                        create_pr_for_finding(oeis_id, res, sequence_data)
                    except Exception:
                        logging.error("Failed to create PR for %s (%s): %s", oeis_id, label, traceback.format_exc())
                any_verified = True
            elif status == "error":
                totals["errors_by_test"][label] = totals["errors_by_test"].get(label, 0) + 1
                err_msg = res.get("error", "unknown error")
                logging.info("No %s result for %s (error: %s).", label, oeis_id, err_msg)
                if "trace" in res:
                    logging.debug("Trace for %s %s:\n%s", oeis_id, label, res["trace"])
            else:
                # status like "unverified", "no_match", etc.
                logging.info("No simple %s found for %s.", label.replace("_", " "), oeis_id)

        totals["candidates_processed"] += 1
        per_seq_elapsed = time.time() - per_seq_start
        if any_verified:
            logging.info("--- Finished analysis for %s (new findings created). [%.2fs] ---", oeis_id, per_seq_elapsed)
        else:
            logging.info("--- Finished analysis for %s (no conjectures verified). [%.2fs] ---", oeis_id, per_seq_elapsed)

    # Summary
    elapsed = time.time() - t_start
    logging.info("Main analyzer has completed its run. run_id=%s", run_id)
    logging.info("Summary: processed %d/%d candidates in %.2fs; fetch ok=%d, fetch failed=%d, verified=%d",
                 totals["candidates_processed"], totals["candidates_total"], elapsed,
                 totals["fetch_success"], totals["fetch_failed"], totals["verified_total"])
    for lbl, cnt in totals["verified_by_test"].items():
        logging.info("  Verified by %-20s: %d", lbl, cnt)
    for lbl, cnt in totals["errors_by_test"].items():
        if cnt:
            logging.info("  Errors in %-22s: %d", lbl, cnt)


if __name__ == "__main__":
    main()
