"""Publication checks use fake secrets and isolated repositories only."""
import importlib.util
import subprocess
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    'publication_guard', Path(__file__).resolve().parents[1] / 'scripts/check_publication.py')
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


@pytest.mark.parametrize('name', ['.env', '.env.production', 'data/raw/vendor.json',
                                 'data/processed/history.csv', 'reports/evidence/probe.json',
                                 'results/run/one_session_trace.json', 'results/run/trades.parquet'])
def test_restricted_paths_fail_even_if_force_added(name):
    assert guard.inspect_blob(name, b'innocuous') == ['RESTRICTED_PATH']


def test_secret_match_is_reported_only_as_code():
    fake = ('PK' + 'A' * 18).encode()
    assert guard.inspect_blob('accidental.txt', fake, (fake,)) == ['LOCAL_SECRET_VALUE', 'SECRET_PATTERN']
    assert guard.inspect_blob('.env.example', b'APCA_API_KEY_ID=\n') == []
    assert guard.inspect_blob('results/run/metrics.json', b'{}') == []


def test_deleted_secret_is_detected_in_history(tmp_path):
    def git(*args):
        return subprocess.run(['git', *args], cwd=tmp_path, capture_output=True, check=True)
    git('init', '-b', 'main')
    (tmp_path / 'leak.txt').write_text('PK' + 'A' * 18)
    git('add', '.')
    git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-m', 'fixture')
    git('rm', 'leak.txt')
    git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-m', 'remove')
    scanned, findings = guard.scan_repository(tmp_path)
    assert scanned > 0
    assert ('history', 'leak.txt', 'SECRET_PATTERN') in findings


def test_local_values_never_appear_in_findings(tmp_path):
    (tmp_path / '.env').write_text('APCA_API_SECRET_KEY="pretend-sensitive-value"\n')
    values = guard.local_secret_values(tmp_path)
    assert guard.inspect_blob('bad.txt', b'pretend-sensitive-value', values) == ['LOCAL_SECRET_VALUE']
