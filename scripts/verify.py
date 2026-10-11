"""Versioned verification. --checks-only excludes data probes and economic replay."""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def main(argv=None):
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, help='New directory; existing paths are refused')
    parser.add_argument('--checks-only', action='store_true',
                        help='Software checks only; no data access or research replay')
    args = parser.parse_args(argv)
    verification = args.output_dir or root / 'results' / (
        'verification_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    verification = verification.resolve()
    verification.mkdir(parents=True, exist_ok=False)
    env = {**os.environ, 'PYTHONPATH': str(root / 'src')}
    env.setdefault('MPLCONFIGDIR', str(root / '.mpl-cache'))
    commands = [
        ([sys.executable, '-m', 'pytest', '-q', '--junitxml=' + str(verification / 'pytest.xml')], [0]),
        ([sys.executable, '-m', 'ruff', 'check', 'src', 'tests', 'scripts'], [0]),
        ([sys.executable, '-m', 'pip', 'check'], [0]),
        ([sys.executable, '-m', 'compileall', '-q', 'src'], [0]),
    ]
    if not args.checks_only:
        commands.extend([
            ([sys.executable, '-m', 'eod_momentum.cli', 'data', 'check', '--source', 'alpaca',
              '--probe', '--report-path', str(verification / 'access_check.json')], [0, 2]),
            ([sys.executable, '-m', 'eod_momentum.cli', 'replay'], [0]),
            ([sys.executable, '-m', 'eod_momentum.cli', 'research', 'validate'], [0]),
        ])
    results = []
    for i, (command, expected) in enumerate(commands):
        p = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False, env=env)
        (verification / f'{i + 1}_command.txt').write_text(' '.join(command) + '\n' + p.stdout + p.stderr)
        print(p.stdout, end='')
        print(p.stderr, end='', file=sys.stderr)
        results.append({'command': command, 'returncode': p.returncode, 'expected': expected})
    (verification / 'commands.json').write_text(json.dumps(results, indent=2) + '\n')
    print(f'Verification evidence: {verification}')
    return 0 if all(r['returncode'] in r['expected'] for r in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
