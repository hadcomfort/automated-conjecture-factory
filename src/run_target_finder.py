# src/run_target_finder.py

import json
import os
from core.target_finder import find_candidate_sequences

def main():
    """
    Main execution function to find and save candidate OEIS sequences.
    """
    print("Starting the process to find candidate OEIS sequences...")

    # --- Define Search Parameters ---
    # You can customize the search query here if needed.
    # This query looks for sequences with the keyword "look" but excludes those
    # marked as "nice" or "easy", which often have known simple formulas.
    search_query = "keyword:look -keyword:nice -keyword:easy"
    
    # --- Run the Finder ---
    # This will fetch the first 10 results that match the criteria.
    # You can increase the `count` to find more candidates.
    candidates = find_candidate_sequences(search_query=search_query, count=10)

    if not candidates:
        print("No suitable candidate sequences were found with the current criteria.")
        return

    # --- Save the Results ---
    output_dir = "data"
    output_path = os.path.join(output_dir, "candidate_sequences.json")

    # Ensure the data directory exists
    os.makedirs(output_dir, exist_ok=True)

    try:
        with open(output_path, "w") as f:
            json.dump(candidates, f, indent=4)
        print(f"Successfully found {len(candidates)} candidates.")
        print(f"Results saved to: {output_path}")
        print("Candidates:", candidates)
    except IOError as e:
        print(f"Error saving candidate sequences to file: {e}")

if __name__ == "__main__":
    # This allows the script to be run directly from the command line
    main()
