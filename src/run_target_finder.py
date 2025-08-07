# src/run_target_finder.py

import json
import os
from core.target_finder import find_candidate_sequences

def main():
    """
    Main execution function to find and save candidate OEIS sequences.
    """
    print("Starting the process to find candidate OEIS sequences with a broader search...")

    # --- Define Search Parameters ---
    # NEW, BROADER QUERY:
    # This query looks for sequences marked as "new" and excludes those
    # marked as "easy". This should provide a different set of candidates
    # that are less likely to have simple, known formulas.
    search_query = "keyword:new -keyword:easy"
    
    # --- Run the Finder ---
    # We'll fetch 20 candidates this time to increase our chances.
    candidates = find_candidate_sequences(search_query=search_query, count=20)

    if not candidates:
        print("No suitable candidate sequences were found with the new criteria.")
        return

    # --- Save the Results ---
    output_dir = "data"
    output_path = os.path.join(output_dir, "candidate_sequences.json")

    # Ensure the data directory exists
    os.makedirs(output_dir, exist_ok=True)

    try:
        with open(output_path, "w") as f:
            json.dump(candidates, f, indent=4)
        print(f"Successfully found {len(candidates)} new candidates.")
        print(f"Results saved to: {output_path}")
        print("New Candidates:", candidates)
    except IOError as e:
        print(f"Error saving candidate sequences to file: {e}")

if __name__ == "__main__":
    # This allows the script to be run directly from the command line
    main()
