# src/main_analyzer.py

import json
import os
import logging

# --- Import Core Modules ---
from core.conjecture_engine import (
    test_polynomial_conjecture, 
    test_linear_recurrence_conjecture,
    test_exponential_conjecture  # <-- IMPORT THE NEW FUNCTION
)
from core.target_finder import fetch_b_file_data
from core.reporting import create_pr_for_finding

def main():
    """
    Main orchestrator to analyze candidate sequences for conjectures.

    This version processes the entire candidate list on every run and does not
    short-circuit after the first verified conjecture. All conjecture tests are
    executed for every sequence so newly added tools are applied to all existing
    candidates as well.
    """
    # --- Setup Logging ---
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='project_log.log',
        filemode='a'
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    logging.info("Starting main analyzer (processing all candidates every run)...")

    # --- Load Candidate Sequences ---
    candidates_path = os.path.join("data", "candidate_sequences.json")
    try:
        with open(candidates_path, "r") as f:
            candidate_ids = json.load(f)
        logging.info(f"Loaded {len(candidate_ids)} candidate sequences from {candidates_path}.")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Could not load candidates from {candidates_path}: {e}")
        return

    # --- Process Each Candidate (always process the full list) ---
    for oeis_id in candidate_ids:
        logging.info(f"--- Analyzing sequence: {oeis_id} ---")

        sequence_data = fetch_b_file_data(oeis_id)
        if not sequence_data:
            logging.warning(f"Could not fetch data for {oeis_id}. Skipping.")
            continue

        any_verified = False

        # 1. Test for a polynomial conjecture
        poly_result = test_polynomial_conjecture(sequence_data)
        if poly_result.get("status") == "verified":
            create_pr_for_finding(oeis_id, poly_result, sequence_data)
            any_verified = True
        else:
            logging.info(f"No simple polynomial formula found for {oeis_id}.")

        # 2. Test for a linear recurrence
        recurrence_result = test_linear_recurrence_conjecture(sequence_data)
        if recurrence_result.get("status") == "verified":
            create_pr_for_finding(oeis_id, recurrence_result, sequence_data)
            any_verified = True
        else:
            logging.info(f"No simple linear recurrence found for {oeis_id}.")

        # 3. Test for an exponential conjecture
        exp_result = test_exponential_conjecture(sequence_data)
        if exp_result.get("status") == "verified":
            create_pr_for_finding(oeis_id, exp_result, sequence_data)
            any_verified = True
        else:
            logging.info(f"No simple exponential formula found for {oeis_id}.")

        if any_verified:
            logging.info(f"--- Finished analysis for {oeis_id} (new findings created). ---")
        else:
            logging.info(f"--- Finished analysis for {oeis_id} (no conjectures verified). ---")

    logging.info("Main analyzer has completed its run.")

if __name__ == "__main__":
    main()
