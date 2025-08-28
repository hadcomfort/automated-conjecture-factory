# src/core/rational_conjecture.py

import numpy as np
import sympy
import logging
from typing import List, Dict, Any, Tuple

def test_rational_conjecture(sequence_data: List[int], oeis_id: str, max_deg: int = 4) -> Dict[str, Any]:
    """
    Tests if a sequence can be described by a rational function P(n)/Q(n).
    
    Tries to find polynomial coefficients for P and Q by solving the linear
    system derived from a(n)Q(n) - P(n) = 0.
    """
    n_sym = sympy.symbols('n')
    
    # Pre-check for large numbers
    try:
        _ = np.array(sequence_data, dtype=np.int64)
    except OverflowError:
        logging.warning(f"Sequence {oeis_id} contains numbers too large for rational fitting. Skipping.")
        return {"status": "failed"}

    # We need enough points to solve for the coefficients.
    # For degrees (d_p, d_q), we need d_p + d_q + 2 points.
    # Max required is (max_deg + max_deg + 2).
    if len(sequence_data) < 2 * max_deg + 2:
        max_deg = (len(sequence_data) - 2) // 2
    
    if max_deg < 0:
        return {"status": "failed"}

    n_values = np.arange(1, len(sequence_data) + 1)
    a_n_values = np.array(sequence_data)

    # Iterate through possible degrees for numerator P(n) and denominator Q(n)
    for p_deg in range(max_deg + 1):
        for q_deg in range(1, max_deg + 1): # Denominator must have at least degree 1
            num_coeffs = p_deg + q_deg + 2
            if len(sequence_data) < num_coeffs:
                continue

            # Set up the linear system Ax = 0
            # The columns correspond to coeffs of P then coeffs of Q
            # [n^p_deg, ..., n, 1, -a(n)*n^q_deg, ..., -a(n)*n]
            # We solve for Ax=b where one Q coeff is fixed to 1.
            
            M = []
            b = []
            
            fit_points = min(len(sequence_data), num_coeffs + 2) # Use extra points for a better fit

            for i in range(fit_points):
                n = n_values[i]
                an = a_n_values[i]

                p_row = [n**k for k in reversed(range(p_deg + 1))]
                q_row = [-an * n**k for k in reversed(range(q_deg))] # Fixed q_0 = 1
                
                M.append(p_row + q_row)
                b.append(an) # Corresponds to the fixed q_0 coefficient
            
            try:
                # Use least squares to find the best-fit coefficients
                coeffs, residuals, _, _ = np.linalg.lstsq(M, b, rcond=None)
                if residuals.size > 0 and residuals[0] > 1e-5:
                    continue

            except np.linalg.LinAlgError:
                continue

            if not np.all(np.abs(coeffs - np.round(coeffs)) < 1e-9):
                continue

            rounded_coeffs = np.round(coeffs).astype(int)
            
            p_coeffs = list(rounded_coeffs[:p_deg + 1])
            q_coeffs = list(rounded_coeffs[p_deg + 1:]) + [1] # Add the fixed q_0=1

            P = sum(c * n_sym**k for c, k in zip(p_coeffs, reversed(range(p_deg + 1))))
            Q = sum(c * n_sym**k for c, k in zip(q_coeffs, reversed(range(q_deg + 1))))
            
            if Q == 0: continue

            # Final verification
            is_verified = True
            for i, true_val in enumerate(sequence_data, 1):
                q_val = Q.subs(n_sym, i)
                if q_val == 0: # Division by zero, invalid formula for this n
                    is_verified = False
                    break
                predicted_val = P.subs(n_sym, i) / q_val
                if abs(predicted_val - true_val) > 1e-9:
                    is_verified = False
                    break

            if is_verified:
                formula_latex = sympy.latex(P / Q)
                logging.info(f"Verified rational conjecture for {oeis_id}: a(n) = {P}/{Q}")
                return {
                    "status": "verified",
                    "type": "rational_function",
                    "formula_latex": formula_latex,
                    "details": f"Rational function with P(n) of degree {p_deg} and Q(n) of degree {q_deg}"
                }

    return {"status": "failed"}
