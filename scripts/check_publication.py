"""Fail closed on secrets or restricted files in staged content and Git history.

Only filenames and issue codes are printed; matching content is never printed.
This supplements .gitignore because force-add can bypass ignore rules.
"""
from __future__ import annotations

import argparse
import re
import shlex
import subprocess
from pathlib import Path

RESULT_FILES = {'RESEARCH_REPORT.md', 'robustness_scorecard.csv', 'metrics.json',
                'walk_forward_folds.csv', 'execution_cost_frontier.csv'}
PATTERNS = (
    rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
    rb'\b(?:PK|AK)[A-Z0-9]{18}\b',
    rb'\bgh[pousr]_[A-Za-z0-9]{30,}\b',
    rb'\bgithub_pat_[A-Za-z0-9_]{30,}\b',
)


def restricted_path(name):
    path = Path(name)
    if path.name == '.env.example':
        return False
    if path.name.startswith('.env') or path.name == '.DS_Store':
        return True
    if any(part in {'.venv', '__pycache__', '.aws', '.ssh'} for part in path.parts):
        return True
    if name.startswith(('data/raw/', 'data/processed/', 'reports/evidence/')):
        return True
    if path.suffix in {'.parquet', '.pem', '.key'}:
        return True
    if name.startswith('results/'):
        chart = path.suffix == '.png' and path.parent.name == 'charts'
        return path.name not in RESULT_FILES and not chart
    return False


def inspect_blob(name, content, secret_values=()):
    issues = []
    if restricted_path(name):
        issues.append('RESTRICTED_PATH')
    if any(value and value in content for value in secret_values):
        issues.append('LOCAL_SECRET_VALUE')
    if any(re.search(pattern, content) for pattern in PATTERNS):
        issues.append('SECRET_PATTERN')
    return issues


def local_secret_values(root):
    """Read optional local credential assignments without echoing parser errors."""
    path = root / '.env'
    if not path.exists():
        return ()
    values = []
    for line in path.read_text().splitlines():
        name, sep, value = line.strip().removeprefix('export ').partition('=')
        if not sep or not any(word in name.upper() for word in ('KEY', 'SECRET', 'TOKEN', 'PASSWORD')):
            continue
        try:
            parts = shlex.split(value, comments=True)
        except ValueError:
            raise ValueError('LOCAL_CREDENTIAL_FILE_INVALID') from None
        values.extend(part.encode() for part in parts if part)
    return tuple(values)


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root, stderr=subprocess.DEVNULL)


def scan_repository(root, *, staged=True, history=True):
    values = local_secret_values(root)
    findings = []
    scanned = 0
    if staged:
        entries = git(root, 'ls-files', '--stage', '-z').split(b'\0')
        for entry in filter(None, entries):
            metadata, raw_name = entry.split(b'\t', 1)
            mode, oid, stage = metadata.decode().split()
            name = raw_name.decode()
            issues = inspect_blob(name, git(root, 'cat-file', 'blob', oid), values)
            if mode == '120000':
                issues.append('SYMLINK_REQUIRES_REVIEW')
            if stage != '0':
                issues.append('UNMERGED_INDEX')
            scanned += 1
            findings.extend(('index', name, code) for code in issues)
    if history:
        seen = set()
        for commit in git(root, 'rev-list', '--all').decode().splitlines():
            for entry in filter(None, git(root, 'ls-tree', '-rz', '--full-tree', commit).split(b'\0')):
                metadata, raw_name = entry.split(b'\t', 1)
                mode, kind, oid = metadata.decode().split()
                name = raw_name.decode()
                if (oid, name) in seen:
                    continue
                seen.add((oid, name))
                issues = []
                if kind == 'blob':
                    issues = inspect_blob(name, git(root, 'cat-file', 'blob', oid), values)
                if mode == '120000':
                    issues.append('SYMLINK_REQUIRES_REVIEW')
                if kind == 'commit':
                    issues.append('SUBMODULE_REQUIRES_REVIEW')
                scanned += 1
                findings.extend(('history', name, code) for code in issues)
    return scanned, findings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--staged', action='store_true')
    parser.add_argument('--history', action='store_true')
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    try:
        scanned, findings = scan_repository(root, staged=args.staged or not args.history,
                                            history=args.history or not args.staged)
    except (ValueError, OSError, subprocess.CalledProcessError):
        print('Publication check FAILED: repository or local credential parsing error; no values logged')
        return 2
    for scope, name, code in findings:
        print(f'{scope}: {name}: {code}')
    print(f'Publication check: {"FAIL" if findings else "PASS"}; {scanned} blobs scanned; no values logged')
    return 1 if findings else 0


if __name__ == '__main__':
    raise SystemExit(main())
