"""Explicit, import-safe Stage 02 intake; never run research or inspect holdout outcomes."""

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shlex

import polars as pl

from eod_momentum.calendar import expected_minutes, latest_completed, sessions
from eod_momentum.common import ROOT, config, dump, sha
from eod_momentum.data import CREDENTIAL_PAIRS, audit, credential_check, fetch
from eod_momentum.research import protocol_status

_PROBE_DAY = "2024-03-08"
_CREDENTIAL_NAMES = frozenset(name for pair in CREDENTIAL_PAIRS for name in pair)


@contextmanager
def _local_credentials(path):
    """Load recognized assignments without shell execution; restore exact prior values."""
    original = {name: os.environ.get(name) for name in _CREDENTIAL_NAMES}
    try:
        if path.exists():
            for line in path.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("export "):
                    line = line[7:]
                name, sep, value = line.partition("=")
                name = name.strip()
                if name not in _CREDENTIAL_NAMES or not sep:
                    continue
                try:
                    pieces = shlex.split(value, comments=True)
                except ValueError:
                    raise ValueError("INVALID_CREDENTIAL_ASSIGNMENT") from None
                if len(pieces) > 1:
                    raise ValueError("INVALID_CREDENTIAL_ASSIGNMENT")
                os.environ[name] = pieces[0] if pieces else ""
        yield
    finally:
        for name, value in original.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


def _preservation_snapshot(root):
    return {
        str(path.relative_to(root)): sha(path)
        for directory in ["results", "data", "experiments", "config", "src", "tests", "scripts"]
        for path in (root / directory).rglob("*")
        if path.is_file() and path.name != ".DS_Store" and "__pycache__" not in path.parts
    }


def _probe_coverage(frame, symbols):
    expected = set(expected_minutes(sessions(_PROBE_DAY, _PROBE_DAY)[0]))
    coverage = {}
    for symbol in symbols:
        group = frame.filter(pl.col("symbol") == symbol)
        stamps = set(group["timestamp_utc"].to_list())
        coverage[symbol] = {
            "all_returned_rows": group.height,
            "first_timestamp_utc": str(group["timestamp_utc"].min()),
            "last_timestamp_utc": str(group["timestamp_utc"].max()),
            "rth_expected_minutes": len(expected),
            "rth_returned_minutes": len(stamps & expected),
            "rth_missing_minutes": len(expected - stamps),
            "duplicates": group.height - len(stamps),
            "timezone": str(group["timestamp_utc"].dtype),
        }
    return coverage


def _development_audit(full, cfg, out):
    dev = full.filter(pl.col("bar_start_et").dt.date().cast(pl.String) < cfg["holdout_start"])
    quality, _ = audit(dev, cfg["start"], "2026-04-09", cfg["symbols"])
    dump(out / "development_quality.json", quality)
    return {
        symbol: {
            "development_returned_rows": dev.filter(pl.col("symbol") == symbol).height,
            "pass_sessions": sum(row["status"] == "PASS" and row["symbol"] == symbol for row in quality),
            "excluded_sessions": sum(row["status"] != "PASS" and row["symbol"] == symbol for row in quality),
        }
        for symbol in cfg["symbols"]
    }


def run_intake(*, root=ROOT, fetch_bars=fetch, acquire=False):
    """Record a frozen SIP probe and optional acquisition; return sanitized status and evidence path.

    ``fetch_bars`` has the existing data.fetch calling convention. This is the actual
    provider I/O seam; callers can exercise intake without credentials or network access.
    Failures remain recorded evidence and are reported with fixed codes, never exception bodies.
    """
    root = Path(root)
    out = root / "reports/evidence" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ_local02")
    out.mkdir(parents=True)
    (root / "reports/evidence/CURRENT_SESSION").write_text(out.name + "\n")
    dump(out / "preservation_before.json", _preservation_snapshot(root))
    status = {
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "request_date": _PROBE_DAY,
        "adjustment": "raw",
        "holdout_evaluated": False,
        "credentials_source": "SUPPORTED_PROCESS_ENV_OR_LOCAL_IGNORED_DOTENV_EXPLICIT_LOAD",
        "credential_values_logged": False,
        "provider_request_attempted": False,
        "acquisition_requested": acquire,
    }
    try:
        cfg = config(root / "config/default.yaml")
        status.update(
            symbols=cfg["symbols"], requested_feed=cfg["feed"], holdout_boundary=cfg["holdout_start"]
        )
        if protocol_status(cfg) != "PRE_REGISTERED":
            raise ValueError("FROZEN_PROTOCOL_GATE_FAILED")
        if cfg["feed"] != "sip":
            raise ValueError("SIP_FEED_GATE_FAILED")
        if cfg["holdout_start"] != "2026-04-10" or _PROBE_DAY >= cfg["holdout_start"]:
            raise ValueError("SEALED_HOLDOUT_GATE_FAILED")
        with _local_credentials(root / ".env"):
            status["credential_pair_present"] = credential_check()["credential_pair_present"]
            if not status["credential_pair_present"]:
                raise ValueError("MISSING_LOCAL_CREDENTIAL_PAIR")
            status["provider_request_attempted"] = True
            frame = fetch_bars(cfg, _PROBE_DAY, _PROBE_DAY, persist_result=False, fresh_request=True)
            status["probe_request_succeeded"] = True
            frame.write_parquet(out / "probe_bars.parquet")
            quality, _ = audit(frame, _PROBE_DAY, _PROBE_DAY, cfg["symbols"])
            dump(out / "probe_quality.json", quality)
            coverage = _probe_coverage(frame, cfg["symbols"])
            status.update(
                symbols_coverage=coverage,
                probe_data_sha256=sha(out / "probe_bars.parquet"),
                probe_quality_pass=bool(quality) and all(row["status"] == "PASS" for row in quality),
                feed_evidence="Explicit SIP route accepted; SDK does not independently echo feed field",
                availability="ASSUMED_MINUTE_END_PLUS_30_SECONDS",
                execution="FILL_PROXY_ONLY",
            )
            if not status["probe_quality_pass"]:
                raise ValueError("PROBE_QUALITY_GATE_FAILED")
            if acquire:
                status["full_acquisition_started"] = True
                dump(out / "access_and_acquisition.json", status)
                full = fetch_bars(cfg)
                status.update(
                    full_acquisition_succeeded=True,
                    full_rows=full.height,
                    full_data_sha256=sha(root / "data/processed/underlying.parquet"),
                    latest_completed=latest_completed(),
                )
                status["development_coverage"] = _development_audit(full, cfg, out)
            status["status"] = "AUTHENTICATED_SIP_REQUEST_SUCCEEDED"
    except Exception as exc:
        status.update(status="ACCESS_OR_ACQUISITION_BLOCKED", error_type=type(exc).__name__)
        safe_codes = {
            "FROZEN_PROTOCOL_GATE_FAILED",
            "SIP_FEED_GATE_FAILED",
            "SEALED_HOLDOUT_GATE_FAILED",
            "MISSING_LOCAL_CREDENTIAL_PAIR",
            "PROBE_QUALITY_GATE_FAILED",
            "INVALID_CREDENTIAL_ASSIGNMENT",
        }
        if isinstance(exc, ValueError) and str(exc) in safe_codes:
            status["safe_error"] = str(exc)
    dump(out / "access_and_acquisition.json", status)
    return {"evidence_directory": str(out), **status}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acquire", action="store_true")
    args = parser.parse_args(argv)
    result = run_intake(acquire=args.acquire)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "AUTHENTICATED_SIP_REQUEST_SUCCEEDED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
