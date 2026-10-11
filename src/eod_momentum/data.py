"""Read-only source adapters and strict canonical bar validation."""
from __future__ import annotations

import hashlib
import json
import os
import time
from tempfile import TemporaryDirectory
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import duckdb
import polars as pl

from .calendar import expected_minutes, latest_completed, sessions
from .common import ET, ROOT, digest, dump, sha, utcnow

REQUIRED = ['symbol', 'timestamp_utc', 'open', 'high', 'low', 'close', 'volume']
DT = pl.Datetime('us', 'UTC')
CREDENTIAL_PAIRS = [('APCA_API_KEY_ID', 'APCA_API_SECRET_KEY'), ('ALPACA_API_KEY', 'ALPACA_SECRET_KEY')]


def normalize(frame, *, source, feed, synthetic=False, delay_seconds=30, retrieved_at=None):
    if delay_seconds < 0:
        raise ValueError('Negative publication delay')
    if set(REQUIRED) - set(frame.columns):
        raise ValueError(f'Missing columns: {sorted(set(REQUIRED) - set(frame.columns))}')
    if source.strip() == '' or feed.strip() == '':
        raise ValueError('Source/feed required')
    f = frame.clone()
    for name in ['timestamp_utc', 'first_available_at_utc', 'revision_available_at_utc']:
        if name in f.columns:
            if f[name].dtype == pl.String:
                nonnull = f[name].drop_nulls().to_list()
                if any(not (v.endswith('Z') or '+' in v[10:]) for v in nonnull):
                    raise ValueError(f'Ambiguous timezone in {name}')
                f = f.with_columns(pl.col(name).str.to_datetime(time_zone='UTC').cast(DT))
            else:
                if not isinstance(f[name].dtype, pl.Datetime) or f[name].dtype.time_zone is None:
                    raise ValueError(f'Ambiguous timezone in {name}')
                f = f.with_columns(pl.col(name).dt.convert_time_zone('UTC').cast(DT))
    f = f.with_columns([pl.col(n).cast(pl.Float64) for n in ['open', 'high', 'low', 'close', 'volume']])
    if f.select(pl.any_horizontal(pl.col(REQUIRED).is_null()).any()).item():
        raise ValueError('Null required field')
    if f.select(pl.struct(['symbol', 'timestamp_utc']).is_duplicated().any()).item():
        raise ValueError('Duplicate bars')
    for symbol in f['symbol'].unique():
        if not f.filter(pl.col('symbol') == symbol)['timestamp_utc'].is_sorted():
            raise ValueError('Nonmonotonic source bars')
    if f.filter(~pl.all_horizontal([pl.col(n).is_finite() for n in REQUIRED[2:]])).height:
        raise ValueError('Nonfinite price/volume')
    if f.filter((pl.min_horizontal('open', 'high', 'low', 'close') <= 0) |
                (pl.col('volume') < 0) | (pl.col('high') < pl.max_horizontal('open', 'close')) |
                (pl.col('low') > pl.min_horizontal('open', 'close')) |
                (pl.col('low') > pl.col('high'))).height:
        raise ValueError('Invalid OHLC/volume')
    if f.filter((pl.col('timestamp_utc').dt.second() != 0) |
                (pl.col('timestamp_utc').dt.microsecond() != 0)).height:
        raise ValueError('Expected exact minute-start timestamps')
    for name in ['first_available_at_utc', 'revision_available_at_utc']:
        if name not in f.columns:
            f = f.with_columns(pl.lit(None, dtype=DT).alias(name))
    f = f.with_columns(
        pl.col('timestamp_utc').dt.convert_time_zone('America/New_York').alias('bar_start_et'),
        (pl.col('timestamp_utc') + pl.duration(minutes=1)).alias('bar_end_utc'),
        pl.lit(source).alias('source'), pl.lit(feed).alias('feed'),
        pl.lit(synthetic).alias('synthetic'), pl.lit(False).alias('is_adjusted'),
        pl.lit(retrieved_at or utcnow(), dtype=DT).alias('retrieved_at'),
        pl.lit('FINALIZED_BAR;FILL_PROXY_ONLY').alias('quality_flags'))
    f = f.with_columns(
        pl.col('bar_end_utc').dt.convert_time_zone('America/New_York').alias('bar_end_et'),
        pl.when(pl.col('first_available_at_utc').is_null())
        .then(pl.col('bar_end_utc') + pl.duration(seconds=delay_seconds)).otherwise(None)
        .cast(DT).alias('assumed_available_at_utc'),
        pl.when(pl.col('first_available_at_utc').is_null()).then(pl.lit('ASSUMED_FINAL_BAR'))
        .otherwise(pl.lit('OBSERVED_RECEIPT')).alias('availability_basis'))
    if f.filter(pl.col('first_available_at_utc') < pl.col('bar_end_utc')).height:
        raise ValueError('Bar available before economic end')
    if f.filter(pl.col('revision_available_at_utc') < pl.col('first_available_at_utc')).height:
        raise ValueError('Reversed revision availability')
    return f.sort(['symbol', 'timestamp_utc'])


