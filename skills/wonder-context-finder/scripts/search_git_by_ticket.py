#!/usr/bin/env python3
"""
Search git history for Jira ticket references in the Wonder monorepo.

Usage:
    python search_git_by_ticket.py MD-17329
    python search_git_by_ticket.py MD-17329 --repo C:/CT-Project
    python search_git_by_ticket.py MD-17329 --files
"""
import subprocess
import re
import sys
import json
import argparse
from pathlib import Path

DEFAULT_REPO = "C:/CT-Project"

def search_commits_by_ticket(ticket_id: str, repo_path: str = DEFAULT_REPO) -> list:
    """Search git commits containing the ticket ID."""
    cmd = [
        "git", "-C", repo_path, "log", "--all", "--oneline",
        f"--grep={ticket_id}", "--format=%H|%s|%an|%ad", "--date=short"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    commits = []
    for line in result.stdout.strip().split('\n'):
        if line:
            parts = line.split('|')
            if len(parts) >= 4:
                commits.append({
                    "hash": parts[0],
                    "message": parts[1],
                    "author": parts[2],
                    "date": parts[3]
                })
    return commits

def get_changed_files(commit_hash: str, repo_path: str = DEFAULT_REPO) -> list:
    """Get files changed in a specific commit."""
    cmd = ["git", "-C", repo_path, "diff-tree", "--no-commit-id", "--name-only", "-r", commit_hash]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    return [f for f in result.stdout.strip().split('\n') if f]

def get_commit_diff_stats(commit_hash: str, repo_path: str = DEFAULT_REPO) -> dict:
    """Get diff statistics for a commit."""
    cmd = ["git", "-C", repo_path, "show", "--stat", "--format=", commit_hash]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    return {"stats": result.stdout.strip()}

def search_ticket(ticket_id: str, repo_path: str = DEFAULT_REPO, include_files: bool = False):
    """Main search function."""
    # Validate ticket format
    if not re.match(r'^MD-\d{4,5}$', ticket_id):
        print(f"Warning: Ticket format should be MD-XXXXX, got: {ticket_id}")

    commits = search_commits_by_ticket(ticket_id, repo_path)

    results = {
        "ticket": ticket_id,
        "repository": repo_path,
        "commit_count": len(commits),
        "commits": []
    }

    for commit in commits[:20]:  # Limit to recent 20
        commit_data = {**commit}
        if include_files:
            files = get_changed_files(commit["hash"], repo_path)
            commit_data["files_changed"] = files[:15]  # Limit files shown
            commit_data["file_count"] = len(files)
        results["commits"].append(commit_data)

    return results

def print_results(results: dict, verbose: bool = False):
    """Print results in a readable format."""
    print(f"\n{'='*60}")
    print(f"Jira Ticket: {results['ticket']}")
    print(f"Repository: {results['repository']}")
    print(f"Total Commits: {results['commit_count']}")
    print(f"{'='*60}\n")

    if not results['commits']:
        print("No commits found for this ticket.")
        return

    for i, commit in enumerate(results['commits'], 1):
        print(f"{i}. [{commit['date']}] {commit['hash'][:8]}")
        print(f"   Message: {commit['message']}")
        print(f"   Author: {commit['author']}")

        if 'files_changed' in commit:
            print(f"   Files ({commit['file_count']} total):")
            for f in commit['files_changed']:
                print(f"      - {f}")
        print()

def main():
    parser = argparse.ArgumentParser(description='Search git history for Jira ticket references')
    parser.add_argument('ticket', help='Jira ticket ID (e.g., MD-17329)')
    parser.add_argument('--repo', default=DEFAULT_REPO, help=f'Repository path (default: {DEFAULT_REPO})')
    parser.add_argument('--files', action='store_true', help='Include changed files for each commit')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    results = search_ticket(args.ticket, args.repo, args.files)

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print_results(results, verbose=args.files)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Demo mode
        print("Usage: python search_git_by_ticket.py MD-XXXXX [--repo PATH] [--files] [--json]")
        print("\nExample:")
        print("  python search_git_by_ticket.py MD-17329")
        print("  python search_git_by_ticket.py MD-17329 --files")
        print("  python search_git_by_ticket.py MD-17329 --json")
    else:
        main()
