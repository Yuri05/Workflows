# GitHub Actions Version Checker

This script analyzes GitHub workflows and actions for outdated external action references and optionally creates GitHub issues for files that need updates.

## Overview

The script performs the following tasks:

1. Scans all GitHub workflow files (`.github/workflows/*.yml`, `.github/workflows/*.yaml`)
2. Scans all GitHub action files (`.github/actions/*/action.yml`, `.github/actions/*/action.yaml`)
3. Identifies external GitHub actions referenced via `uses:`
4. Checks the latest released major version for each external action via GitHub API
5. Compares current versions against latest versions
6. Optionally creates GitHub issues for files with outdated actions

## Requirements

- Python 3.6+
- Required Python packages:
  - `requests`
  - `pyyaml`

Install dependencies:
```bash
pip install requests pyyaml
```

## Usage

### Analyze workflows and actions (dry run)

Run the script without creating issues to see what would be updated:

```bash
python3 check_gha_versions.py
```

This will:
- Scan all workflows and actions
- Check for outdated external actions
- Display a summary and proposed issue content
- NOT create any GitHub issues

### Create GitHub issues for outdated actions

To actually create GitHub issues, use the `--create-issues` flag:

```bash
export GITHUB_TOKEN=your_github_token
python3 check_gha_versions.py --create-issues
```

**Note:** The `--create-issues` flag requires a `GITHUB_TOKEN` environment variable with permissions to create issues in the target repository.

### Options

- `--create-issues`: Create GitHub issues for outdated actions (requires GITHUB_TOKEN)
- `--repo REPO`: Repository in format `owner/repo` (default: `Open-Systems-Pharmacology/Workflows`)
- `--repo-root REPO_ROOT`: Path to repository root (default: `/home/runner/work/Workflows/Workflows`)

### Examples

Analyze a different repository:
```bash
python3 check_gha_versions.py --repo myorg/myrepo --repo-root /path/to/repo
```

Analyze and create issues:
```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
python3 check_gha_versions.py --create-issues
```

## Output Format

For each file with outdated actions, the script generates an issue with:

- **Title**: `Update outdated GitHub Actions in <file-path>`
- **Body**: Markdown formatted with:
  - Link to the file in the repository
  - Table with three columns:
    - **Action used**: Current action reference (e.g., `actions/checkout@v5`)
    - **Action latest**: Latest major version (e.g., `actions/checkout@v6`)
    - **Number of occurrences**: Count of usages in the file

### Example Issue

```markdown
## Outdated GitHub Actions in Workflow/Action

**File:** https://github.com/Open-Systems-Pharmacology/Workflows/blob/main/.github/workflows/test.yml

The following external GitHub Actions are using outdated major versions:

| Action used | Action latest | Number of occurrences |
|-------------|---------------|----------------------|
| actions/checkout@v5 | actions/checkout@v6 | 2 |
| actions/setup-python@v4 | actions/setup-python@v6 | 1 |
```

## How It Works

### Action Parsing

The script:
1. Reads YAML workflow and action files
2. Finds all `uses:` statements
3. Filters out local actions (starting with `./` or from the same repository)
4. Extracts owner, repo, and version from external action references

### Version Checking

For each external action:
1. Queries GitHub API for releases/tags
2. Extracts major version numbers (e.g., `v5` from `v5.2.1`)
3. Compares current major version against latest major version
4. Reports actions where latest major version is newer

### Issue Creation

When `--create-issues` is enabled:
1. Creates one issue per file with outdated actions
2. Groups all outdated actions in a single table per file
3. Uses GitHub API to create issues in the specified repository
4. Prints confirmation with issue URLs

## Authentication

The script uses the `GITHUB_TOKEN` environment variable for GitHub API authentication. This is required for:
- Creating issues (when using `--create-issues`)
- Avoiding rate limiting on API requests

To generate a GitHub token:
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with `repo` scope
3. Export it: `export GITHUB_TOKEN=your_token`

## Limitations

- Only checks major version updates (e.g., v5 → v6, not v5.1 → v5.2)
- Does not analyze local actions (those starting with `./`)
- Does not analyze actions from the same repository being scanned
- Rate limiting applies if no GitHub token is provided

## Exit Codes

- `0`: Success
- `1`: Error (e.g., missing GITHUB_TOKEN when --create-issues is used)

## Example Output

```
Found 24 workflow files and 11 action files

Analyzing: /path/to/.github/workflows/test.yml
  Found 3 unique external actions
  ⚠️  Found 2 outdated actions

  ...

================================================================================
Summary: Found 16 files with outdated actions
================================================================================

Creating 16 GitHub issues...

Creating issue: Update outdated GitHub Actions in .github/workflows/test.yml
  ✓ Created issue #123: https://github.com/org/repo/issues/123
```
