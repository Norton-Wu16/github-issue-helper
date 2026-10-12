# GitHub Issue Helper — Dify Plugin

A Dify tool plugin that lets you list and inspect GitHub issues inside Dify workflows, chatflows, and agent apps.

## What it does

- List issues in any public or private GitHub repository (by owner/repo)
- Filter by state: **open**, **closed**, or **all**
- Control the number of results returned (1-100)
- Returns structured JSON with issue number, title, URL, author, labels, and creation date

## Why this plugin?

When triaging a GitHub repository — especially for DevRel or community work — it's tedious to manually scroll through dozens of issues. This plugin brings GitHub issue data directly into Dify, so you can combine it with LLM nodes to summarize, classify, or generate reports.

## Installation

### 1. Clone this repository

git clone https://github.com/Norton-Wu16/github-issue-helper.git
cd github-issue-helper

### 2. Install dependencies

pip install -r requirements.txt

### 3. Install into Dify

There are two ways to install the plugin into Dify:

**Option A — Marketplace installation (recommended):**

1. In Dify, go to **Plugins → Marketplace**.
2. Search for "GitHub Issue Helper" and click **Install**.

**Option B — Remote debugging (for development):**

1. Copy ".env.example" to ".env" and fill in your Dify debug URL and key:
   cp .env.example .env
2. Run the plugin locally:
   python -m main
3. The plugin will connect to your Dify instance and appear in the plugin list.

## Configuration

This plugin requires a **GitHub Personal Access Token** with repo scope.

1. Create a token at https://github.com/settings/tokens
2. In Dify, go to **Plugins → GitHub Issue Helper → Settings**
3. Paste your token into the **GitHub Personal Access Token** field and save

> The token is stored as an encrypted secret and never exposed in logs or responses.

## How to use

1. Install and configure the plugin (see above).
2. In a **Workflow**, **Chatflow**, or **Agent** app, add a **Tool** node.
3. Select **GitHub Issue Helper → List Issues**.
4. Provide the input parameters:
   - owner — GitHub username or organization (e.g., langgenius)
   - repo — repository name (e.g., dify)
   - state (optional) — open (default), closed, or all
   - per_page (optional) — number of issues, 1-100 (default: 10)

## Example usage

**Input:**

| Parameter | Value |
|---|---|
| owner | langgenius |
| repo | dify |
| state | open |
| per_page | 5 |

**Output (JSON):**

```json
{
  "repository": "langgenius/dify",
  "state_filter": "open",
  "count": 5,
  "issues": [
    {
      "number": 12345,
      "title": "Bug: Workflow execution fails on large inputs",
      "state": "open",
      "html_url": "https://github.com/langgenius/dify/issues/12345",
      "user": "octocat",
      "labels": ["bug", "workflow"],
      "created_at": "2025-10-10T08:00:00Z"
    }
  ]
}
```

## Error handling

The plugin handles common GitHub API errors gracefully:

| Status | Cause | Message returned to user |
|---|---|---|
| 401 | Invalid or expired token | Asks user to update credentials |
| 403 | Rate limit exceeded | Shows the rate-limit reset timestamp |
| 404 | Repo not found or no access | Explains the likely cause |
| Timeout | Network delay | Suggests retrying |
| Connection error | Network unreachable | Suggests checking connection |

## Built with

- [Dify Plugin SDK](https://github.com/langgenius/dify-plugin-sdks)
- [GitHub REST API](https://docs.github.com/en/rest)
- Python requests library

## License

MIT
