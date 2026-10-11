"""Toy corporate-action records only; no network or local credential files."""

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/corporate_actions.py"


def load_module():
    spec = importlib.util.spec_from_file_location("corporate_actions_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def intake(tmp_path):
    module = load_module()
    envelope = {
        "request": dict(module.REQUEST),
        "retrieved_at_utc": "2026-10-11T00:00:00+00:00",
        "payload": {"cash_dividends": [{"symbol": "SPY", "ex_date": "2024-03-15", "id": "toy-action"}]},
    }
    raw = tmp_path / "raw.json"
    return module, envelope, raw, tmp_path / "actions.csv"


def write_raw(raw, envelope):
    raw.write_text(json.dumps(envelope))


def test_normalize_source_hash_and_frozen_schema(intake):
    module, envelope, raw, output = intake
    envelope["payload"]["cash_dividends"].append({"symbol": "QQQ", "ex_date": "2023-03-20"})
    envelope["payload"]["stock_splits"] = []
    write_raw(raw, envelope)
    result = module.reconstruct_actions(raw_input=raw, output=output)
    assert (
        output.read_text()
        == "symbol,date,kind\nQQQ,2023-03-20,cash_dividends\nSPY,2024-03-15,cash_dividends\n"
    )
    manifest = json.loads(Path(result["manifest"]).read_text())
    assert manifest["raw_sha256"] == hashlib.sha256(raw.read_bytes()).hexdigest()
    assert manifest["normalized_sha256"] == hashlib.sha256(output.read_bytes()).hexdigest()
    assert manifest["historical_publication_timestamps"] == "UNKNOWN"
    assert manifest["coverage_completeness"] == "UNKNOWN_INDEPENDENT_EXHAUSTIVENESS"
    assert manifest["request"] == module.REQUEST
    assert manifest["holdout_evaluated"] is False
    assert json.loads(raw.read_text()) == envelope


@pytest.mark.parametrize("category", ["stock_splits", "mergers", "spinoffs", "future_provider_category"])
def test_nonempty_unmapped_categories_fail_closed(intake, category):
    module, envelope, raw, output = intake
    envelope["payload"][category] = [{"symbol": "SPY", "date": "2024-03-15"}]
    write_raw(raw, envelope)
    with pytest.raises(module.IntakeError, match="UNRESOLVED_CORPORATE_ACTION_CATEGORY"):
        module.reconstruct_actions(raw_input=raw, output=output)
    assert not output.exists()
    assert not output.with_suffix(".manifest.json").exists()


@pytest.mark.parametrize(
    "record",
    [
        {"symbol": "SPY"},
        {"symbol": "SPY", "ex_date": "bad-date"},
        {"symbol": "SPY", "ex_date": "20240315"},
        {"symbol": "SPY", "ex_date": "2026-04-10"},
        {"ex_date": "2024-03-15"},
        {"symbol": "AAPL", "ex_date": "2024-03-15"},
        "malformed-record",
    ],
)
def test_missing_invalid_or_out_of_scope_economic_fields_fail_closed(intake, record):
    module, envelope, raw, output = intake
    envelope["payload"]["cash_dividends"] = [record]
    write_raw(raw, envelope)
    with pytest.raises(module.IntakeError):
        module.reconstruct_actions(raw_input=raw, output=output)
    assert not output.exists()


def test_request_provenance_must_match_development_scope(intake):
    module, envelope, raw, output = intake
    envelope["request"]["end"] = "2026-04-10"
    write_raw(raw, envelope)
    with pytest.raises(module.IntakeError, match="REQUEST_PROVENANCE_MISMATCH"):
        module.reconstruct_actions(raw_input=raw, output=output)


@pytest.mark.parametrize("target", ["csv", "manifest", "raw"])
def test_never_overwrite_existing_outputs_or_call_provider(intake, monkeypatch, target):
    module, _, raw, output = intake
    path = {"csv": output, "manifest": output.with_suffix(".manifest.json"), "raw": raw}[target]
    path.write_text("preserve-existing-bytes")
    monkeypatch.setattr(module, "_fetch_envelope", lambda: pytest.fail("No request before overwrite guard"))
    with pytest.raises(module.IntakeError, match="OUTPUT_ALREADY_EXISTS"):
        module.reconstruct_actions(fetch=True, raw_output=raw, output=output)
    assert path.read_text() == "preserve-existing-bytes"


def test_fetch_requires_process_credentials_and_does_not_load_dotenv(intake, monkeypatch):
    module, _, raw, output = intake
    for pair in module.CREDENTIAL_PAIRS:
        for name in pair:
            monkeypatch.delenv(name, raising=False)
    (raw.parent / ".env").write_text("APCA_API_KEY_ID=toy\nAPCA_API_SECRET_KEY=toy\n")
    with pytest.raises(module.IntakeError, match="MISSING_PROCESS_CREDENTIAL_PAIR"):
        module.reconstruct_actions(fetch=True, raw_output=raw, output=output)
    assert not raw.exists()


def test_fetch_raw_envelope_retained_when_normalization_blocked(intake, monkeypatch):
    module, envelope, raw, output = intake
    envelope["payload"]["unresolved_category"] = [{"date": "2024-03-15"}]
    monkeypatch.setattr(module, "_fetch_envelope", lambda: envelope)
    with pytest.raises(module.IntakeError, match="UNRESOLVED_CORPORATE_ACTION_CATEGORY"):
        module.reconstruct_actions(fetch=True, raw_output=raw, output=output)
    assert json.loads(raw.read_text()) == envelope
    assert not output.exists()


def test_cli_unexpected_errors_sanitized(intake, monkeypatch, capsys):
    module, _, raw, output = intake
    secret = "never-display-this-value"

    def unsafe_error(**kwargs):
        raise RuntimeError(secret)

    monkeypatch.setattr(module, "reconstruct_actions", unsafe_error)
    assert module.main(["--raw-input", str(raw), "--output", str(output)]) == 2
    assert secret not in capsys.readouterr().out


def test_import_has_no_file_or_argument_side_effects(monkeypatch):
    load_module()

    def forbidden(*args, **kwargs):
        pytest.fail("Import must not read credential/data files or parse arguments")

    import argparse

    monkeypatch.setattr(Path, "read_text", forbidden)
    monkeypatch.setattr(Path, "mkdir", forbidden)
    monkeypatch.setattr(argparse.ArgumentParser, "parse_args", forbidden)
    load_module()


@pytest.mark.parametrize("failure", [False, True])
def test_fetch_uses_raw_all_category_request_and_sanitizes_provider_errors(intake, monkeypatch, failure):
    module, envelope, raw, output = intake
    from alpaca.data.historical import corporate_actions

    monkeypatch.setenv("APCA_API_KEY_ID", "fixture-key")
    monkeypatch.setenv("APCA_API_SECRET_KEY", "fixture-secret")
    calls = []

    class FakeClient:
        def __init__(self, key, secret, raw_data):
            assert (key, secret, raw_data) == ("fixture-key", "fixture-secret", True)

        def get_corporate_actions(self, request):
            calls.append(request)
            if failure:
                raise RuntimeError("provider body exposes fixture-secret")
            return envelope["payload"]

    monkeypatch.setattr(corporate_actions, "CorporateActionsClient", FakeClient)
    if failure:
        with pytest.raises(module.IntakeError) as error:
            module.reconstruct_actions(fetch=True, raw_output=raw, output=output)
        assert str(error.value) == "CORPORATE_ACTION_PROVIDER_REQUEST_FAILED"
        assert not raw.exists()
    else:
        result = module.reconstruct_actions(fetch=True, raw_output=raw, output=output)
        assert result["rows"] == 1
        assert json.loads(raw.read_text())["request"] == module.REQUEST
    request = calls[0]
    assert request.symbols == ["SPY", "QQQ"]
    assert str(request.start)[:10] == "2023-01-03"
    assert str(request.end)[:10] == "2026-04-09"
    assert request.types is None and request.limit is None


def test_prestart_economic_date_retained_and_annotated(intake):
    module, envelope, raw, output = intake
    envelope["payload"]["cash_dividends"].append(
        {
            "symbol": "SPY",
            "ex_date": "2022-12-16",
            "process_date": "2023-01-31",
            "payable_date": "2023-01-31",
        }
    )
    write_raw(raw, envelope)
    result = module.reconstruct_actions(raw_input=raw, output=output)
    manifest = json.loads(Path(result["manifest"]).read_text())
    assert result["rows"] == 2
    assert "SPY,2022-12-16,cash_dividends" in output.read_text()
    assert manifest["development_economic_date_rows"] == 1
    assert manifest["out_of_requested_economic_range_count"] == 1
    assert manifest["out_of_requested_economic_range"] == [
        {"symbol": "SPY", "date": "2022-12-16", "kind": "cash_dividends"}
    ]