def audit(frame, start, end, symbols):
    """Report every expected session, including entirely absent ones; no imputation."""
    rows = frame.with_columns(pl.col('bar_start_et').dt.date().cast(pl.String).alias('date'))
    groups = {(k[0], k[1]): g for k, g in rows.group_by(['symbol', 'date'], maintain_order=True)}
    report, valid = [], {}
    for s in sessions(start, end):
        for symbol in symbols:
            g = groups.get((symbol, s['date']))
            reasons = []
            if s['early']:
                reasons.append('EARLY_CLOSE')
            expected = set(expected_minutes(s))
            if g is None:
                reasons.append('MISSING_SESSION')
                count = 0
            else:
                g = g.filter((pl.col('timestamp_utc') >= s['open']) &
                             (pl.col('timestamp_utc') < s['close']))
                count = g.height
                if set(g['timestamp_utc'].to_list()) != expected:
                    reasons.append('MISSING_MINUTES')
                if count and (g['volume'] <= 0).any():
                    reasons.append('ZERO_VOLUME_OR_HALT')
            report.append({'symbol': symbol, 'date': s['date'], 'bars': count,
                           'expected_bars': len(expected), 'status': 'EXCLUDED' if reasons else 'PASS',
                           'reasons': reasons})
            if not reasons:
                valid[(symbol, s['date'])] = g
    return report, valid


def credential_check():
    names = next((p for p in CREDENTIAL_PAIRS if all(os.getenv(n) for n in p)), None)
    return {'source': 'alpaca', 'credential_pair_present': bool(names),
            'credential_values_logged': False, 'feed_entitlement': 'UNVERIFIED',
            'checked_at_utc': utcnow().isoformat()}


def client():
    from alpaca.data.historical import StockHistoricalDataClient
    names = next((p for p in CREDENTIAL_PAIRS if all(os.getenv(n) for n in p)), None)
    if names is None:
        raise ValueError('MISSING_CREDENTIALS: APCA_API_KEY_ID + APCA_API_SECRET_KEY')
    key, secret = (os.getenv(n) for n in names)
    return StockHistoricalDataClient(key, secret)


def fetch(cfg, start=None, end=None, *, persist_result=True, fresh_request=False):
    """SDK auto-pagination, immutable monthly checkpoints, bounded retries.

    Fresh requests are read-only entitlement probes: each call writes a unique raw
    evidence namespace and never replaces the production normalized dataset.
    """
    import pandas as pd
    from alpaca.data.enums import Adjustment, DataFeed
    from alpaca.data.requests import StockBarsRequest
    from alpaca.data.timeframe import TimeFrame

    c = client()
    start = start or cfg['start']
    end = min(end or latest_completed(), latest_completed())
    last = pd.Timestamp(end) + pd.Timedelta(days=1)
    edges = [pd.Timestamp(start)]
    while edges[-1] < last:
        edges.append(min(edges[-1] + pd.offsets.MonthBegin(1), last))
    frames = []
    raw_root = ROOT / 'data/raw/alpaca'
    if fresh_request:
        raw_root = raw_root / 'probes' / uuid4().hex
    for left, right in zip(edges, edges[1:]):
        request = {'symbols': cfg['symbols'], 'start': str(left.date()), 'end_exclusive': str(right.date()),
                   'feed': cfg['feed'], 'adjustment': 'raw', 'timeframe': '1Min'}
        path = raw_root / (digest(request) + '.json')
        if fresh_request or not path.exists():
            req = StockBarsRequest(symbol_or_symbols=cfg['symbols'], timeframe=TimeFrame.Minute,
                                   start=left.tz_localize(ET).to_pydatetime(),
                                   end=(right.tz_localize(ET) - pd.Timedelta(microseconds=1)).to_pydatetime(),
                                   feed=DataFeed(cfg['feed']), adjustment=Adjustment.RAW)
            for attempt in range(4):
                try:
                    bars = c.get_stock_bars(req)
                    break
                except Exception as exc:
                    status = getattr(exc, 'status_code', None)
                    if status not in [429, 500, 502, 503, 504] or attempt == 3:
                        raise RuntimeError(f'ALPACA_ACCESS_FAILED status={status}; no credentials logged') from None
                    time.sleep(2 ** attempt)
            records = [{'symbol': sym, 'timestamp_utc': b.timestamp.isoformat(), 'open': b.open,
                        'high': b.high, 'low': b.low, 'close': b.close, 'volume': b.volume}
                       for sym, values in bars.data.items() for b in values]
            records.sort(key=lambda r: (r['symbol'], r['timestamp_utc']))
            # SDK model serialization retains original vendor fields, no authentication headers.
            dump(path, {'request': request, 'retrieved_at': utcnow().isoformat(),
                        'vendor_payload': bars.model_dump(mode='json') if hasattr(bars, 'model_dump')
                        else bars.dict(), 'bars': records})
        obj = json.loads(path.read_text())
        if obj['bars']:
            frames.append(normalize(pl.DataFrame(obj['bars']), source='alpaca', feed=cfg['feed'],
                                    delay_seconds=cfg['publication_delay_seconds'],
                                    retrieved_at=datetime.fromisoformat(obj['retrieved_at'])))
    if not frames:
        raise ValueError('NO_BARS_RETURNED')
    f = pl.concat(frames).sort(['symbol', 'timestamp_utc'])
    if persist_result and not fresh_request:
        persist(f, 'underlying', {'source': 'alpaca', 'feed': cfg['feed'], 'start': start, 'end': end,
                                 'raw_hashes': {str(p): sha(p) for p in (ROOT / 'data/raw/alpaca').glob('*.json')}})
    return f


