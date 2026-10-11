"""Reconstruct development-only corporate-action exclusions without changing the research protocol."""

import argparse
import csv
from datetime import date, datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path

from eod_momentum.data import CREDENTIAL_PAIRS

REQUEST = {
    "symbols": ["SPY", "QQQ"],
    "start": "2023-01-03",
    "end": "2026-04-09",
    "types": "ALL",
    "limit": None,
}


class IntakeError(ValueError):
    """Fixed diagnostic code safe for display; never contains provider or credential values."""


def _normalize(envelope):
    if not isinstance(envelope, dict) or envelope.get("request") != REQUEST:
        raise IntakeError("REQUEST_PROVENANCE_MISMATCH")
    payload = envelope.get("payload")
    if not isinstance(payload, dict):
        raise IntakeError("INVALID_PAYLOAD")
    rows = []
    for category, records in payload.items():
        if not isinstance(records, list):
            raise IntakeError("INVALID_CATEGORY_RECORDS")
        if category != "cash_dividends":
            if records:
                raise IntakeError("UNRESOLVED_CORPORATE_ACTION_CATEGORY")
            continue
        for record in records:
            if not isinstance(record, dict):
                raise IntakeError("INVALID_CASH_DIVIDEND")
            symbol, ex_date = record.get("symbol"), record.get("ex_date")
            if not isinstance(symbol, str) or symbol not in REQUEST["symbols"]:
                raise IntakeError("INVALID_OR_OUT_OF_SCOPE_SYMBOL")
            try:
                economic_date = date.fromisoformat(ex_date)
            except (ValueError, TypeError):
                raise IntakeError("INVALID_ECONOMIC_DATE") from None
            if economic_date.isoformat() != ex_date:
                raise IntakeError("INVALID_ECONOMIC_DATE")
            # Provider request dates can match process/payable dates rather than ex_date.
            # Preserve earlier economic dates explicitly; never admit sealed-holdout actions.
            if ex_date > REQUEST["end"]:
                raise IntakeError("ECONOMIC_DATE_IN_SEALED_HOLDOUT")
            rows.append((symbol, ex_date, category))
    return sorted(rows)


def _fetch_envelope():
    """Read supported process credentials only. No dotenv loading and no order endpoints."""
    pair = next((pair for pair in CREDENTIAL_PAIRS if all(os.getenv(name) for name in pair)), None)
    if pair is None:
        raise IntakeError("MISSING_PROCESS_CREDENTIAL_PAIR")
    try:
        from alpaca.data.historical.corporate_actions import CorporateActionsClient
        from alpaca.data.requests import CorporateActionsRequest

        request = CorporateActionsRequest(
            symbols=REQUEST["symbols"],
            start=date.fromisoformat(REQUEST["start"]),
            end=date.fromisoformat(REQUEST["end"]),
            types=None,
            limit=None,
        )
        payload = CorporateActionsClient(
            os.environ[pair[0]], os.environ[pair[1]], raw_data=True
        ).get_corporate_actions(request)
    except Exception:
        raise IntakeError("CORPORATE_ACTION_PROVIDER_REQUEST_FAILED") from None
    return {
        "request": dict(REQUEST),
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }


def reconstruct_actions(*, output, raw_input=None, fetch=False, raw_output=None):
    """Write a new exclusion CSV and provenance manifest from preserved raw records.

    Unsupported action categories fail closed. Source records remain in the raw envelope;
    the CSV exposes only the frozen exclusion schema (symbol, date, kind).
    """
    output = Path(output)
    manifest_path = output.with_suffix(".manifest.json")
    if (raw_input is None) == (not fetch) or (fetch and raw_output is None) or (not fetch and raw_output):
        raise IntakeError("INVALID_INPUT_MODE")
    source_path = Path(raw_output if fetch else raw_input)
    targets = [output, manifest_path] + ([source_path] if fetch else [])
    if len({path.resolve() for path in targets}) != len(targets) or (
        not fetch and source_path.resolve() in {path.resolve() for path in targets}
    ):
        raise IntakeError("OUTPUT_PATH_COLLISION")
    if any(path.exists() for path in targets):
        raise IntakeError("OUTPUT_ALREADY_EXISTS")
    if any(not path.parent.is_dir() for path in targets):
        raise IntakeError("OUTPUT_PARENT_MISSING")
    if fetch:
        envelope = _fetch_envelope()
        raw_bytes = (json.dumps(envelope, indent=2, sort_keys=True) + "\n").encode()
        # Preserve the authentic response even when its categories cannot yet be normalized.
        with source_path.open("xb") as handle:
            handle.write(raw_bytes)
    else:
        raw_bytes = source_path.read_bytes()
        try:
            envelope = json.loads(raw_bytes)
        except (ValueError, UnicodeError):
            raise IntakeError("INVALID_RAW_JSON") from None
    rows = _normalize(envelope)
    text = io.StringIO(newline="")
    writer = csv.writer(text)
    writer.writerow(["symbol", "date", "kind"])
    writer.writerows(rows)
    csv_bytes = text.getvalue().encode()
    manifest = {
        "source": "ALPACA_V1_CORPORATE_ACTIONS_AUTHENTICATED" if fetch else "PRESERVED_ALPACA_RAW_ENVELOPE",
        "raw_path": str(source_path.resolve()),
        "raw_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "normalized_path": str(output.resolve()),
        "normalized_sha256": hashlib.sha256(csv_bytes).hexdigest(),
        "request": envelope["request"],
        "retrieved_at_utc": envelope.get("retrieved_at_utc", "UNKNOWN"),
        "rows": len(rows),
        "economic_date": "ex_date for observed cash_dividends",
        "out_of_requested_economic_range": [
            {"symbol": symbol, "date": economic_date, "kind": kind}
            for symbol, economic_date, kind in rows
            if economic_date < REQUEST["start"]
        ],
        "out_of_requested_economic_range_count": sum(
            economic_date < REQUEST["start"] for _, economic_date, _ in rows
        ),
        "development_economic_date_rows": sum(
            REQUEST["start"] <= economic_date <= REQUEST["end"] for _, economic_date, _ in rows
        ),
        "request_date_scope": "Provider request dates need not restrict economic ex_dates; earlier returned actions retained",
        "coverage_completeness": "UNKNOWN_INDEPENDENT_EXHAUSTIVENESS",
        "historical_publication_timestamps": "UNKNOWN",
        "unresolved": [],
        "credential_values_logged": False,
        "holdout_evaluated": False,
    }
    with output.open("xb") as handle:
        handle.write(csv_bytes)
    with manifest_path.open("x") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return {"output": str(output), "manifest": str(manifest_path), "rows": len(rows)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--raw-input", type=Path)
    mode.add_argument("--fetch", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--raw-output", type=Path)
    args = parser.parse_args(argv)
    try:
        result = reconstruct_actions(
            output=args.output, raw_input=args.raw_input, fetch=args.fetch, raw_output=args.raw_output
        )
    except IntakeError as exc:
        print(json.dumps({"status": "BLOCKED", "safe_error": str(exc)}))
        return 2
    except Exception:
        print(json.dumps({"status": "BLOCKED", "safe_error": "CORPORATE_ACTION_INTAKE_FAILED"}))
        return 2
    print(json.dumps({"status": "NORMALIZED_EXCLUSIONS_ONLY", **result}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
