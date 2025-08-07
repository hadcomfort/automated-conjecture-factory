import requests
import json
import yaml
import time
import logging
from typing import List, Dict, Optional

# --- Configuration Loading ---
def load_config() -> Dict:
    """Loads the project configuration from the YAML file."""
    try:
        with open("config/settings.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logging.error("Configuration file 'config/settings.yaml' not found.")
        # Return a default config to prevent crashing
        return {
            'oeis_base_url': "https://oeis.org/",
            'min_sequence_length': 30,
        }

CONFIG = load_config()

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=CONFIG.get('log_file', 'project.log')
)

# --- Core Functions ---

def fetch_b_file_data(oeis_id: str) -> Optional[List[int]]:
    """
    Fetches the raw numerical data for a given OEIS sequence from its b-file.

    Args:
        oeis_id (str): The OEIS identifier (e.g., 'A000045').

    Returns:
        Optional[List[int]]: A list of integers in the sequence, or None if fetching fails.
    """
    # The b-file name is the OEIS ID with 'A' replaced by 'b'
    b_file_id = oeis_id.replace('A', 'b')
    url = f"{CONFIG['oeis_base_url']}{oeis_id}/{b_file_id}.txt"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        
        sequence_data = []
        lines = response.text.strip().split('\n')
        for line in lines:
            # Skip comments or empty lines
            if line.startswith('#') or not line.strip():
                continue
            
            # B-file format is typically "index value"
            parts = line.split()
            if len(parts) >= 2:
                try:
                    # The value is the second part
                    value = int(parts[1])
                    sequence_data.append(value)
                except (ValueError, IndexError):
                    logging.warning(f"Could not parse line in {oeis_id} b-file: {line}")
                    continue
                    
        return sequence_data
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch b-file for {oeis_id}. Error: {e}")
        return None

def find_candidate_sequences(search_query: str = "keyword:look -keyword:nice -keyword:easy", start_index: int = 0, count: int = 10) -> List[str]:
    """
    Finds promising OEIS sequences that are non-trivial and have sufficient data.

    Args:
        search_query (str): The search query for the OEIS database.
        start_index (int): The starting index for search results (for pagination).
        count (int): The number of results to fetch per API call.

    Returns:
        List[str]: A list of qualifying OEIS IDs.
    """
    search_url = f"{CONFIG['oeis_base_url']}search"
    params = {
        'q': search_query,
        'fmt': 'json',
        'start': start_index
    }
    
    logging.info(f"Searching OEIS with query: '{search_query}' starting at index {start_index}")
    
    try:
        response = requests.get(search_url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to search OEIS. Error: {e}")
        return []
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON response from OEIS search.")
        return []

    if 'results' not in data or data['results'] is None:
        logging.warning("No 'results' found in OEIS API response.")
        return []

    candidate_ids = []
    min_len = CONFIG.get('min_sequence_length', 30)

    for result in data['results']:
        oeis_id = result.get('number')
        if not oeis_id:
            continue
        
        # Format the ID correctly (e.g., 45 -> A000045)
        oeis_id_str = f"A{oeis_id:06d}"

        logging.info(f"Checking candidate: {oeis_id_str}")
        
        # Fetch the b-file to check the sequence length
        sequence_data = fetch_b_file_data(oeis_id_str)
        
        # Add a small delay to be respectful to the OEIS servers
        time.sleep(0.5) 
        
        if sequence_data and len(sequence_data) >= min_len:
            logging.info(f"  -> QUALIFIED: {oeis_id_str} has {len(sequence_data)} terms.")
            candidate_ids.append(oeis_id_str)
        elif sequence_data:
            logging.info(f"  -> SKIPPED: {oeis_id_str} has only {len(sequence_data)} terms (min: {min_len}).")
        else:
            logging.info(f"  -> SKIPPED: Could not fetch data for {oeis_id_str}.")
            
    return candidate_ids
