# src/run_target_finder.py

import json
import os
import logging
from datetime import datetime

# Important: Import happens AFTER logging is configured in main()
# to ensure module-level code in target_finder also gets logged.

def setup_runner_logging():
    """Sets up basic logging for this script, consistent with the main analyzer."""
    root = logging.getLogger()
    # Clear any existing handlers to avoid duplicates
    if root.handlers:
        for handler in root.handlers[:]:
            root.removeHandler(handler)
            
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("project_log.log", mode='a', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def find_and_update_candidates():
    # Now we call the function which will use the pre-configured session
    from core.target_finder import find_candidate_sequences
    
    logging.info("Starting the process to find and update candidate OEIS sequences...")
    output_dir = "data"
    output_path = os.path.join(output_dir, "candidate_sequences.json")
    search_query = "keyword:unkn"
    num_to_find = 100

    existing_candidates = []
    existing_ids = set()
    try:
        if os.path.exists(output_path):
            with open(output_path, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
                for item in loaded_data:
                    if isinstance(item, str):
                        existing_candidates.append({"oeis_id": item, "comment": "Legacy entry."})
                        existing_ids.add(item)
                    elif isinstance(item, dict) and "oeis_id" in item:
                        existing_candidates.append(item)
                        existing_ids.add(item["oeis_id"])
            logging.info(f"Loaded {len(existing_ids)} existing candidates from {output_path}.")
    except (IOError, json.JSONDecodeError) as e:
        logging.warning(f"Could not read existing candidates file. Starting fresh. Error: {e}")

    logging.info("Searching for new candidate sequences...")
    new_candidate_ids = find_candidate_sequences(search_query=search_query, count=num_to_find)

    if not new_candidate_ids:
        logging.info("No new candidate sequences were found in this run.")
        return

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

    os.makedirs(output_dir, exist_ok=True)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(existing_candidates, f, indent=4)
        logging.info(f"Successfully saved a total of {len(existing_candidates)} candidates to: {output_path}")
    except IOError as e:
        logging.error(f"Error saving updated candidate sequences to file: {e}")


def main():
    """Main entry point for finding new target sequences."""
    setup_runner_logging()
    find_and_update_candidates()


if __name__ == "__main__":
    main()
