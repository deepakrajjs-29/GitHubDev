# Troubleshooting & Error Recovery Guide

This guide covers common failure modes, diagnostic logs, and manual intervention protocols.

---

## 🔍 Audit & Failure Logs

When any failure occurs during Gemini generation or GitHub publishing:
1. Progress state in `state/progress.json` remains **unchanged**.
2. Failure metadata is appended to `backup/automation_log.md`.
3. Execution log details are saved to `logs/execution.log`.

---

## 🚨 Common Error Scenarios

### 1. Gemini Rate Limit / Quota Exceeded
- **Symptom**: Primary model `gemini-2.5-flash` returns API error or HTTP 429.
- **Engine Recovery**: Engine automatically retries 3 times with exponential backoff, then switches to fallback model `gemini-1.5-pro`.
- **Manual Fix**: Check API key quota or re-run workflow manually via `manual_dispatch.yml`.

### 2. GitHub Authentication Failure
- **Symptom**: GitHub REST API returns `401 Unauthorized` or `403 Forbidden`.
- **Cause**: `GITHUB_PAT` secret is missing or expired.
- **Fix**: Re-generate Fine-Grained PAT with `repo` contents write permission and update repository secrets.

### 3. Missing Markdown Sections
- **Symptom**: `MarkdownFormatError` raised.
- **Cause**: AI output missed one of the 9 required section headings.
- **Fix**: The engine automatically rejects malformed markdown and logs the failure for retry on the next schedule.
