# Step-by-Step Setup Guide: GitHub Secrets & Personal Access Token (PAT)

This guide walks you through generating a GitHub Personal Access Token (PAT) and configuring GitHub Secrets so that `GitHubDev` can automatically publish lessons to `Codewithpython`.

---

## 🔑 Part 1: How to Generate a GitHub Personal Access Token (PAT)

To allow `GitHubDev` to commit generated lessons to your target repository `deepakrajjs-29/Codewithpython`, follow these steps:

1. **Log in to GitHub** and open your account settings:
   - Go to: **[https://github.com/settings/tokens](https://github.com/settings/tokens)**

2. **Generate a Fine-Grained Personal Access Token** (Recommended):
   - Click **Generate new token** -> **Generate new token (beta)**.
   - **Token Name**: `GitHubDev Cross-Repo Publisher`
   - **Expiration**: Select `90 days` or `No expiration`.
   - **Repository Access**: Select **Only select repositories** -> Select `deepakrajjs-29/Codewithpython`.
   - **Permissions**:
     - Under **Repository permissions**, find **Contents**.
     - Set access to: **Read and write**.
   - Click **Generate token** at the bottom of the page.

3. **Copy Your Token**:
   - Copy the generated token string (starts with `github_pat_...`).
   - Save it temporarily in a safe place. *Note: GitHub will only show it once!*

---

## 🔐 Part 2: Adding Secrets to Repository A (`GitHubDev`)

> [!IMPORTANT]
> 1. GitHub prohibits secret & variable names starting with `GITHUB_` (e.g. `GITHUB_PAT` is rejected by GitHub validation). We use **`GH_PAT`** instead.
> 2. Open **Secrets** (not Variables), as secrets encrypt your access token and mask it in workflow logs.

Follow these exact steps:

1. Open your **`GitHubDev`** repository on GitHub:
   - `https://github.com/deepakrajjs-29/GitHubDev`

2. Click **Settings** -> **Secrets and variables** -> **Actions**.

3. Make sure you are on the **Secrets** tab (click **New repository secret**):

### Secret 1: `GEMINI_API_KEY`
- **Name**: `GEMINI_API_KEY`
- **Secret Value**: Your Google Gemini API Key.
- Click **Add secret**.

### Secret 2: `GH_PAT`
- **Name**: `GH_PAT` *(Note: Use `GH_PAT`, not `GITHUB_PAT`!)*
- **Secret Value**: The Fine-Grained Personal Access Token generated in Part 1 (`github_pat_11BFC...`).
- Click **Add secret**.

---

## 🚀 Part 3: Verify Deployment

Once secrets are added:
1. Go to the **Actions** tab in `GitHubDev`.
2. Select **Manual Workflow Dispatch**.
3. Click **Run workflow** (or check `dry_run` for a test run).
4. Check the workflow logs to confirm clean publishing!
