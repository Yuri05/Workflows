#!/usr/bin/env python3
"""
Script to analyze GitHub Actions and Workflows for outdated external action references.
Creates GitHub issues for workflows/actions that use outdated versions.
"""

import os
import re
import sys
import yaml
import requests
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# GitHub API base URL
GITHUB_API_BASE = "https://api.github.com"

def parse_action_reference(uses_line: str) -> Optional[Tuple[str, str, str]]:
    """
    Parse a 'uses:' line to extract owner, repo, and version.
    Returns (owner, repo, version) or None if it's a local action.

    Example: 'actions/checkout@v5' -> ('actions', 'checkout', 'v5')
    """
    # Skip local actions (those starting with ./)
    if uses_line.startswith('./'):
        return None

    # Skip actions from the same repository
    if 'Open-Systems-Pharmacology/Workflows/' in uses_line:
        return None

    # Pattern: owner/repo@version or owner/repo/path@version
    match = re.match(r'^([^/]+)/([^/@]+)(?:/[^@]*)?@(.+)$', uses_line.strip())
    if match:
        owner, repo, version = match.groups()
        return (owner, repo, version)

    return None

def extract_major_version(version: str) -> Optional[str]:
    """Extract major version from a version string."""
    # Handle v1, v2, etc.
    match = re.match(r'^v?(\d+)', version)
    if match:
        return f"v{match.group(1)}"
    return None

def get_latest_release(owner: str, repo: str, github_token: Optional[str] = None) -> Optional[str]:
    """
    Get the latest release tag for a GitHub repository.
    Returns the latest major version (e.g., 'v5') or None if not found.
    """
    headers = {}
    if github_token:
        headers['Authorization'] = f'token {github_token}'

    # Try to get the latest release
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/releases/latest"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            tag = data.get('tag_name', '')
            major = extract_major_version(tag)
            return major
    except Exception as e:
        print(f"Warning: Could not fetch latest release for {owner}/{repo}: {e}", file=sys.stderr)

    # Fallback: try to get all releases and find the latest
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/releases"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            releases = response.json()
            if releases:
                # Get the first (latest) release
                tag = releases[0].get('tag_name', '')
                major = extract_major_version(tag)
                return major
    except Exception as e:
        print(f"Warning: Could not fetch releases for {owner}/{repo}: {e}", file=sys.stderr)

    # Last resort: check tags
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/tags"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            tags = response.json()
            if tags:
                # Find the highest major version
                major_versions = []
                for tag in tags:
                    tag_name = tag.get('name', '')
                    major = extract_major_version(tag_name)
                    if major:
                        major_num = int(major[1:])  # Remove 'v' and convert to int
                        major_versions.append(major_num)

                if major_versions:
                    latest_major = max(major_versions)
                    return f"v{latest_major}"
    except Exception as e:
        print(f"Warning: Could not fetch tags for {owner}/{repo}: {e}", file=sys.stderr)

    return None

def find_yaml_files(directory: str) -> List[str]:
    """Find all YAML files in a directory."""
    yaml_files = []
    path = Path(directory)
    for ext in ['*.yml', '*.yaml']:
        yaml_files.extend(path.glob(ext))
    return [str(f) for f in yaml_files]

def analyze_yaml_file(file_path: str) -> Dict[str, Dict]:
    """
    Analyze a YAML file and extract external action references.
    Returns a dict mapping action names to their usage info.
    """
    actions_used = defaultdict(lambda: {'count': 0, 'version': None})

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find all 'uses:' lines
        uses_pattern = r'^\s*uses:\s*(.+)$'
        for match in re.finditer(uses_pattern, content, re.MULTILINE):
            uses_line = match.group(1).strip()

            # Parse the action reference
            parsed = parse_action_reference(uses_line)
            if parsed:
                owner, repo, version = parsed
                action_key = f"{owner}/{repo}"
                current_major = extract_major_version(version)

                actions_used[action_key]['count'] += 1
                if actions_used[action_key]['version'] is None:
                    actions_used[action_key]['version'] = current_major
                    actions_used[action_key]['full_ref'] = uses_line

    except Exception as e:
        print(f"Error analyzing {file_path}: {e}", file=sys.stderr)

    return dict(actions_used)

def check_for_updates(actions_used: Dict[str, Dict], github_token: Optional[str] = None) -> List[Dict]:
    """
    Check if any actions have newer versions available.
    Returns list of actions that need updates.
    """
    outdated_actions = []

    for action_name, info in actions_used.items():
        owner, repo = action_name.split('/')
        current_version = info['version']

        latest_version = get_latest_release(owner, repo, github_token)

        if latest_version and current_version:
            # Compare major versions
            current_major_num = int(current_version[1:])
            latest_major_num = int(latest_version[1:])

            if latest_major_num > current_major_num:
                outdated_actions.append({
                    'action': action_name,
                    'current_version': current_version,
                    'latest_version': latest_version,
                    'count': info['count'],
                    'full_ref': info['full_ref']
                })

    return outdated_actions

