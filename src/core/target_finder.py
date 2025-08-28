# src/core/target_finder.py

import requests
import json
import re
import logging
from typing import List, Optional, Dict

# Use the official JSON search endpoint for finding candidates
OEIS_SEARCH_URL = "https://oeis.org/search"
OEIS_BFILE_URL_TEMPLATE = "https://oeis.org/{oeis_id}/b{oeis_id_num}.txt"

def find_candidate_sequences(search_query: str, count: int) -> List[str]:
    """
    Searches the OEIS database using a given query string via its JSON API.
    
    Args:
        search_query: The string to search for (e.g., "keyword:unkn").
        count: The maximum number of results to fetch.
        
    Returns:
        A list of OEIS ID strings (e.g., ["A000045", "A000010"]).
    """
    logging.info(f"Searching OEIS with query='{search_query}' and count={count}...")
    
    # --- FIX: Add a User-Agent header to mimic a browser and avoid being blocked ---
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    params = {
        "q": search_query,
        "fmt": "json",
        "n": count, # 'n' specifies the number of results
        "start": 0
    }
    
    new_ids = []
    try:
        # Add the headers parameter to the request call
        response = requests.get(OEIS_SEARCH_URL, params=params, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()
        
        if "results" in data and data["results"] is not None:
            for result in data["results"]:
                # Format the number as a standard 6-digit zero-padded ID
                oeis_id = f"A{result['number']:06d}"
                new_ids.append(oeis_id)
            logging.info(f"OEIS search returned {len(new_ids)} new candidate IDs.")
        else:
            logging.info("OEIS search returned no results.")
        return new_ids

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to search OEIS: {e}")
        return []
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON response from OEIS search API.")
        return []

def fetch_b_file_data(oeis_id: str) -> Optional[List[int]]:
    """
    Fetches the b-file for a given OEIS ID, containing the sequence terms.
    This function is used by the main analyzer.
    """
    if not re.fullmatch(r"A\d{6,}", oeis_id):
        logging.warning(f"Invalid OEIS ID format passed to fetch_b_file_data: {oeis_id}")
        return None

    oeis_id_num_part = oeis_id[1:]
    url = OEIS_BFILE_URL_TEMPLATE.format(oeis_id=oeis_id, oeis_id_num=oeis_id_num_part)
    
    # Also add headers here to be safe and consistent
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        sequence_data = []
        for line in response.text.splitlines():
            if not line or line.startswith('#'):
                continue
            # A b-file line is typically 'n a(n)'
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    # The second column is the sequence value a(n)
                    a_n = int(parts[1])
                    sequence_data.append(a_n)
                except (ValueError, IndexError):
                    continue
        
        if not sequence_data:
            logging.warning(f"B-file for {oeis_id} was empty or unparseable.")
            return None
        
        return sequence_data

    except requests.exceptions.RequestException as e:
        logging.warning(f"Failed to fetch b-file for {oeis_id}: {e}")
        return None
