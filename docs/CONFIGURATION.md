# Multi-Course Configuration & Extension Guide

The `GitHubDev` engine is 100% decoupled from specific course content. You can adapt the automation engine to generate and publish other course repositories (such as `CodewithJava`, `CodewithSQL`, `CodewithCPP`) **without modifying a single line of Python source code**.

---

## 🛠 How to Port Engine for a New Course

To create a new course automation (e.g. `CodewithJava`):

### 1. Update `config/config.yaml`
```yaml
repositories:
  engine_repo: "deepakrajjs-29/GitHubDev"
  target_repo: "deepakrajjs-29/CodewithJava"

syllabus:
  file_path: "syllabus/java_90_days.json"
  course_name: "Java 90 Days Mastery"
  total_days: 90

prompt:
  template_path: "prompts/java_lesson_prompt.md"
```

### 2. Add Syllabus JSON
Create `syllabus/java_90_days.json` defining the course curriculum topics, difficulty levels, and lesson objectives.

### 3. Add Prompt Template
Create `prompts/java_lesson_prompt.md` with language-specific instructions for Java syntax, concepts, and code examples.

### 4. Reset Progress State
Reset `state/progress.json` with `"current_course": "Java 90 Days Mastery"`.
