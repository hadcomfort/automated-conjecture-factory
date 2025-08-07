# src/core/conjecture_engine.py

import numpy as np
import sympy
import yaml
import logging
from scipy.linalg import solve, LinAlgError
from typing import List, Dict, Any

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
            'max_poly_degree_to_test': 10,
            'max_recurrence_depth_to_test': 10,
            'verification_ratio': 0.8
        }

CONFIG = load_config()

# --- Logging Setup ---
# Assumes logging is configured by the main script, but sets a basic config if run standalone.
if not logging.getLogger().hasHandlers():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=CONFIG.get('log_file', 'project.log')
    )

# --- Conjecture Functions ---

def test_polynomial_conjecture(sequence_data: List[int]) -> Dict[str, Any]:
    """
    Tests if a sequence can be described by a simple polynomial formula.

    Args:
        sequence_data (List[int]): The integer sequence to analyze.

    Returns:
        Dict[str, Any]: A dictionary containing the status and details of the conjecture.
    """
    n = sympy.symbols('n')
    max_degree = CONFIG.get('max_poly_degree_to_test', 10)
    verification_ratio = CONFIG.get('verification_ratio', 0.8)
    
    # Determine the number of terms to use for fitting the polynomial
    fit_len = int(len(sequence_data) * verification_ratio)
    if fit_len < 2:
        logging.warning("Sequence too short for polynomial fitting.")
        return {"status": "failed"}

    x_fit = np.arange(1, fit_len + 1) # OEIS sequences are typically 1-indexed
    y_fit = np.array(sequence_data[:fit_len])

    for degree in range(1, max_degree + 1):
        if fit_len <= degree:
            continue # Not enough data points to fit a polynomial of this degree

        try:
            # Fit a polynomial of the current degree
            coeffs = np.polyfit(x_fit, y_fit, degree)
        except np.linalg.LinAlgError:
            logging.warning(f"Could not fit polynomial of degree {degree}.")
            continue

        # Check if coefficients are close to simple integers or rationals
        # A tolerance of 1e-9 is used to account for floating point inaccuracies.
        if not all(abs(c - round(c)) < 1e-9 for c in coeffs):
            continue # Coefficients are not simple integers, so we skip

        # Create a symbolic polynomial with rounded, integer coefficients
        rounded_coeffs = [int(round(c)) for c in coeffs]
        poly_formula = sum(c * n**(degree - i) for i, c in enumerate(rounded_coeffs))
        
        # Verify the formula against the *entire* sequence
        is_verified = True
        for i, true_val in enumerate(sequence_data, 1):
            predicted_val = poly_formula.subs(n, i)
            if predicted_val != true_val:
                is_verified = False
                break
        
        if is_verified:
            logging.info(f"Verified polynomial conjecture of degree {degree}.")
            return {
                "status": "verified",
                "type": "polynomial",
                "formula_latex": str(sympy.latex(poly_formula)),
                "details": f"Polynomial of degree {degree}"
            }
            
    return {"status": "failed"}


def test_linear_recurrence_conjecture(sequence_data: List[int]) -> Dict[str, Any]:
    """
    Tests if a sequence satisfies a linear recurrence relation with integer coefficients.

    Args:
        sequence_data (List[int]): The integer sequence to analyze.

    Returns:
        Dict[str, Any]: A dictionary containing the status and details of the conjecture.
    """
    max_depth = CONFIG.get('max_recurrence_depth_to_test', 10)
    
    for k in range(1, max_depth + 1):
        # We need at least 2*k terms to solve for k coefficients
        if len(sequence_data) < 2 * k:
            continue

        # Construct the system of linear equations Ax = b
        # where x is the vector of coefficients [c_1, c_2, ..., c_k]
        # a(n) = c_1*a(n-1) + ... + c_k*a(n-k)
        
        # Matrix A: each row is [a(n-1), a(n-2), ..., a(n-k)]
        A = []
        # Vector b: each entry is a(n)
        b = []
        
        for i in range(k, 2 * k):
            A.append(list(reversed(sequence_data[i-k:i])))
            b.append(sequence_data[i])
            
        try:
            # Solve for the coefficients
            coeffs = solve(np.array(A), np.array(b))
        except LinAlgError:
            # This can happen if the matrix is singular (linearly dependent rows)
            continue

        # --- FIX ---
        # Before checking for integer-ness, ensure all coefficients are finite numbers.
        # This handles cases where the solver returns 'inf' or 'nan'.
        if not np.all(np.isfinite(coeffs)):
            continue
        # --- END FIX ---

        # Check if coefficients are close to integers
        if not all(abs(c - round(c)) < 1e-9 for c in coeffs):
            continue

        rounded_coeffs = [int(round(c)) for c in coeffs]

        # Verify the recurrence for the rest of the sequence
        is_verified = True
        for i in range(k, len(sequence_data)):
            predicted_val = sum(c * sequence_data[i-j-1] for j, c in enumerate(rounded_coeffs))
            if int(round(predicted_val)) != sequence_data[i]:
                is_verified = False
                break
        
        if is_verified:
            logging.info(f"Verified linear recurrence of depth {k}.")
            # Create a LaTeX representation of the formula
            n = sympy.symbols('n')
            a = sympy.Function('a')
            terms = " + ".join(f"{c} \\cdot a(n-{j+1})" for j, c in enumerate(rounded_coeffs) if c != 0)
            formula_latex = f"a(n) = {terms}".replace('+ -', '- ')
            
            return {
                "status": "verified",
                "type": "linear_recurrence",
                "formula_latex": formula_latex,
                "details": f"Linear recurrence of depth {k}"
            }

    return {"status": "failed"}
