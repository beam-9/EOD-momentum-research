"""Mock-only credential/cache contracts; no network calls or real credentials."""
import json
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from eod_momentum import data
from eod_momentum.common import digest, sha
from eod_momentum.data import fetch


@pytest.fixture
def aliases_cleared(monkeypatch):
    for pair in data.CREDENTIAL_PAIRS:
        for name in pair:
            monkeypatch.delenv(name, raising=False)


@pytest.mark.parametrize('partial_primary', ['APCA_API_KEY_ID', 'APCA_API_SECRET_KEY'])
def test_client_uses_complete_secondary_pair_despite_partial_primary(monkeypatch, aliases_cleared,
                                                                  partial_primary):
    monkeypatch.setenv(partial_primary, 'MOCK_PARTIAL_PRIMARY')
    monkeypatch.setenv('ALPACA_API_KEY', 'MOCK_SECONDARY_KEY')
    monkeypatch.setenv('ALPACA_SECRET_KEY', 'MOCK_SECONDARY_SECRET')
    constructor = Mock()
    monkeypatch.setattr('alpaca.data.historical.StockHistoricalDataClient', constructor)
    assert data.credential_check()['credential_pair_present']
    assert data.client() is constructor.return_value
    constructor.assert_called_once_with('MOCK_SECONDARY_KEY', 'MOCK_SECONDARY_SECRET')


def test_client_prefers_complete_primary_pair(monkeypatch, aliases_cleared):
    for name, value in [('APCA_API_KEY_ID', 'MOCK_PRIMARY_KEY'),
                        ('APCA_API_SECRET_KEY', 'MOCK_PRIMARY_SECRET'),
                        ('ALPACA_API_KEY', 'MOCK_SECONDARY_KEY'),
                        ('ALPACA_SECRET_KEY', 'MOCK_SECONDARY_SECRET')]:
        monkeypatch.setenv(name, value)
    constructor = Mock()
    monkeypatch.setattr('alpaca.data.historical.StockHistoricalDataClient', constructor)
    data.client()
    constructor.assert_called_once_with('MOCK_PRIMARY_KEY', 'MOCK_PRIMARY_SECRET')


def test_client_rejects_cross_alias_partial_pair(monkeypatch, aliases_cleared):
    monkeypatch.setenv('APCA_API_KEY_ID', 'MOCK_PARTIAL_PRIMARY')
    monkeypatch.setenv('ALPACA_SECRET_KEY', 'MOCK_PARTIAL_SECONDARY')
    constructor = Mock()
    monkeypatch.setattr('alpaca.data.historical.StockHistoricalDataClient', constructor)
    assert not data.credential_check()['credential_pair_present']
    with pytest.raises(ValueError, match='MISSING_CREDENTIALS'):
        data.client()
    constructor.assert_not_called()


@pytest.fixture
def adapter_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(data, 'ROOT', tmp_path)
    monkeypatch.setattr(data, 'latest_completed', lambda: '2024-03-08')
    cfg = {'start': '2024-03-08', 'symbols': ['SPY'], 'feed': 'iex', 'publication_delay_seconds': 30}
    request = {'symbols': ['SPY'], 'start': '2024-03-08', 'end_exclusive': '2024-03-09',
               'feed': 'iex', 'adjustment': 'raw', 'timeframe': '1Min'}
    cached = tmp_path / 'data/raw/alpaca' / (digest(request) + '.json')
    record = {'symbol': 'SPY', 'timestamp_utc': '2024-03-08T14:30:00+00:00',
              'open': 100, 'high': 101, 'low': 99, 'close': 100, 'volume': 500}
    data.dump(cached, {'request': request, 'retrieved_at': '2024-03-09T00:00:00+00:00',
                       'vendor_payload': {'fixture': 'MOCK_ONLY'}, 'bars': [record]})
    processed = tmp_path / 'data/processed/underlying.parquet'
    manifest = tmp_path / 'data/manifests/underlying.json'
    for path in [processed, manifest]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'MOCK_PRODUCTION_SENTINEL; DO NOT REPLACE')
    fresh_bar = SimpleNamespace(timestamp=datetime(2024, 3, 8, 14, 30, tzinfo=timezone.utc),
                                open=200, high=201, low=199, close=200, volume=900)
    response = SimpleNamespace(data={'SPY': [fresh_bar]},
                               model_dump=lambda **_: {'fixture': 'FRESH_MOCK_ONLY'})
    sdk = Mock()
    sdk.get_stock_bars.return_value = response
    monkeypatch.setattr(data, 'client', lambda: sdk)
    persister = Mock(side_effect=AssertionError('Probe must preserve production normalized data'))
    monkeypatch.setattr(data, 'persist', persister)
    return SimpleNamespace(cfg=cfg, root=tmp_path, cached=cached, sdk=sdk, persister=persister,
                           preserved={p: p.read_bytes() for p in [cached, processed, manifest]})


