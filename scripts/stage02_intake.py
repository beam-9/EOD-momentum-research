import os
import json
import shlex
import argparse
from datetime import datetime, timezone
import polars as pl
from eod_momentum.common import ROOT, config, dump, sha
from eod_momentum.data import fetch, audit, credential_check, CREDENTIAL_PAIRS
from eod_momentum.calendar import sessions, expected_minutes, latest_completed
from eod_momentum.research import protocol_status

p = argparse.ArgumentParser()
p.add_argument("--acquire", action="store_true")
args = p.parse_args()
out = ROOT / "reports/evidence" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ_local02")
out.mkdir(parents=True)
(ROOT / "reports/evidence/CURRENT_SESSION").write_text(out.name + "\n")
protected = {
    str(p.relative_to(ROOT)): sha(p)
    for d in ["results", "data", "experiments", "config", "src", "tests", "scripts"]
    for p in (ROOT / d).rglob("*")
    if p.is_file() and p.name != ".DS_Store" and "__pycache__" not in p.parts
}
dump(out / "preservation_before.json", protected)
cfg = config()
assert protocol_status(cfg) == "PRE_REGISTERED"
day = "2024-03-08"
assert day < cfg["holdout_start"]
status = {
    "started_at_utc": datetime.now(timezone.utc).isoformat(),
    "request_date": day,
    "symbols": cfg["symbols"],
    "requested_feed": cfg["feed"],
    "adjustment": "raw",
    "holdout_boundary": cfg["holdout_start"],
    "holdout_evaluated": False,
    "credentials_source": "LOCAL_IGNORED_DOTENV_EXPLICIT_LOAD",
    "credential_values_logged": False,
    "provider_request_attempted": False,
    "acquisition_requested": args.acquire,
}
try:
    allowed = {n for pair in CREDENTIAL_PAIRS for n in pair}
    for line in (ROOT / ".env").read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:]
        name, sep, value = line.partition("=")
        if name.strip() in allowed and sep:
            pieces = shlex.split(value, comments=True)
            if len(pieces) > 1:
                raise ValueError("Invalid credential assignment format")
            os.environ[name.strip()] = pieces[0] if pieces else ""
    status["credential_pair_present"] = credential_check()["credential_pair_present"]
    if not status["credential_pair_present"]:
        raise ValueError("MISSING_LOCAL_CREDENTIAL_PAIR")
    status["provider_request_attempted"] = True
    f = fetch(cfg, day, day, persist_result=False, fresh_request=True)
    status["probe_request_succeeded"] = True
    f.write_parquet(out / "probe_bars.parquet")
    quality, valid = audit(f, day, day, cfg["symbols"])
    dump(out / "probe_quality.json", quality)
    expected = set(expected_minutes(sessions(day, day)[0]))
    coverage = {}
    for sym in cfg["symbols"]:
        g = f.filter(pl.col("symbol") == sym)
        stamps = set(g["timestamp_utc"].to_list())
        coverage[sym] = {
            "all_returned_rows": g.height,
            "first_timestamp_utc": str(g["timestamp_utc"].min()),
            "last_timestamp_utc": str(g["timestamp_utc"].max()),
            "rth_expected_minutes": len(expected),
            "rth_returned_minutes": len(stamps & expected),
            "rth_missing_minutes": len(expected - stamps),
            "duplicates": g.height - len(stamps),
            "timezone": str(g["timestamp_utc"].dtype),
        }
    status.update(
        status="AUTHENTICATED_SIP_REQUEST_SUCCEEDED",
        symbols_coverage=coverage,
        probe_data_sha256=sha(out / "probe_bars.parquet"),
        probe_quality_pass=all(q["status"] == "PASS" for q in quality),
        feed_evidence="Explicit SIP route accepted; SDK does not independently echo feed field",
        availability="ASSUMED_MINUTE_END_PLUS_30_SECONDS",
        execution="FILL_PROXY_ONLY",
    )
    if args.acquire:
        if not status["probe_quality_pass"]:
            raise ValueError("PROBE_QUALITY_GATE_FAILED")
        status["full_acquisition_started"] = True
        dump(out / "access_and_acquisition.json", status)
        full = fetch(cfg)
        status.update(
            full_acquisition_succeeded=True,
            full_rows=full.height,
            full_data_sha256=sha(ROOT / "data/processed/underlying.parquet"),
            latest_completed=latest_completed(),
        )
        dev_end = "2026-04-09"
        dev = full.filter(pl.col("bar_start_et").dt.date().cast(pl.String) < cfg["holdout_start"])
        dq, valid = audit(dev, cfg["start"], dev_end, cfg["symbols"])
        dump(out / "development_quality.json", dq)
        counts = {
            sym: {
                "development_returned_rows": dev.filter(pl.col("symbol") == sym).height,
                "pass_sessions": sum(x["status"] == "PASS" and x["symbol"] == sym for x in dq),
                "excluded_sessions": sum(x["status"] != "PASS" and x["symbol"] == sym for x in dq),
            }
            for sym in cfg["symbols"]
        }
        status["development_coverage"] = counts
except Exception as exc:
    status.update(status="ACCESS_OR_ACQUISITION_BLOCKED", error_type=type(exc).__name__)
    if isinstance(exc, RuntimeError) and str(exc).startswith("ALPACA_ACCESS_FAILED"):
        status["safe_error"] = str(exc)
    elif isinstance(exc, ValueError) and str(exc) in [
        "MISSING_LOCAL_CREDENTIAL_PAIR",
        "PROBE_QUALITY_GATE_FAILED",
        "Invalid credential assignment format",
    ]:
        status["safe_error"] = str(exc)
finally:
    for pair in CREDENTIAL_PAIRS:
        for n in pair:
            os.environ.pop(n, None)
    dump(out / "access_and_acquisition.json", status)
    print(json.dumps({"evidence_directory": str(out), **status}, indent=2))

# Fail a batch command when its access/acquisition gate did not pass.
raise SystemExit(0 if status.get("status") == "AUTHENTICATED_SIP_REQUEST_SUCCEEDED" else 2)
