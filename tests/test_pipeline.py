import json

import polars as pl
import pytest

from conftest import synthetic
from eod_momentum.common import sha
from eod_momentum.data import import_bars, persist
from eod_momentum.holdout import freeze
from eod_momentum.research import run


def test_parquet_duckdb_and_import(bars, cfg, tmp_path, monkeypatch):
    import eod_momentum.data as module
    monkeypatch.setattr(module, 'ROOT', tmp_path)
    p = persist(bars, 'fixture', {'status': 'SYNTHETIC_TEST_ONLY'})
    assert pl.read_parquet(p).height == bars.height
    with pytest.raises(ValueError, match='Synthetic'):
        import_bars(p, cfg, source='TEST', feed='TEST')
    manifest = json.loads((tmp_path / 'data/manifests/fixture.json').read_text())
    assert manifest['sha256'] == sha(p)


def test_no_data_report_has_no_profitability(cfg, tmp_path):
    out = run(cfg, out=tmp_path / 'no_data')
    m = json.loads((out / 'metrics.json').read_text())
    assert m['performance'] is None
    assert 'NO_REAL_HISTORICAL_BACKTEST' in (out / 'RESEARCH_REPORT.md').read_text()
    assert pl.read_parquet(out / 'trades.parquet').height == 0
    assert not list((out / 'charts').glob('*.png'))
    assert 'INCONCLUSIVE' in (out / 'robustness_scorecard.csv').read_text()
    with pytest.raises(ValueError, match='synthetic/absent'):
        freeze(cfg, out, tmp_path / 'seal.json')


def test_synthetic_refused_as_real(bars, cfg, tmp_path):
    with pytest.raises(ValueError, match='Synthetic'):
        run(cfg, frame=bars, out=tmp_path / 'bad')


def test_full_chronological_fixture_pipeline(cfg, tmp_path):
    # Shorter calendar windows are TEST ONLY; actual pre-registered production stays 12/3/3.
    cfg.update(start='2023-01-03', holdout_start='2023-06-01', train_months=1,
               validation_months=1, test_months=1, bootstrap_samples=25,
               null_seeds=5, min_session_coverage=0.85)
    bars = synthetic('2023-01-03', '2023-06-09', ('SPY', 'QQQ'))
    first = run(cfg, frame=bars, out=tmp_path / 'full', fixture=True)
    daily = pl.read_csv(first / 'daily_pnl.csv')
    assert daily.height > 0
    assert daily['date'].max() < '2023-06-01'
    assert daily.select(pl.struct(['symbol', 'date', 'strategy', 'cost_bps_side']).is_duplicated().any()).item() is False
    assert len(daily['strategy'].unique()) == 15
    summary = json.loads((first / 'metrics.json').read_text())
    assert len(summary) == 15 * 2 * 4
    assert 'SYNTHETIC_TEST_ONLY' in (first / 'RESEARCH_REPORT.md').read_text()
    assert json.loads((first / 'reconciliation_report.json').read_text())['status'] == 'PASS'
    assert len(list((first / 'charts').glob('*.png'))) == 8
    # Randomize sealed holdout prices; all earlier outputs must remain identical.
    modified = bars.with_columns(pl.when(pl.col('bar_start_et').dt.date().cast(pl.String) >= '2023-06-01')
                                 .then(pl.col('close') * 100).otherwise(pl.col('close')).alias('close'))
    second = run(cfg, frame=modified, out=tmp_path / 'replay', fixture=True)
    for filename in ['daily_pnl.csv', 'metrics.json', 'model_ledger.csv', 'stress_tests.csv',
                     'execution_cost_frontier.csv', 'joint_date_bootstrap.json', 'null_controls.csv']:
        assert sha(first / filename) == sha(second / filename), filename
    # Future test outcomes cannot change thresholds selected on earlier validation dates.
    ledger = pl.read_csv(first / 'model_ledger.csv')
    assert ledger.height > 0
    assert (first / 'trials.jsonl').exists()
    with pytest.raises(ValueError, match='synthetic/absent'):
        freeze(cfg, first, tmp_path / 'seal.json')
