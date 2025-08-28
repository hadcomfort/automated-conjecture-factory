# src/core/conjecture_engine.py

import numpy as np
import sympy
import yaml
import logging
from scipy.linalg import solve, LinAlgError
from scipy.optimize import fsolve
from typing import List, Dict, Any

# --- Configuration Loading ---
def load_config() -> Dict:
    """Loads the project configuration from the YAML file."""
    try:
        with open("config/settings.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logging.error("Configuration file 'config/settings.yaml' not found.")
        return {
            'max_poly_degree_to_test': 15,
            'max_recurrence_depth_to_test': 15,
            'verification_ratio': 0.8
        }

CONFIG = load_config()

# --- Logging Setup ---
if not logging.getLogger().hasHandlers():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=CONFIG.get('log_file', 'project.log')
    )

# --- Conjecture Functions ---

def test_polynomial_conjecture(sequence_data: List[int]) -> Dict[str, Any]:
    """Tests if a sequence can be described by a simple polynomial formula."""
    n = sympy.symbols('n')
    max_degree = CONFIG.get('max_poly_degree_to_test', 15)
    verification_ratio = CONFIG.get('verification_ratio', 0.8)
    
    fit_len = int(len(sequence_data) * verification_ratio)
    if fit_len < 2:
        return {"status": "failed"}

    x_fit = np.arange(1, fit_len + 1)
    
    try:
        # Attempt to cast the relevant part of the sequence to a fixed-size integer array.
        # This preemptively catches numbers that are too large for numpy's C-based routines.
        y_fit = np.array(sequence_data[:fit_len], dtype=np.int64)
    except OverflowError:
        logging.warning("Sequence contains numbers too large for polynomial fitting. Skipping.")
        return {"status": "failed"}

    for degree in range(1, max_degree + 1):
        if fit_len <= degree: continue
        try:
            coeffs = np.polyfit(x_fit, y_fit, degree)
        except np.linalg.LinAlgError:
            continue
        if not all(abs(c - round(c)) < 1e-9 for c in coeffs): continue
        rounded_coeffs = [int(round(c)) for c in coeffs]
        poly_formula = sum(c * n**(degree - i) for i, c in enumerate(rounded_coeffs))
        is_verified = all(poly_formula.subs(n, i) == true_val for i, true_val in enumerate(sequence_data, 1))
        if is_verified:
            return {"status": "verified", "type": "polynomial", "formula_latex": str(sympy.latex(poly_formula)), "details": f"Polynomial of degree {degree}"}
            
    return {"status": "failed"}


def test_linear_recurrence_conjecture(sequence_data: List[int]) -> Dict[str, Any]:
    """Tests if a sequence satisfies a linear recurrence relation."""
    # Preemptively check if sequence values are too large for numpy's standard integer types.
    # This is more robust than checking for 'object' dtype later on.
    try:
        _ = np.array(sequence_data, dtype=np.int64)
    except OverflowError:
        logging.warning("Sequence contains numbers too large for recurrence solver. Skipping.")
        return {"status": "failed"}

    max_depth = CONFIG.get('max_recurrence_depth_to_test', 15)
    for k in range(1, max_depth + 1):
        if len(sequence_data) < 2 * k: continue
        
        A_list, b_list = [], []
        for i in range(k, 2 * k):
            A_list.append(list(reversed(sequence_data[i-k:i])))
            b_list.append(sequence_data[i])
        
        A = np.array(A_list)
        b = np.array(b_list)

        try:
            coeffs = solve(A, b)
        except LinAlgError:
            continue
        if not np.all(np.isfinite(coeffs)): continue
        if not all(abs(c - round(c)) < 1e-9 for c in coeffs): continue
        rounded_coeffs = [int(round(c)) for c in coeffs]
        is_verified = all(int(round(sum(c * sequence_data[i-j-1] for j, c in enumerate(rounded_coeffs)))) == sequence_data[i] for i in range(k, len(sequence_data)))
        if is_verified:
            terms = " + ".join(f"{c} \\cdot a(n-{j+1})" for j, c in enumerate(rounded_coeffs) if c != 0)
            formula_latex = f"a(n) = {terms}".replace('+ -', '- ')
            return {"status": "verified", "type": "linear_recurrence", "formula_latex": formula_latex, "details": f"Linear recurrence of depth {k}"}
    return {"status": "failed"}

def test_exponential_conjecture(sequence_data: List[int]) -> Dict[str, Any]:
    """Tests for a formula like a(n) = A * B^n + C."""
    if len(sequence_data) < 5:
        return {"status": "failed"}

    points = sequence_data[:3]
    
    def equations(p):
        A, B, C = p
        return (A * B**1 + C - points[0], A * B**2 + C - points[1], A * B**3 + C - points[2])

    try:
        initial_guess = (1.0, 2.0, 0.0)
        coeffs, _, ier, _ = fsolve(equations, initial_guess, full_output=True)
        if ier != 1: return {"status": "failed"}
    except (ValueError, TypeError):
        return {"status": "failed"}

    if not np.all(np.isfinite(coeffs)) or not all(abs(c - round(c)) < 1e-9 for c in coeffs):
        return {"status": "failed"}

    A, B, C = [int(round(c)) for c in coeffs]
    if B == 1 or A == 0: return {"status": "failed"}

    n = sympy.symbols('n')
    exp_formula = A * (B**n) + C
    
    is_verified = all(exp_formula.subs(n, i) == true_val for i, true_val in enumerate(sequence_data, 1))

    if is_verified:
        logging.info(f"Verified exponential conjecture: a(n) = {A}*({B}**n) + {C}")
        return {"status": "verified", "type": "exponential", "formula_latex": sympy.latex(exp_formula), "details": f"Exponential formula with base {B}"}

    return {"status": "failed"}