@pytest.mark.parametrize('persist_result', [False, True])
def test_fresh_probe_bypasses_cache_preserves_production_and_retains_unique_evidence(adapter_cache,
                                                                                  persist_result):
    fixture = adapter_cache
    for _ in range(2):
        result = data.fetch(fixture.cfg, end='2024-03-08', persist_result=persist_result, fresh_request=True)
        assert result['close'].to_list() == [200]
    assert fixture.sdk.get_stock_bars.call_count == 2
    fixture.persister.assert_not_called()
    for path, original in fixture.preserved.items():
        assert path.read_bytes() == original
    evidence = sorted((fixture.root / 'data/raw/alpaca/probes').glob('*/*.json'))
    assert len(evidence) == 2
    assert evidence[0].parent != evidence[1].parent
    assert all(json.loads(path.read_text())['bars'][0]['close'] == 200 for path in evidence)


def test_default_fetch_resumes_from_existing_cache(adapter_cache):
    fixture = adapter_cache
    result = data.fetch(fixture.cfg, end='2024-03-08', persist_result=False)
    assert result['close'].to_list() == [100]
    fixture.sdk.get_stock_bars.assert_not_called()
    fixture.persister.assert_not_called()
    assert not (fixture.root / 'data/raw/alpaca/probes').exists()
    for path, original in fixture.preserved.items():
        assert path.read_bytes() == original


class FixtureClient:
    calls = 0

    def get_stock_bars(self, request):
        self.calls += 1
        row = SimpleNamespace(timestamp=datetime(2024, 3, 8, 14, 30, tzinfo=timezone.utc),
                              open=100., high=101., low=99., close=100., volume=1000)
        return SimpleNamespace(data={'SPY': [row]}, model_dump=lambda **kw: {'mock': 'TEST_ONLY'})


def test_cache_replay_identical_acquisition_time(tmp_path, cfg, monkeypatch):
    import eod_momentum.data as module
    c = FixtureClient()
    monkeypatch.setattr(module, 'ROOT', tmp_path)
    monkeypatch.setattr(module, 'client', lambda: c)
    monkeypatch.setattr(module, 'latest_completed', lambda: '2024-03-08')
    cfg['symbols'] = ['SPY']
    f = fetch(cfg, '2024-03-08', '2024-03-08')
    path = tmp_path / 'data/processed/underlying.parquet'
    checksum = sha(path)
    replay = fetch(cfg, '2024-03-08', '2024-03-08')
    assert c.calls == 1
    assert f.equals(replay)
    assert sha(path) == checksum


def test_read_only_probe_does_not_replace_history(tmp_path, cfg, monkeypatch):
    import eod_momentum.data as module
    c = FixtureClient()
    monkeypatch.setattr(module, 'ROOT', tmp_path)
    monkeypatch.setattr(module, 'client', lambda: c)
    monkeypatch.setattr(module, 'latest_completed', lambda: '2024-03-08')
    cfg['symbols'] = ['SPY']
    path = tmp_path / 'data/processed/underlying.parquet'
    path.parent.mkdir(parents=True)
    path.write_bytes(b'EXISTING_FULL_HISTORY_SENTINEL')
    previous = sha(path)
    sample = fetch(cfg, '2024-03-08', '2024-03-08', persist_result=False)
    assert sample.height == 1
    assert sha(path) == previous
