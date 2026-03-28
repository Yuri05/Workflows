#!/usr/bin/env python3
"""
Script to create GitHub issues for outdated actions using the analysis results.
"""

import os
import sys
import json

# Import from the check script
sys.path.insert(0, '/home/runner/work/Workflows/Workflows')
from check_gha_versions import (
    find_yaml_files, analyze_yaml_file, check_for_updates,
    create_issue_body, create_github_issue
)

def main():
    """Create all GitHub issues for outdated actions."""
    repo_root = '/home/runner/work/Workflows/Workflows'
    workflows_dir = os.path.join(repo_root, '.github/workflows')
    actions_dir = os.path.join(repo_root, '.github/actions')
    repo_url = 'https://github.com/Open-Systems-Pharmacology/Workflows'
    repo = 'Open-Systems-Pharmacology/Workflows'

    # Get GitHub token from environment
    github_token = os.environ.get('GITHUB_TOKEN')

    if not github_token:
        print("Error: GITHUB_TOKEN not found in environment.", file=sys.stderr)
        print("Cannot create issues without authentication.", file=sys.stderr)
        return 1

    # Find all YAML files
    workflow_files = find_yaml_files(workflows_dir)
    action_files = []
    for root, dirs, files in os.walk(actions_dir):
        for file in files:
            if file in ['action.yml', 'action.yaml']:
                action_files.append(os.path.join(root, file))

    all_files = workflow_files + action_files

    print(f"Found {len(workflow_files)} workflow files and {len(action_files)} action files")

    # Collect issues to create
    issues_to_create = []

    for file_path in all_files:
        actions_used = analyze_yaml_file(file_path)
        if not actions_used:
            continue

        outdated_actions = check_for_updates(actions_used, github_token)
        if outdated_actions:
            issue_body = create_issue_body(file_path, repo_url, outdated_actions)
            rel_path = file_path.replace(f'{repo_root}/', '')
            issues_to_create.append({
                'title': f'Update outdated GitHub Actions in {rel_path}',
                'body': issue_body,
                'file': rel_path
            })

    print(f"\nFound {len(issues_to_create)} files with outdated actions")
    print(f"Creating {len(issues_to_create)} GitHub issues in {repo}...\n")

    # Create issues
    created_count = 0
    failed_count = 0

    for i, issue in enumerate(issues_to_create, 1):
        print(f"[{i}/{len(issues_to_create)}] Creating issue: {issue['title']}")
        result = create_github_issue(issue['title'], issue['body'], repo, github_token)
        if result:
            created_count += 1
        else:
            failed_count += 1
        print()  # Empty line for readability

    # Summary
    print("="*80)
    print(f"Summary:")
    print(f"  ✓ Successfully created: {created_count} issues")
    if failed_count > 0:
        print(f"  ✗ Failed to create: {failed_count} issues")
    print("="*80)

    return 0 if failed_count == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
