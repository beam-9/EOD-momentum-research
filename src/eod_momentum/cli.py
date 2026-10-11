from __future__ import annotations

import argparse
import json
import sys

import polars as pl

from .common import ROOT, config, dump
from .data import credential_check, fetch, import_bars
from .research import preregister, run


def parser():
    p = argparse.ArgumentParser(description='Reproducible research only; never places orders')
    p.add_argument('--config', default=str(ROOT / 'config/default.yaml'))
    subs = p.add_subparsers(dest='command', required=True)
    data = subs.add_parser('data').add_subparsers(dest='action', required=True)
    check = data.add_parser('check')
    check.add_argument('--source', choices=['alpaca'], default='alpaca')
    check.add_argument('--probe', action='store_true', help='Actual read-only one-session feed request')
    check.add_argument('--report-path', help='New access-check evidence path; refuses to overwrite')
    fetchp = data.add_parser('fetch')
    fetchp.add_argument('--start')
    fetchp.add_argument('--end')
    fetchp.add_argument('--symbols', nargs='+')
    fetchp.add_argument('--source', choices=['alpaca'], default='alpaca')
    imp = data.add_parser('import')
    imp.add_argument('--path', required=True)
    imp.add_argument('--source', required=True)
    imp.add_argument('--feed', required=True)
    imp.add_argument('--timestamp-convention', choices=['minute-start-utc'], required=True)
    opt = data.add_parser('import-options')
    opt.add_argument('--path', required=True)
    research = subs.add_parser('research').add_subparsers(dest='action', required=True)
    rp = research.add_parser('run')
    rp.add_argument('--phase', choices=['A', 'B', 'C', 'D'], default='A')
    research.add_parser('validate')
    subs.add_parser('replay')
    ho = subs.add_parser('holdout').add_subparsers(dest='action', required=True)
    freeze = ho.add_parser('freeze')
    freeze.add_argument('--run', required=True)
    ho.add_parser('evaluate')
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    cfg = config(args.config)
    preregister(cfg)
    try:
        if args.command == 'data':
            if args.action == 'check':
                from pathlib import Path
                report_path = (Path(args.report_path) if args.report_path else
                               ROOT / 'data/manifests/access_check.json')
                if args.report_path and report_path.exists():
                    raise FileExistsError('Access report already exists; choose a new report path')
                status = credential_check()
                path = ROOT / 'data/processed/underlying.parquet'
                status['local_bars_present'] = path.exists()
                if args.probe and status['credential_pair_present']:
                    from .calendar import latest_completed
                    f = fetch(cfg, latest_completed(), latest_completed(), persist_result=False,
                              fresh_request=True)
                    status.update(feed_entitlement='REQUEST_SUCCEEDED', returned_rows=f.height,
                                  requested_feed=cfg['feed'], probe_status='FRESH_REQUEST_SUCCEEDED')
                elif args.probe:
                    status['probe_status'] = 'NOT_SENT_MISSING_CREDENTIALS'
                dump(report_path, status)
                print(json.dumps(status, indent=2))
                return 0 if status['credential_pair_present'] or path.exists() else 2
            if args.action == 'fetch':
                if args.symbols:
                    cfg['symbols'] = args.symbols
                print(f'Acquired {fetch(cfg, args.start, args.end).height} bars')
                return 0
            if args.action == 'import':
                f = import_bars(args.path, cfg, args.source, args.feed)
                print(f'Imported {f.height} bars; timestamp convention explicitly declared')
                return 0
            if args.action == 'import-options':
                from .options import OPTION_FIELDS
                from .data import persist
                f = pl.read_parquet(args.path) if args.path.endswith('.parquet') else pl.read_csv(args.path)
                missing = set(OPTION_FIELDS) - set(f.columns)
                if missing:
                    raise ValueError(f'Missing option columns: {sorted(missing)}')
                # Import is storage only: typed as-of validation is mandatory before any later execution.
                persist(f, 'option_snapshots', {'source': 'USER_LICENSED_IMPORT', 'status': 'UNVALIDATED'})
                print('Stored unvalidated licensed option snapshots; no backtest claimed')
                return 0
        if args.command in ['replay', 'research']:
            path = ROOT / 'data/processed/underlying.parquet'
            if args.command == 'research' and args.action == 'validate':
                dirs = sorted((ROOT / 'results').glob('*/robustness_scorecard.csv'))
                if not dirs:
                    raise ValueError('No research run exists')
                print(dirs[-1].read_text())
                return 0
            if args.command == 'research' and args.phase == 'D':
                from .ibs_pipeline import run as run_ibs
                f = pl.read_parquet(path) if path.exists() else None
                print(run_ibs(cfg, frame=f))
                print('NO_REAL_HISTORICAL_BACKTEST' if f is None else 'INCONCLUSIVE_RESEARCH_ONLY')
                return 0
            if args.command == 'research' and args.phase != 'A':
                raise ValueError(f'PHASE_{args.phase}_DATA_GATE: see DATA_ACCESS_BLOCKERS.md. '
                                 'Only isolated utilities are verified; empirical phase runner requires '
                                 'fit-for-purpose point-in-time inputs and a separately frozen protocol.')
            f = pl.read_parquet(path) if path.exists() else None
            out = run(cfg, frame=f)
            print(out)
            print('NO_REAL_HISTORICAL_BACKTEST' if f is None else 'INCONCLUSIVE_RESEARCH_ONLY')
            return 0
        if args.command == 'holdout':
            from .holdout import evaluate, freeze
            print(freeze(cfg, args.run) if args.action == 'freeze' else evaluate(cfg))
            return 0
    except (ValueError, RuntimeError, FileNotFoundError, FileExistsError) as exc:
        print(f'BLOCKED: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
