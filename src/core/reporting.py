# src/core/reporting.py

import os
import json
import base64
import requests
import logging
from typing import Dict, Any, List

# --- Configuration ---
# It's useful to have these as environment variables for automation
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
# The format should be "owner/repository_name", e.g., "my-username/automated-conjecture-factory"
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY") 
API_BASE_URL = "https://api.github.com"

def _get_headers() -> Dict[str, str]:
    """Constructs the authorization headers for GitHub API requests."""
    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN environment variable is not set.")
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }

def create_pr_for_finding(oeis_id: str, result: Dict[str, Any], sequence_data: List[int]):
    """
    Creates a file with the conjecture and opens a pull request on GitHub.

    Args:
        oeis_id (str): The OEIS identifier (e.g., 'A000045').
        result (Dict[str, Any]): The dictionary containing the verified conjecture details.
        sequence_data (List[int]): The full list of sequence terms.
    """
    if not GITHUB_REPOSITORY:
        logging.error("GITHUB_REPOSITORY environment variable is not set. Cannot create PR.")
        print("ERROR: GITHUB_REPOSITORY not set. See logs for details.")
        return

    try:
        owner, repo = GITHUB_REPOSITORY.split('/')
    except ValueError:
        logging.error(f"Invalid GITHUB_REPOSITORY format: {GITHUB_REPOSITORY}. Expected 'owner/repo'.")
        return

    headers = _get_headers()
    
    # --- 1. Define paths and content ---
    new_branch_name = f"feature/conjecture-{oeis_id}"
    report_filename = f"{oeis_id}.md"
    report_path = f"data/reports/{report_filename}"
    commit_message = f"feat: Add conjecture report for {oeis_id}"
    pr_title = f"Conjecture Found: {result['type'].capitalize()} formula for {oeis_id}"

    # --- 2. Create the Markdown content for the report ---
    markdown_content = f"""# New Conjecture Found for OEIS Sequence: {oeis_id}

A new potential formula has been discovered for sequence [{oeis_id}](https://oeis.org/{oeis_id}).

## Conjecture Details

- **Type:** {result['type']}
- **Formula (LaTeX):** `${result['formula_latex']}$`

## Verification

This formula has been computationally verified against all {len(sequence_data)} available terms of the sequence.

---
*This report was generated automatically by the Automated Conjecture Factory.*
"""

    # --- 3. Get the SHA of the main branch ---
    main_branch_url = f"{API_BASE_URL}/repos/{owner}/{repo}/git/ref/heads/main"
    try:
        response = requests.get(main_branch_url, headers=headers)
        response.raise_for_status()
        main_sha = response.json()["object"]["sha"]
    except requests.RequestException as e:
        logging.error(f"Failed to get main branch SHA: {e}")
        return

    # --- 4. Create a new branch ---
    new_branch_url = f"{API_BASE_URL}/repos/{owner}/{repo}/git/refs"
    branch_payload = {"ref": f"refs/heads/{new_branch_name}", "sha": main_sha}
    try:
        requests.post(new_branch_url, headers=headers, json=branch_payload).raise_for_status()
        logging.info(f"Successfully created branch: {new_branch_name}")
    except requests.RequestException as e:
        # It might fail if the branch already exists, which is okay for idempotency
        logging.warning(f"Could not create new branch (it might already exist): {e}")

    # --- 5. Create the new file on the new branch ---
    file_url = f"{API_BASE_URL}/repos/{owner}/{repo}/contents/{report_path}"
    # Content must be base64 encoded for the API
    encoded_content = base64.b64encode(markdown_content.encode('utf-8')).decode('utf-8')
    file_payload = {
        "message": commit_message,
        "content": encoded_content,
        "branch": new_branch_name
    }
    try:
        requests.put(file_url, headers=headers, json=file_payload).raise_for_status()
        logging.info(f"Successfully created file: {report_path} on branch {new_branch_name}")
    except requests.RequestException as e:
        logging.error(f"Failed to create file on GitHub: {e}")
        return

    # --- 6. Create the pull request ---
    pr_url = f"{API_BASE_URL}/repos/{owner}/{repo}/pulls"
    pr_payload = {
        "title": pr_title,
        "head": new_branch_name,
        "base": "main",
        "body": markdown_content,
        "maintainer_can_modify": True
    }
    try:
        response = requests.post(pr_url, headers=headers, json=pr_payload)
        response.raise_for_status()
        pr_html_url = response.json().get('html_url')
        logging.info(f"Successfully created Pull Request: {pr_html_url}")
        print(f"SUCCESS: Created Pull Request for {oeis_id} at {pr_html_url}")
    except requests.RequestException as e:
        logging.error(f"Failed to create pull request: {e.json()}")
