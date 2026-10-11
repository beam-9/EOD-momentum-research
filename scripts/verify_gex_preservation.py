"""Verify the GEX pivot preserves legacy bytes; never deserialize market data."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

BASELINE = '32c843ab5ef6fb2dc4d7f4aefcc364719652e873'
CURRENT_DOCS = {'README.md', 'reports/PROJECT_STATUS.md', 'docs/PUBLICATION.md'}
UNDERLYING_SHA256 = '435db3c8e69e96c5356a385c1941ac889a083d36ceaa0c66b186cfec5bfae2c5'


def verify(root: Path, *, hash_private_data: bool = False) -> dict:
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=root)

    preserved = {}
    mismatches = []
    for name in git('ls-tree', '-r', '--name-only', BASELINE).decode().splitlines():
        if name in CURRENT_DOCS:
            continue
        original = git('show', f'{BASELINE}:{name}')
        path = root / name
        if not path.is_file() or path.read_bytes() != original:
            mismatches.append(name)
        preserved[name] = hashlib.sha256(original).hexdigest()
    archives = {}
    for name, archived in [('README.md', 'EOD_README_2026-10-11.md'),
                           ('reports/PROJECT_STATUS.md', 'EOD_PROJECT_STATUS_2026-10-11.md')]:
        path = root / 'docs/gex/archive' / archived
        archives[name] = path.is_file() and path.read_bytes() == git('show', f'{BASELINE}:{name}')
    data_status = 'NOT_READ'
    if hash_private_data:
        path = root / 'data/processed/underlying.parquet'
        if not path.exists():
            data_status = 'LOCAL_DATA_ABSENT'
        else:
            with path.open('rb') as stream:
                digest = hashlib.file_digest(stream, 'sha256').hexdigest()
            data_status = 'PASS' if digest == UNDERLYING_SHA256 else 'FAIL'
    passed = not mismatches and all(archives.values()) and data_status != 'FAIL'
    return {'status': 'PASS' if passed else 'FAIL', 'baseline_commit': BASELINE,
            'unchanged_file_count': len(preserved) - len(mismatches),
            'legacy_sha256': preserved, 'mismatched_paths': mismatches,
            'exact_archives': archives, 'private_data_hash_check': data_status,
            'expected_underlying_sha256': UNDERLYING_SHA256,
            'data_content_deserialized': False,
            'holdout_boundary': '2026-04-10',
            'scope': 'Byte preservation only; not a proof of all historical access behavior.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--hash-private-data', action='store_true')
    args = parser.parse_args(argv)
    if args.output.exists():
        parser.error('Output already exists; choose a new evidence path')
    result = verify(Path(__file__).resolve().parents[1], hash_private_data=args.hash_private_data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'legacy_sha256'}, indent=2))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
