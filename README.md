<div align="center">
<img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Science/Telescope.png" alt="Telescope Logo" width="120" height="120" />
<h1 style="border-bottom: none;">Automated Conjecture Factory</h1>
<p>
A modest inquiry into the vast ocean of integer sequences. This small automaton is designed to assist in the search for patterns and underlying structures within the On-Line Encyclopedia of Integer Sequences (OEIS), in the hope of uncovering a few new grains of mathematical truth.
</p>
<p>
<a href="https://github.com/hadcomfort/automated-conjecture-factory/actions/workflows/daily_conjecture_run.yml">
<img src="https://github.com/hadcomfort/automated-conjecture-factory/actions/workflows/daily_conjecture_run.yml/badge.svg" alt="Build Status">
</a>
<a href="https://opensource.org/licenses/MIT">
<img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
</a>
<a href="https://www.python.org/downloads/release/python-3100/">
<img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python 3.10+">
</a>
</p>
</div>
📖 Table of Contents
 * A Note on its Purpose and Origins
   * Our Approach
   * The Instruments of Our Craft
 * Our Method of Inquiry
 * Joining the Exploration
   * Prerequisites
   * Installation
 * Usage
 * Configuration
 * The Path Forward
 * An Invitation to Collaborate
 * License
 * On the Shoulders of Giants
🔭 A Note on its Purpose and Origins
The process of mathematical discovery has long been a deeply human endeavor—a blend of intuition, patience, and the painstaking search for patterns. Yet, the universe of numbers is a vast and mysterious landscape, far too expansive for any single mind to explore completely.
This project was born from a simple question: could we build a tool, a sort of tireless assistant, to help with the more laborious aspects of this exploration? Its purpose is not to replace human insight, but to augment it. By systematically sifting through the countless sequences cataloged in the monumental On-Line Encyclopedia of Integer Sequences (OEIS), it seeks to identify simple, underlying structures that may have been overlooked. It is a humble attempt to automate the preliminary search for form, freeing the human mathematician to ponder the deeper significance of the patterns revealed.
Our Approach
 * A Methodical Search: A GitHub Action provides a steady, rhythmic pulse, allowing the system to periodically scan for new and interesting sequences.
 * Focused Inquiry: Rather than wander aimlessly, the tool seeks out sequences that appear promising for analysis—those that are new, yet not marked as trivial.
 * A Toolkit of Simple Forms: We begin with the simplest of tools, checking if a sequence can be described by common mathematical structures:
   * Polynomials: a(n) = c\_k n^k + \\dots + c\_0
   * Linear Recurrences: a(n) = \\sum\_{i=1}^{k} c\_i a(n-i)
   * Simple Exponentials: a(n) = A \\cdot B^n + C
 * Sharing Tentative Findings: When a hypothesis appears to hold, the system automatically prepares a report and presents it to the community via a Pull Request, inviting scrutiny and discussion.
 * Adjustable Instruments: The parameters of the search (e.g., the complexity of polynomials or recurrences) can be easily tuned, for we recognize that our initial assumptions may not always be correct.
🛠️ The Instruments of Our Craft
This project is constructed from a collection of fine, open-source tools:
 * Core Logic: Python 3.10
 * Numerical & Symbolic Math: NumPy, SciPy, SymPy
 * Automation: GitHub Actions
 * API Interaction: Requests
 * Configuration: PyYAML
⚙️ Our Method of Inquiry
The process is a simple, cyclical one, inspired by the scientific method itself.
 * 🎯 Identifying Points of Interest
   The run_target_finder.py script gazes into the OEIS, looking for sequences that fit our criteria for inquiry. It ensures a sequence has sufficient length for meaningful analysis before adding it to our list of candidates.
 * 🧠 Formulating and Testing Hypotheses
   The main_analyzer.py script then examines each candidate. Its "Conjecture Engine" applies various models from our toolkit to the initial terms of a sequence. If a model can then predict the remaining terms with sufficient accuracy, we consider the hypothesis worthy of note.
 * 🤖 Communicating Tentative Findings
   Once a hypothesis is verified by the machine, the Reporting module carefully drafts a summary of its finding, creates a new Git branch for this idea, and opens a Pull Request. This act is not a declaration of truth, but an invitation for human review, collaboration, and ultimate confirmation.
