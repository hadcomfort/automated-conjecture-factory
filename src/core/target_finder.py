# src/core/target_finder.py

import requests
import json
import re
import logging
import time
from typing import List, Optional, Dict

OEIS_HOMEPAGE_URL = "https://oeis.org/"
OEIS_SEARCH_URL = "https://oeis.org/search"
OEIS_BFILE_URL_TEMPLATE = "https://oeis.org/{oeis_id}/b{oeis_id_num}.txt"

def _create_oeis_session() -> requests.Session:
    """
    Creates a requests.Session and performs a warm-up request to the OEIS homepage
    to acquire necessary session cookies, mimicking a real browser visit.
    """
    session = requests.Session()
    # A standard User-Agent header to avoid instant blocks
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    })
    try:
        logging.info("Performing warm-up request to OEIS homepage to establish a session...")
        response = session.get(OEIS_HOMEPAGE_URL, timeout=15)
        response.raise_for_status()
        logging.info("Session established successfully.")
    except requests.RequestException as e:
        logging.error(f"Failed to establish OEIS session during warm-up request: {e}")
        # Return the session anyway; maybe the subsequent calls will work.
    return session

# Create a single session to be reused by functions in this module.
# This is more efficient and correctly maintains the session state.
oeis_session = _create_oeis_session()

def find_candidate_sequences(search_query: str, count: int) -> List[str]:
    """
    Searches the OEIS database using a given query string via its JSON API.
    """
    logging.info(f"Searching OEIS with query='{search_query}' and count={count}...")
    params = {
        "q": search_query,
        "fmt": "json",
        "n": count,
        "start": 0
    }
    
    new_ids = []
    try:
        # Use the pre-warmed session object for the request
        response = oeis_session.get(OEIS_SEARCH_URL, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
        
        if "results" in data and data.get("results") is not None:
            for result in data["results"]:
                oeis_id = f"A{result['number']:06d}"
                new_ids.append(oeis_id)
            logging.info(f"OEIS search returned {len(new_ids)} new candidate IDs.")
        else:
            logging.info("OEIS search returned no results or an empty result set.")
        return new_ids

    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP Error searching OEIS: {e}. The server may be blocking our requests.")
        return []
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to search OEIS: {e}")
        return []
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON response from OEIS search API.")
        return []

def fetch_b_file_data(oeis_id: str) -> Optional[List[int]]:
    """
    Fetches the b-file for a given OEIS ID using the shared session.
    """
    if not re.fullmatch(r"A\d{6,}", oeis_id):
        logging.warning(f"Invalid OEIS ID format passed to fetch_b_file_data: {oeis_id}")
        return None

    oeis_id_num_part = oeis_id[1:]
    url = OEIS_BFILE_URL_TEMPLATE.format(oeis_id=oeis_id, oeis_id_num=oeis_id_num_part)
    
    try:
        # Use the same shared session to fetch the b-file
        response = oeis_session.get(url, timeout=15)
        response.raise_for_status()
        
        sequence_data = []
        for line in response.text.splitlines():
            if not line or line.startswith('#'):
                continue
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
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
