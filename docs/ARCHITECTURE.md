# System Architecture & Technical Specifications

## Architectural Overview

`GitHubDev` is an unattended, configuration-driven GitHub automation platform designed according to layered software architecture and SOLID design principles.

```
                    +--------------------------------+
                    |    GitHub Actions Workflows    |
                    | (daily, weekly, recovery, CLI) |
                    +---------------+----------------+
                                    |
                                    v
                    +--------------------------------+
                    |     Publisher Orchestrator     |
                    |       (src/publisher.py)       |
                    +---------------+----------------+
                                    |
     +-----------------+------------+------------+-----------------+
     |                 |                         |                 |
     v                 v                         v                 v
+----------+   +---------------+        +-----------------+   +----------+
|  Config  |   |  Progress &   |        |   Gemini API    |   | GitHub   |
|  Loader  |   |  State Mgmt   |        |    Client       |   | Manager  |
+----------+   +---------------+        +-----------------+   +----------+
                       |                         |                 |
                       v                         v                 v
               +---------------+        +-----------------+   +----------+
               |   Syllabus    |        |   Markdown      |   | README   |
               |    Manager    |        |   Formatter     |   | Generator|
               +---------------+        +-----------------+   +----------+
```

---

## Component Responsibilities

1. **ConfigLoader (`src/config_loader.py`)**:
   - Parses `config/config.yaml` using Pydantic models.
   - Inject environment secrets (`GEMINI_API_KEY`, `GITHUB_PAT`).

2. **ProgressManager (`src/progress_manager.py`)**:
   - Manages state file `state/progress.json`.
   - Guarantees contiguous progress progression (only increments state after successful push).

3. **SyllabusManager (`src/syllabus_manager.py`)**:
   - Parses 90-day curriculum schema in `syllabus/python_90_days.json`.
   - Validates prerequisites and lesson sequence.

4. **PromptBuilder (`src/prompt_builder.py`)**:
   - Compiles template placeholders in `prompts/python_lesson_prompt.md`.

5. **GeminiClient (`src/gemini_client.py`)**:
   - Handles Google Gemini API requests via official `google-genai` SDK.
   - Primary model `gemini-2.5-flash` (3 retries with exponential backoff) with automatic fallback to `gemini-1.5-pro`.

6. **MarkdownFormatter (`src/markdown_formatter.py`)**:
   - Sanitizes raw AI text and validates presence of all 9 required lesson sections.

7. **CacheManager (`src/cache_manager.py`)**:
   - Pre-generates 7-day lesson batch every Sunday.
   - Computes SHA256 content hashes to verify integrity.

8. **GitHubManager (`src/github_manager.py`)**:
   - Manages cross-repo git commits to `deepakrajjs-29/Codewithpython` via GitHub REST API.

9. **ReadmeGenerator (`src/readme_generator.py`)**:
   - Generates live progress bar dashboard for target repository `Codewithpython/README.md`.

10. **RecoveryManager (`src/recovery_manager.py`)**:
    - Appends detailed failure logs to `backup/automation_log.md`.