def create_issue_body(file_path: str, repo_url: str, outdated_actions: List[Dict]) -> str:
    """Create the GitHub issue body with the required format."""
    # Get relative path from repository root
    rel_path = file_path.replace('/home/runner/work/Workflows/Workflows/', '')
    file_url = f"{repo_url}/blob/main/{rel_path}"

    body = f"## Outdated GitHub Actions in Workflow/Action\n\n"
    body += f"**File:** {file_url}\n\n"
    body += "The following external GitHub Actions are using outdated major versions:\n\n"
    body += "| Action used | Action latest | Number of occurrences |\n"
    body += "|-------------|---------------|----------------------|\n"

    for action in sorted(outdated_actions, key=lambda x: x['action']):
        action_used = f"{action['action']}@{action['current_version']}"
        action_latest = f"{action['action']}@{action['latest_version']}"
        count = action['count']
        body += f"| {action_used} | {action_latest} | {count} |\n"

    return body

def create_github_issue(title: str, body: str, repo: str, github_token: str) -> Optional[int]:
    """
    Create a GitHub issue.
    Returns the issue number if successful, None otherwise.
    """
    # Parse repo (format: owner/repo)
    parts = repo.split('/')
    if len(parts) != 2:
        print(f"Error: Invalid repo format: {repo}", file=sys.stderr)
        return None

    owner, repo_name = parts

    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo_name}/issues"
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    data = {
        'title': title,
        'body': body
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        if response.status_code == 201:
            issue_data = response.json()
            issue_number = issue_data.get('number')
            issue_url = issue_data.get('html_url')
            print(f"  ✓ Created issue #{issue_number}: {issue_url}")
            return issue_number
        else:
            print(f"  ✗ Failed to create issue: {response.status_code} {response.text}", file=sys.stderr)
            return None
    except Exception as e:
        print(f"  ✗ Error creating issue: {e}", file=sys.stderr)
        return None

def main():
    """Main function to analyze workflows and actions."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Analyze GitHub workflows and actions for outdated external action references.'
    )
    parser.add_argument(
        '--create-issues',
        action='store_true',
        help='Create GitHub issues for outdated actions (requires GITHUB_TOKEN)'
    )
    parser.add_argument(
        '--repo',
        default='Open-Systems-Pharmacology/Workflows',
        help='Repository in format owner/repo (default: Open-Systems-Pharmacology/Workflows)'
    )
    parser.add_argument(
        '--repo-root',
        default='/home/runner/work/Workflows/Workflows',
        help='Path to repository root (default: /home/runner/work/Workflows/Workflows)'
    )

    args = parser.parse_args()

    repo_root = args.repo_root
    workflows_dir = os.path.join(repo_root, ".github/workflows")
    actions_dir = os.path.join(repo_root, ".github/actions")

    # Construct repo URL
    repo_url = f"https://github.com/{args.repo}"

    # Get GitHub token from environment
    github_token = os.environ.get('GITHUB_TOKEN')

    if not github_token:
        print("Warning: GITHUB_TOKEN not found in environment. Rate limiting may apply.", file=sys.stderr)
        if args.create_issues:
            print("Error: --create-issues requires GITHUB_TOKEN environment variable", file=sys.stderr)
            return 1

    # Find all YAML files
    workflow_files = find_yaml_files(workflows_dir)
    action_files = []

    # Find action.yml/action.yaml in all action subdirectories
    for root, dirs, files in os.walk(actions_dir):
        for file in files:
            if file in ['action.yml', 'action.yaml']:
                action_files.append(os.path.join(root, file))

    all_files = workflow_files + action_files

    print(f"Found {len(workflow_files)} workflow files and {len(action_files)} action files")

    # Analyze each file
    issues_to_create = []

    for file_path in all_files:
        print(f"\nAnalyzing: {file_path}")

        # Analyze the file
        actions_used = analyze_yaml_file(file_path)

        if not actions_used:
            print("  No external actions found")
            continue

        print(f"  Found {len(actions_used)} unique external actions")

        # Check for updates
        outdated_actions = check_for_updates(actions_used, github_token)

        if outdated_actions:
            print(f"  ⚠️  Found {len(outdated_actions)} outdated actions")
            issue_body = create_issue_body(file_path, repo_url, outdated_actions)

            # Get file name for issue title
            rel_path = file_path.replace(f'{repo_root}/', '')

            issues_to_create.append({
                'title': f"Update outdated GitHub Actions in {rel_path}",
                'body': issue_body,
                'file': rel_path
            })

            if not args.create_issues:
                print(f"\n{issue_body}\n")
        else:
            print("  ✓ All actions are up to date")

    # Summary
    print(f"\n{'='*80}")
    print(f"Summary: Found {len(issues_to_create)} files with outdated actions")
    print(f"{'='*80}")

    # Create issues
    if issues_to_create:
        if args.create_issues:
            print(f"\nCreating {len(issues_to_create)} GitHub issues...")
            for issue in issues_to_create:
                print(f"\nCreating issue: {issue['title']}")
                create_github_issue(issue['title'], issue['body'], args.repo, github_token)
        else:
            print("\nIssues to create (use --create-issues to create them):")
            for issue in issues_to_create:
                print(f"\n{'-'*80}")
                print(f"Title: {issue['title']}")
                print(f"{'-'*80}")
                print(issue['body'])

    return 0

if __name__ == '__main__':
    sys.exit(main())
