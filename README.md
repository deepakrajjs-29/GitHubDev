# GitHubDev -- AI-Powered GitHub Learning Automation System

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Actions](https://img.shields.io/badge/automation-GitHub%20Actions-blueviolet.svg)](https://github.com/features/actions)
[![AI Engine: Gemini](https://img.shields.io/badge/AI-Google%20Gemini-orange.svg)](https://ai.google.dev/)

**GitHubDev** is an unattended, production-grade GitHub automation platform built in Python. It automatically generates and publishes structured daily lessons from a 90-day Python curriculum into the clean target repository **[Codewithpython](https://github.com/deepakrajjs-29/Codewithpython)**.

---

## 🌟 Key Features

- **Unattended Daily Publishing**: Publishes 1 contiguous lesson per day to the target repository.
- **Strict Progress Tracking**: Progress increments **only after** successful commit & push to the target repo. Zero skipped lesson numbers.
- **Multi-Level AI Fallback**: Primary generation uses `gemini-2.5-flash` (3 retries with exponential backoff) with automatic fallback to `gemini-1.5-pro`.
- **Sunday Batch Caching**: Pre-generates the next 7 lessons every Sunday and caches them locally for reliable weekday dispatch.
- **Decoupled Architecture**: Designed to support future courses (*CodewithJava*, *CodewithSQL*, *CodewithCPP*) by changing only `config.yaml`, syllabus JSON, and prompt templates.
- **Dynamic Progress Dashboard**: Automatically updates `Codewithpython/README.md` with progress bars, streak statistics, and lesson navigation links.
- **Fail-Safe Recovery**: Detailed failure logs written to `backup/automation_log.md` with clean graceful exit.

---

## 📂 Architecture Overview

```text
GitHubDev/
├── .github/workflows/       # GitHub Actions (daily, weekly cache, recovery, manual)
├── src/                     # Core Python modules (generator, publisher, managers, formatters)
├── config/                  # Engine configuration (config.yaml)
├── syllabus/                # Course definitions (python_90_days.json)
├── prompts/                 # Gemini prompt templates (python_lesson_prompt.md)
├── cache/                   # Local batch storage for pre-generated lessons
├── state/                   # State tracking (progress.json)
├── logs/                    # Execution logs
├── backup/                  # Automation failure & recovery audit logs
├── docs/                    # Architecture, setup, and developer guides
└── tests/                   # Pytest test suite
```

---

## 🚀 Quick Setup & Local Execution

### 1. Prerequisites
- Python 3.12+
- Google Gemini API Key
- GitHub Personal Access Token (PAT with `repo` scope)

### 2. Installation
```bash
git clone https://github.com/deepakrajjs-29/GitHubDev.git
cd GitHubDev
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env` and fill in your secrets:
```env
GEMINI_API_KEY=your_gemini_api_key
GITHUB_PAT=your_github_pat
```

### 4. Local Execution
```bash
# Run tests
pytest tests/ -v

# Run publisher engine locally
python -m src.publisher
```

---

## 🔐 Security & Secrets
- `GEMINI_API_KEY`: Stored exclusively in GitHub Secrets.
- `GITHUB_PAT`: Personal Access Token with repository write permissions for cross-repo publishing.

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