<details>
<summary><b>📂 A Glimpse at the Machinery</b></summary>
.
├── .github/workflows/         # GitHub Actions workflow for automation
├── config/
│   └── settings.yaml          # All configurable parameters for the project
├── data/
│   ├── candidate_sequences.json # List of OEIS sequences to analyze
│   └── reports/               # Directory for generated conjecture reports
├── src/
│   ├── core/
│   │   ├── conjecture_engine.py # Core logic for testing formulas
│   │   ├── reporting.py         # Handles creating reports and PRs
│   │   └── target_finder.py     # Finds new sequences from OEIS
│   ├── main_analyzer.py       # Main script to run the analysis engine
│   └── run_target_finder.py   # Script to update the candidate list
├── requirements.txt           # Project dependencies
└── README.md                  # You are here!

</details>
🚀 Joining the Exploration
We humbly invite others to join in this exploration. To set up your own instance of this small factory, please follow the steps below.
Prerequisites
 * Python 3.10 or newer
 * A GitHub Account
Installation
 * Clone the repository:
   git clone https://github.com/hadcomfort/automated-conjecture-factory.git
cd automated-conjecture-factory

 * Set up a virtual environment (recommended):
   # Create the virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

 * Install dependencies:
   pip install -r requirements.txt

 * Configure Environment Variables (for local reporting):
   To allow the reporting script to create pull requests from your local machine, you must set two environment variables.
   * Generate a GitHub Personal Access Token with repo scope.
   * Set the variables in your shell:
     # On macOS/Linux:
export GITHUB_TOKEN="your_personal_access_token_here"
export GITHUB_REPOSITORY="your_username/automated-conjecture-factory"

# On Windows (Command Prompt):
set GITHUB_TOKEN="your_personal_access_token_here"
set GITHUB_REPOSITORY="your_username/automated-conjecture-factory"

▶️ Usage
One may operate the two primary functions of the system as follows from the root directory.
 * To find new candidate sequences from the OEIS:
   python src/run_target_finder.py

 * To analyze the current list of candidates and generate reports:
   python src/main_analyzer.py

🔧 Configuration
The parameters that guide our search are not set in stone. They can be adjusted in config/settings.yaml to refine the focus of our inquiry.
| Parameter | Type | Description |
|---|---|---|
| min_sequence_length | int | The minimum number of terms a sequence must have to be analyzed. |
| max_poly_degree_to_test | int | The maximum polynomial degree to test for. |
| max_recurrence_depth_to_test | int | The maximum depth (k) for linear recurrences. |
| verification_ratio | float | Fraction of sequence terms used to fit the model (e.g., 0.8 = 80%). |
| log_file | str | The name of the file for logging output. |
🗺️ The Path Forward
A single lifetime is not enough to ask all the questions, let alone find all the answers. Our current methods are but a starting point, and there are many paths we have yet to walk. We are currently pondering several directions for future inquiry:
 * [ ] Broadening Our Theoretical Lens: Our current toolkit is limited. We hope to teach our assistant to recognize more complex patterns, such as those involving factorials (n\!), binomial coefficients (\\binom{n}{k}), hypergeometric series, or fundamental constants like \\pi, e, and \\phi.
 * [ ] A Deeper Dialogue with the OEIS: The system could learn to read existing formulas in the OEIS, preventing it from rediscovering what is already known. It might also learn to see connections between sequences, suggesting new avenues for thought.
 * [ ] Strengthening Our Confidence: Numerical verification is a good first step, but true confidence comes from symbolic proof. We hope to one day incorporate symbolic methods to confirm conjectures with absolute certainty.
 * [ ] A Window into the Workshop: A simple interface could allow one to observe the system's work, view recent findings, and perhaps even submit a sequence by hand for immediate analysis.
We welcome discussion on these and other ideas. The open issues page is a fine place to begin.
🤝 An Invitation to Collaborate
The grandest of theories are often built upon the small contributions of many. We believe that collaboration is the true engine of discovery. Any contribution, whether it is a new line of code or a new idea, is received with immense gratitude.
A wonderful place to begin is by expanding the capabilities of the conjecture_engine.py, teaching it to see new kinds of patterns.
 * Fork the Project.
 * Create your Feature Branch (git checkout -b feature/AmazingFormula).
 * Commit your Changes (git commit -m 'Add support for AmazingFormula').
 * Push to the Branch (git push origin feature/AmazingFormula).
 * Open a Pull Request.
Please feel free to propose new features by creating an issue.
📄 License
Distributed under the MIT License. See LICENSE for more information.
🙏 On the Shoulders of Giants
One cannot explore a landscape without a map. This entire endeavor would be inconceivable without the monumental work of Neil J. A. Sloane and the thousands of contributors to the On-Line Encyclopedia of Integer Sequences (OEIS). It is a testament to the collaborative spirit of mathematics and serves as the bedrock upon which this project rests.
We also extend our gratitude to the creators of the Animated Fluent Emojis project for the small telescope that serves as our emblem.
