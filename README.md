The Automated Conjecture Factory is a sophisticated bot designed to explore the vast landscape of the Online Encyclopedia of Integer Sequences (OEIS). It systematically identifies promising integer sequences, applies a suite of computational methods to discover their underlying mathematical formulas, and automatically reports its findings by generating new pull requests.
✨ How It Works
The project operates in a continuous, automated loop, managed by a GitHub Actions workflow. The process can be broken down into three main stages:
 * 🎯 Target Acquisition:
   * A script (src/run_target_finder.py) queries the OEIS database for sequences that are tagged as interesting candidates (e.g., keyword:new, -keyword:easy).
   * It filters these results to ensure they have a sufficient number of terms for robust analysis, as defined in config/settings.yaml.
   * Promising sequence IDs (e.g., A000045) are collected and saved to data/candidate_sequences.json, updating the list of targets.
 * 🧠 Conjecture Generation & Verification:
   * The main analysis script (src/main_analyzer.py) iterates through the list of candidate sequences.
   * For each sequence, the Conjecture Engine (src/core/conjecture_engine.py) attempts to find a generating formula by testing various models:
     * Polynomial Functions: a(n) = c_d n^d + \dots + c_1 n + c_0
     * Linear Recurrence Relations: a(n) = c_1 a(n-1) + c_2 a(n-2) + \dots
     * Exponential Formulas: a(n) = A \cdot B^n + C
   * If a potential formula is found, it is rigorously verified against the known terms of the sequence to ensure its accuracy.
 * 🤖 Automated Reporting:
   * When a conjecture is successfully verified, the Reporting module (src/core/reporting.py) springs into action.
   * It autonomously creates a new Git branch, drafts a detailed Markdown report containing the sequence ID, the discovered formula (in LaTeX), and verification details.
   * Finally, it commits the report to the data/reports/ directory and opens a new Pull Request to merge the finding into the main branch, awaiting human review.
🚀 Features
 * Hourly Automation: Runs every hour via GitHub Actions to continuously search for new conjectures.
 * Intelligent Sourcing: Filters the OEIS to find non-trivial sequences that are ripe for analysis.
 * Multi-Model Analysis: Capable of discovering polynomial, linear recurrence, and exponential relationships.
 * Automated PR Generation: Seamlessly integrates with the GitHub API to report findings in a version-controlled manner.
 * Configurable: Easily tweak analysis parameters like polynomial degree, recurrence depth, and sequence length via config/settings.yaml.
 * Robust & Scalable: Built with a modular structure, making it easy to add new conjecture-testing modules.
📂 Project Structure
.
├── .github/workflows/         # GitHub Actions workflow for automation
├── config/
│   └── settings.yaml          # All configurable parameters for the project
├── data/
│   ├── candidate_sequences.json # List of OEIS sequences to analyze
│   └── reports/               # Directory for generated conjecture reports (as .md files)
├── src/
│   ├── core/
│   │   ├── conjecture_engine.py # Core logic for testing formulas
│   │   ├── reporting.py         # Handles creating reports and PRs
│   │   └── target_finder.py     # Finds new sequences from OEIS
│   ├── main_analyzer.py       # Main script to run the analysis engine
│   └── run_target_finder.py   # Script to update the candidate list
├── requirements.txt           # Project dependencies
└── README.md                  # You are here!

🛠️ Getting Started
To run the Automated Conjecture Factory locally, follow these steps.
Prerequisites
 * Python 3.10 or higher
 * A GitHub account
Installation & Setup
 * Clone the repository:
   git clone https://github.com/hadcomfort/automated-conjecture-factory.git
cd automated-conjecture-factory

 * Create a virtual environment:
   python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

 * Install dependencies:
   pip install -r requirements.txt

 * Configure GitHub Authentication:
   The reporting script requires a GitHub token to create pull requests.
   * Generate a Personal Access Token (PAT) with repo scope.
   * Set it as an environment variable:
     export GITHUB_TOKEN="your_personal_access_token_here"

   * Set the repository owner and name:
     export GITHUB_REPOSITORY="your_github_username/automated-conjecture-factory"

   > Note: The GitHub Actions workflow is already configured to use a repository secret GH_TOKEN. You only need to set these environment variables for local runs.
   > 
⚙️ Usage
You can run the two main components of the factory separately.
 * Find new candidate sequences:
   This script will update data/candidate_sequences.json with new finds from OEIS.
   python src/run_target_finder.py

 * Run the analyzer on existing candidates:
   This script will process all sequences in the JSON file and create PRs for any verified conjectures.
   python src/main_analyzer.py

🔧 Configuration
All major parameters can be adjusted in config/settings.yaml:
# OEIS settings
oeis_base_url: "https://oeis.org/"

# Analysis parameters
min_sequence_length: 30
max_poly_degree_to_test: 15
max_recurrence_depth_to_test: 15
verification_ratio: 0.8 # Use 80% of terms to fit, 20% to verify

# Logging
log_file: "project_log.log"

🤝 Contributing
Contributions are welcome! A great way to contribute is by expanding the capabilities of the conjecture_engine.py. You could add new modules to test for other types of mathematical relationships, such as:
 * Formulas involving factorials or binomial coefficients.
 * Connections to other known sequences.
 * More complex exponential or power-based forms.
Feel free to fork the repository, make your changes, and submit a pull request.
📜 License
This project is licensed under the MIT License - see the LICENSE file for details.
