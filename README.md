<p align="center">
  <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/refs/heads/master/Emojis/Objects/Telescope.png" alt="Telescope Logo" width="120" height="120" />
</p>

<h1 align="center">Automated Conjecture Factory</h1>

<p align="center">
  A modest inquiry into the vast ocean of integer sequences. This small automaton is designed to assist in the search for patterns and underlying structures within the On-Line Encyclopedia of Integer Sequences (OEIS), in the hope of uncovering a few new grains of mathematical truth.
</p>

<p align="center">
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

## 📖 Table of Contents
- [A Note on its Purpose and Origins](#-a-note-on-its-purpose-and-origins)
  - [Our Approach](#our-approach)
  - [The Instruments of Our Craft](#-the-instruments-of-our-craft)
- [Our Method of Inquiry](#%EF%B8%8F-our-method-of-inquiry)
- [Joining the Exploration](#-joining-the-exploration)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#%EF%B8%8F-usage)
- [Configuration](#-configuration)
- [The Path Forward](#%EF%B8%8F-the-path-forward)
- [An Invitation to Collaborate](#-an-invitation-to-collaborate)
- [License](#-license)
- [On the Shoulders of Giants](#-on-the-shoulders-of-giants)

## 🔭 A Note on its Purpose and Origins
The process of mathematical discovery has long been a deeply human endeavor—a blend of intuition, patience, and the painstaking search for patterns. Yet, the universe of numbers is a vast and mysterious landscape, far too expansive for any single mind to explore completely.

This project was born from a simple question: could we build a tool, a sort of tireless assistant, to help with the more laborious aspects of this exploration? Its purpose is not to replace human insight, but to augment it. By systematically sifting through the countless sequences cataloged in the monumental On-Line Encyclopedia of Integer Sequences (OEIS), it seeks to identify simple, underlying structures that may have been overlooked. It is a humble attempt to automate the preliminary search for form, freeing the human mathematician to ponder the deeper significance of the patterns revealed.

### Our Approach
- A Methodical Search: A GitHub Action provides a steady, rhythmic pulse, allowing the system to periodically scan for new and interesting sequences.
- Focused Inquiry: Rather than wander aimlessly, the tool seeks out sequences that appear promising for analysis—those that are new, yet not marked as trivial.
- A Toolkit of Simple Forms: We begin with the simplest of tools, checking if a sequence can be described by common mathematical structures:
  - Polynomials: a(n) = c_k n^k + ... + c_0
  - Linear Recurrences: a(n) = Σ_{i=1}^{k} c_i a(n-i)
  - Simple Exponentials: a(n) = A · B^n + C
- Sharing Tentative Findings: When a hypothesis appears to hold, the system automatically prepares a report and presents it to the community via a Pull Request, inviting scrutiny and discussion.
- Adjustable Instruments: The parameters of the search (e.g., the complexity of polynomials or recurrences) can be easily tuned.

## 🛠️ The Instruments of Our Craft
This project is constructed from a collection of fine, open-source tools:
- Core Logic: Python 3.10+
- Numerical & Symbolic Math: NumPy, SciPy, SymPy
- Automation: GitHub Actions
- API Interaction: Requests
- Configuration: PyYAML

## ⚙️ Our Method of Inquiry
The process is a simple, cyclical one, inspired by the scientific method itself.

- 🎯 Identifying Points of Interest
  The run_target_finder.py script looks into the OEIS, finding sequences that fit our criteria for inquiry. It ensures a sequence has sufficient length for meaningful analysis before adding it to our list of candidates.

- 🧠 Formulating and Testing Hypotheses
  The main_analyzer.py script then examines each candidate. Its “Conjecture Engine” applies various models from our toolkit to the initial terms of a sequence. If a model can predict the remaining terms with sufficient accuracy, we consider the hypothesis worthy of note.

- 🤖 Communicating Tentative Findings
  Once a hypothesis is verified by the machine, the Reporting module drafts a summary of its finding, creates a new Git branch for this idea, and opens a Pull Request. This is an invitation for human review and collaboration.

<details>
<summary><b>📂 A Glimpse at the Machinery</b></summary>

```
.
├── .github/workflows/           # GitHub Actions workflow for automation
├── config/
│   └── settings.yaml            # All configurable parameters for the project
├── data/
│   ├── candidate_sequences.json # List of OEIS sequences to analyze
│   └── reports/                 # Directory for generated conjecture reports
├── src/
│   ├── core/
│   │   ├── conjecture_engine.py # Core logic for testing formulas
│   │   ├── reporting.py         # Handles creating reports and PRs
│   │   └── target_finder.py     # Finds new sequences from OEIS
│   ├── main_analyzer.py         # Main script to run the analysis engine
│   └── run_target_finder.py     # Script to update the candidate list
├── requirements.txt             # Project dependencies
└── README.md                    # You are here!
```

</details>

## 🚀 Joining the Exploration
We humbly invite others to join in this exploration. To set up your own instance of this small factory, please follow the steps below.

### Prerequisites
- Python 3.10 or newer
- A GitHub account

### Installation
- Clone the repository:
```bash
git clone https://github.com/hadcomfort/automated-conjecture-factory.git
cd automated-conjecture-factory
```

- Set up a virtual environment (recommended):
```bash
# Create the virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows (Command Prompt):
venv\Scripts\activate
```

- Install dependencies:
```bash
pip install -r requirements.txt
```

- Configure environment variables (for local reporting):
  To allow the reporting script to create pull requests from your local machine, set:
  - A GitHub Personal Access Token with repo scope.
  - Environment variables in your shell:

macOS/Linux:
```bash
export GITHUB_TOKEN="your_personal_access_token_here"
export GITHUB_REPOSITORY="your_username/automated-conjecture-factory"
```

Windows (Command Prompt):
```cmd
set GITHUB_TOKEN=your_personal_access_token_here
set GITHUB_REPOSITORY=your_username/automated-conjecture-factory
```

## ▶️ Usage
Run from the repository root.

- Find new candidate sequences from the OEIS:
```bash
python src/run_target_finder.py
```

- Analyze current candidates and generate reports:
```bash
python src/main_analyzer.py
```

## 🔧 Configuration
Adjust parameters in config/settings.yaml.

| Parameter                   | Type  | Description                                                        |
| -------------------------- | ----- | ------------------------------------------------------------------ |
| min_sequence_length        | int   | Minimum number of terms a sequence must have to be analyzed.       |
| max_poly_degree_to_test    | int   | Maximum polynomial degree to test.                                 |
| max_recurrence_depth_to_test | int | Maximum depth (k) for linear recurrences.                          |
| verification_ratio         | float | Fraction of terms used to fit the model (e.g., 0.8 = 80%).         |
| log_file                   | str   | File name for logging output.                                      |

## 🗺️ The Path Forward
A single lifetime is not enough to ask all the questions, let alone find all the answers. Our current methods are a starting point, and there are many paths we have yet to walk. We are pondering several directions:

- [ ] Broadening Our Theoretical Lens: Recognize patterns involving factorials (n!), binomial coefficients (binomial(n, k)), hypergeometric series, or constants like π, e, and φ.
- [ ] A Deeper Dialogue with the OEIS: Read existing formulas to avoid rediscovery and detect connections between sequences.
- [ ] Strengthening Our Confidence: Move from numerical verification toward symbolic proof.
- [ ] A Window into the Workshop: Provide a simple interface to observe work, view findings, and submit sequences for analysis.

We welcome discussion—see the open issues page.

## 🤝 An Invitation to Collaborate
The grandest of theories are often built upon the small contributions of many. We believe that collaboration is the true engine of discovery. Any contribution, whether it is a new line of code or a new idea, is received with immense gratitude.

A wonderful place to begin is by expanding the capabilities of conjecture_engine.py.

- Fork the project.
- Create your feature branch: git checkout -b feature/AmazingFormula
- Commit your changes: git commit -m "Add support for AmazingFormula"
- Push to the branch: git push origin feature/AmazingFormula
- Open a Pull Request.

Please feel free to propose new features by creating an issue.

## 📄 License
Distributed under the MIT License. See LICENSE for more information.

## 🙏 On the Shoulders of Giants
One cannot explore a landscape without a map. This endeavor would be inconceivable without the monumental work of Neil J. A. Sloane and the thousands of contributors to the On-Line Encyclopedia of Integer Sequences (OEIS). It is a testament to the collaborative spirit of mathematics and serves as the bedrock upon which this project rests.

We also extend our gratitude to the creators of the Animated Fluent Emojis project for the small telescope that serves as our emblem.