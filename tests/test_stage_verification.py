"""Engineering-only regression tests: evidence preservation and revision identity."""
import importlib.util
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from eod_momentum import common


def verifier():
    spec = importlib.util.spec_from_file_location('stage_verify',
                                                Path(__file__).parents[1] / 'scripts/verify.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_checks_only_never_invokes_data_or_research(tmp_path, monkeypatch):
    module = verifier()
    commands = []

    def fake_run(command, **kwargs):
        commands.append(command)
        return SimpleNamespace(returncode=0, stdout='TEST_ONLY\n', stderr='')

    monkeypatch.setattr(module.subprocess, 'run', fake_run)
    out = tmp_path / 'new_verification'
    assert module.main(['--checks-only', '--output-dir', str(out)]) == 0
    assert len(commands) == 4
    assert not any('eod_momentum.cli' in cmd for cmd in commands)
    assert len(json.loads((out / 'commands.json').read_text())) == 4


def test_verification_refuses_existing_evidence_before_work(tmp_path, monkeypatch):
    module = verifier()
    sentinel = tmp_path / 'commands.json'
    sentinel.write_text('PRIOR_EVIDENCE')

    def forbidden(*args, **kwargs):
        pytest.fail('Must refuse overwrite before running any subprocess')

    monkeypatch.setattr(module.subprocess, 'run', forbidden)
    with pytest.raises(FileExistsError):
        module.main(['--output-dir', str(tmp_path)])
    assert sentinel.read_text() == 'PRIOR_EVIDENCE'


def test_failed_git_revision_is_not_literal_head(monkeypatch):
    monkeypatch.setattr(common.subprocess, 'run',
                        lambda *args, **kwargs: SimpleNamespace(returncode=128, stdout='HEAD\n'))
    monkeypatch.setattr(common, 'distributions', lambda: [])
    assert common.environment()['git_commit'] == 'UNCOMMITTED_REPOSITORY'


def test_access_report_refuses_overwrite(tmp_path):
    path = tmp_path / 'access.json'
    path.write_text('PRIOR_ACCESS_EVIDENCE')
    result = subprocess.run([
        str(Path(__file__).parents[1] / '.venv/bin/python'), '-m', 'eod_momentum.cli',
        'data', 'check', '--probe', '--report-path', str(path)], capture_output=True, text=True)
    assert result.returncode == 2
    assert 'already exists' in result.stderr
    assert path.read_text() == 'PRIOR_ACCESS_EVIDENCE'
