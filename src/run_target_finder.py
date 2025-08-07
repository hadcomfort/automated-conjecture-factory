# src/run_target_finder.py

import json
import os
from core.target_finder import find_candidate_sequences

def main():
    """
    Main execution function to find and save candidate OEIS sequences.
    This version updates the existing list of candidates rather than overwriting it.
    """
    print("Starting the process to find and update candidate OEIS sequences...")

    # --- Define Paths and Search Parameters ---
    output_dir = "data"
    output_path = os.path.join(output_dir, "candidate_sequences.json")
    search_query = "keyword:new -keyword:easy"

    # --- 1. Load Existing Candidates (if any) ---
    existing_candidates = []
    try:
        if os.path.exists(output_path):
            with open(output_path, "r") as f:
                existing_candidates = json.load(f)
            print(f"Loaded {len(existing_candidates)} existing candidates from {output_path}.")
    except (IOError, json.JSONDecodeError) as e:
        print(f"Could not read existing candidates file. Starting fresh. Error: {e}")
        existing_candidates = []

    # --- 2. Find New Candidates ---
    print("Searching for new candidate sequences...")
    new_candidates = find_candidate_sequences(search_query=search_query, count=20)

    if not new_candidates:
        print("No new candidate sequences were found in this run.")
        return

    # --- 3. Combine and De-duplicate ---
    # We use a set for efficient de-duplication and then convert back to a list.
    combined_list = existing_candidates + new_candidates
    unique_candidates = list(dict.fromkeys(combined_list)) # Preserves order and removes duplicates

    newly_added_count = len(unique_candidates) - len(existing_candidates)
    if newly_added_count > 0:
        print(f"Added {newly_added_count} new unique candidates.")
    else:
        print("No new unique candidates were found to add to the list.")

    # --- 4. Save the Updated List ---
    os.makedirs(output_dir, exist_ok=True)
    try:
        with open(output_path, "w") as f:
            json.dump(unique_candidates, f, indent=4)
        print(f"Successfully saved a total of {len(unique_candidates)} candidates to: {output_path}")
        print("Final Candidates:", unique_candidates)
    except IOError as e:
        print(f"Error saving updated candidate sequences to file: {e}")

if __name__ == "__main__":
    main()
