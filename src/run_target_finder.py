# src/run_target_finder.py

import json
import os
import logging
from datetime import datetime

from core.target_finder import find_candidate_sequences

def setup_runner_logging():
    """Sets up basic logging for this script, consistent with the main analyzer."""
    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("project_log.log", mode='a', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

def main():
    """
    Main execution function to find and save candidate OEIS sequences.
    This version updates the existing list of candidates rather than overwriting it,
    and searches for high-value 'unkn' sequences.
    """
    setup_runner_logging()
    logging.info("Starting the process to find and update candidate OEIS sequences...")

    # --- Configuration ---
    output_dir = "data"
    output_path = os.path.join(output_dir, "candidate_sequences.json")
    # Strategy: Search for sequences with 'unkn' keyword. These have no known formula.
    search_query = "keyword:unkn"
    num_to_find = 100

    # --- 1. Load Existing Candidates ---
    existing_candidates = []
    existing_ids = set()
    try:
        if os.path.exists(output_path):
            with open(output_path, "r", encoding="utf-8") as f:
                # Support both simple list of IDs and list of dicts with IDs
                loaded_data = json.load(f)
                for item in loaded_data:
                    # Normalize to our new format of dicts
                    if isinstance(item, str):
                        existing_candidates.append({"oeis_id": item, "comment": "Legacy entry."})
                        existing_ids.add(item)
                    elif isinstance(item, dict) and "oeis_id" in item:
                        existing_candidates.append(item)
                        existing_ids.add(item["oeis_id"])

            logging.info(f"Loaded {len(existing_ids)} existing candidates from {output_path}.")
    except (IOError, json.JSONDecodeError) as e:
        logging.warning(f"Could not read existing candidates file. Starting fresh. Error: {e}")

    # --- 2. Find New Candidates ---
    logging.info("Searching for new candidate sequences...")
    new_candidate_ids = find_candidate_sequences(search_query=search_query, count=num_to_find)

    if not new_candidate_ids:
        logging.info("No new candidate sequences were found in this run.")
        return

    # --- 3. Combine and De-duplicate (BUG FIX HERE) ---
    newly_added_count = 0
    for oeis_id in new_candidate_ids:
        if oeis_id not in existing_ids:
            existing_candidates.append({
                "oeis_id": oeis_id,
                "comment": f"Found via '{search_query}' search on {datetime.now().strftime('%Y-%m-%d')}"
            })
            existing_ids.add(oeis_id)
            newly_added_count += 1
    
    if newly_added_count > 0:
        logging.info(f"Added {newly_added_count} new unique candidates.")
    else:
        logging.info("No new unique candidates were found to add to the list.")

    # --- 4. Save the Updated List ---
    os.makedirs(output_dir, exist_ok=True)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(existing_candidates, f, indent=4)
        logging.info(f"Successfully saved a total of {len(existing_candidates)} candidates to: {output_path}")
    except IOError as e:
        logging.error(f"Error saving updated candidate sequences to file: {e}")

if __name__ == "__main__":
    main()
