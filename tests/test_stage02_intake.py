"""Synthetic intake fixtures only; never contact Alpaca or read project credentials."""

import importlib.util
import json
import os
from pathlib import Path

import pytest
import yaml

from conftest import synthetic

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/stage02_intake.py"


def load_module():
    spec = importlib.util.spec_from_file_location("stage02_intake_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def intake(monkeypatch, tmp_path, cfg):
    module = load_module()
    for name in module._CREDENTIAL_NAMES:
        monkeypatch.delenv(name, raising=False)
    (tmp_path / "config").mkdir()
    (tmp_path / "config/default.yaml").write_text(yaml.safe_dump(cfg))
    monkeypatch.setattr(module, "protocol_status", lambda config: "PRE_REGISTERED")
    return module, tmp_path


def credentials(monkeypatch):
    monkeypatch.setenv("APCA_API_KEY_ID", "fixture-key")
    monkeypatch.setenv("APCA_API_SECRET_KEY", "fixture-secret")


def forbidden_fetch(*args, **kwargs):
    pytest.fail("Provider must not be called before intake gates pass")


def test_import_does_not_read_files_create_evidence_or_parse_arguments(monkeypatch):
    # Cache dependencies before intercepting script filesystem/argument I/O.
    load_module()

    def forbidden(*args, **kwargs):
        pytest.fail("Import must not perform filesystem or argument I/O")

    import argparse

    monkeypatch.setattr(Path, "read_text", forbidden)
    monkeypatch.setattr(Path, "mkdir", forbidden)
    monkeypatch.setattr(argparse.ArgumentParser, "parse_args", forbidden)
    load_module()


def test_supported_process_credentials_without_dotenv(intake, monkeypatch):
    module, root = intake
    credentials(monkeypatch)
    frame = synthetic("2024-03-08", "2024-03-08", ("SPY", "QQQ"))
    calls = []

    def provider(cfg, start, end, **kwargs):
        calls.append((cfg["feed"], start, end, kwargs))
        return frame

    result = module.run_intake(root=root, fetch_bars=provider)
    assert result["status"] == "AUTHENTICATED_SIP_REQUEST_SUCCEEDED"
    assert calls == [("sip", "2024-03-08", "2024-03-08", {"persist_result": False, "fresh_request": True})]
    assert result["symbols_coverage"]["SPY"]["rth_returned_minutes"] == 390
    assert os.environ["APCA_API_SECRET_KEY"] == "fixture-secret"
    assert result["holdout_evaluated"] is False


def test_missing_credentials_fail_closed(intake):
    module, root = intake
    result = module.run_intake(root=root, fetch_bars=forbidden_fetch)
    assert result["safe_error"] == "MISSING_LOCAL_CREDENTIAL_PAIR"
    assert result["provider_request_attempted"] is False


@pytest.mark.parametrize("gate", ["protocol", "feed", "holdout"])
def test_protocol_feed_and_holdout_gates_block_provider(intake, monkeypatch, gate):
    module, root = intake
    credentials(monkeypatch)
    path = root / "config/default.yaml"
    cfg = yaml.safe_load(path.read_text())
    if gate == "protocol":
        monkeypatch.setattr(module, "protocol_status", lambda config: "EXPLORATORY_PROTOCOL_CHANGED")
    else:
        cfg[{"feed": "feed", "holdout": "holdout_start"}[gate]] = {"feed": "iex", "holdout": "2024-03-08"}[
            gate
        ]
        path.write_text(yaml.safe_dump(cfg))
    result = module.run_intake(root=root, fetch_bars=forbidden_fetch)
    assert result["status"] == "ACCESS_OR_ACQUISITION_BLOCKED"
    assert result["provider_request_attempted"] is False


@pytest.mark.parametrize("failure", ["provider", "malformed"])
def test_restore_environment_and_sanitize_failures(intake, monkeypatch, failure):
    module, root = intake
    credentials(monkeypatch)
    monkeypatch.setenv("UNRELATED_SETTING", "keep")
    before = {name: os.environ.get(name) for name in module._CREDENTIAL_NAMES}
    secret = "never-print-this-value"
    text = "export APCA_API_KEY_ID=temporary-key\nALPACA_API_KEY=temporary-alternate\nUNRELATED_SETTING=overwrite\n"
    text += f'APCA_API_SECRET_KEY="{secret}' + ('"\n' if failure == "provider" else "\n")
    (root / ".env").write_text(text)

    def provider(*args, **kwargs):
        assert os.environ["APCA_API_SECRET_KEY"] == secret
        raise RuntimeError(f"ALPACA_ACCESS_FAILED secret={secret}")

    result = module.run_intake(root=root, fetch_bars=provider)
    assert result["status"] == "ACCESS_OR_ACQUISITION_BLOCKED"
    assert secret not in json.dumps(result)
    evidence = Path(result["evidence_directory"]) / "access_and_acquisition.json"
    assert secret not in evidence.read_text()
    assert {name: os.environ.get(name) for name in module._CREDENTIAL_NAMES} == before
    assert os.environ["UNRELATED_SETTING"] == "keep"
    if failure == "malformed":
        assert result["safe_error"] == "INVALID_CREDENTIAL_ASSIGNMENT"
        assert result["provider_request_attempted"] is False


def test_dotenv_restores_environment_after_success(intake, monkeypatch):
    module, root = intake
    credentials(monkeypatch)
    (root / ".env").write_text("APCA_API_KEY_ID=temporary-key\nAPCA_API_SECRET_KEY=temporary-secret\n")
    frame = synthetic("2024-03-08", "2024-03-08", ("SPY", "QQQ"))
    result = module.run_intake(root=root, fetch_bars=lambda *args, **kwargs: frame)
    assert result["probe_quality_pass"] is True
    assert os.environ["APCA_API_KEY_ID"] == "fixture-key"
    assert os.environ["APCA_API_SECRET_KEY"] == "fixture-secret"


@pytest.mark.parametrize("acquire", [False, True])
def test_bad_probe_quality_fails_without_acquisition(intake, monkeypatch, acquire):
    module, root = intake
    credentials(monkeypatch)
    frame = synthetic("2024-03-08", "2024-03-08", ("SPY", "QQQ")).slice(1)
    calls = []

    def provider(*args, **kwargs):
        calls.append(args)
        return frame

    result = module.run_intake(root=root, fetch_bars=provider, acquire=acquire)
    assert len(calls) == 1
    assert result["safe_error"] == "PROBE_QUALITY_GATE_FAILED"
    assert "full_acquisition_started" not in result
    monkeypatch.setattr(module, "run_intake", lambda **kwargs: result)
    assert module.main(["--acquire"] if acquire else []) == 2