def _retain_snapshot(path, content):
    """Create once; an existing content-addressed artifact must match exactly."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise ValueError('Snapshot integrity failure: symbolic link')
    try:
        with path.open('xb') as fh:
            fh.write(content)
    except FileExistsError:
        if path.read_bytes() != content:
            raise ValueError('Snapshot integrity failure: existing contents differ') from None


def _archive_dataset(name, content, manifest_content=None):
    data_hash = hashlib.sha256(content).hexdigest()
    data_path = ROOT / f'data/processed/snapshots/{name}/{data_hash}.parquet'
    _retain_snapshot(data_path, content)
    manifest_path = None
    if manifest_content is not None:
        manifest = json.loads(manifest_content)
        if manifest.get('sha256') != data_hash:
            raise ValueError('Active manifest does not match dataset')
        manifest_hash = hashlib.sha256(manifest_content).hexdigest()
        manifest_path = ROOT / f'data/manifests/snapshots/{name}/{data_hash}/{manifest_hash}.json'
        _retain_snapshot(manifest_path, manifest_content)
    return {'data_path': str(data_path.relative_to(ROOT)), 'sha256': data_hash,
            'manifest_path': str(manifest_path.relative_to(ROOT)) if manifest_path else None,
            'provenance_status': 'RETAINED' if manifest_path else 'UNKNOWN_MISSING_MANIFEST'}


def persist(frame, name, provenance):
    """Retain immutable versions, then replace the existing active dataset interface.

    A legacy dataset without a manifest is retained with explicitly unknown
    provenance; its historical provenance is never reconstructed or invented.
    """
    path = ROOT / f'data/processed/{name}.parquet'
    manifest_path = ROOT / f'data/manifests/{name}.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=path.parent, prefix='.persist-') as temporary:
        staged = Path(temporary) / 'dataset.parquet'
        frame.write_parquet(staged)
        # Validate the replacement before touching the active dataset.
        with duckdb.connect() as conn:
            count = conn.execute('SELECT count(*) FROM read_parquet(?)', [str(staged)]).fetchone()[0]
            if count != frame.height:
                raise ValueError('Parquet SQL reconciliation failed')
        previous = None
        if path.exists():
            previous = _archive_dataset(name, path.read_bytes(),
                                        manifest_path.read_bytes() if manifest_path.exists() else None)
        elif manifest_path.exists():
            raise ValueError('Active manifest exists without dataset')
        data_hash = sha(staged)
        record = {**provenance, 'sha256': data_hash, 'rows': frame.height,
                  'snapshot_data_path': f'data/processed/snapshots/{name}/{data_hash}.parquet',
                  'previous_snapshot': previous}
        staged_manifest = Path(temporary) / 'manifest.json'
        dump(staged_manifest, record)
        _archive_dataset(name, staged.read_bytes(), staged_manifest.read_bytes())
        staged.replace(path)
        staged_manifest.replace(manifest_path)
    return path


def import_bars(path, cfg, source, feed):
    path = Path(path)
    f = pl.read_parquet(path) if path.suffix == '.parquet' else pl.read_csv(path)
    if 'is_adjusted' in f.columns and f['is_adjusted'].any():
        raise ValueError('Raw prices required; adjusted import is not transaction history')
    if 'synthetic' in f.columns and f['synthetic'].any():
        raise ValueError('Synthetic data cannot be imported into real-data storage')
    raw = ROOT / 'data/raw/import' / (sha(path) + path.suffix)
    raw.parent.mkdir(parents=True, exist_ok=True)
    if not raw.exists():
        raw.write_bytes(path.read_bytes())
    f = normalize(f, source=source, feed=feed, delay_seconds=cfg['publication_delay_seconds'])
    persist(f, 'underlying', {'source': source, 'feed': feed, 'raw_hash': sha(raw),
                             'bar_timestamp_convention': 'UTC_MINUTE_START', 'adjustment': 'raw',
                             'permission': 'USER_SUPPLIED_LICENSED_IMPORT'})
    return f
