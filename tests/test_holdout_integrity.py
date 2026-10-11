"""Unit tests use mock provenance only, never real holdout evidence."""

import pytest

from eod_momentum.common import code_hashes, digest, dump, external_hashes, sha
from eod_momentum.holdout import evaluate, freeze


def setup_seal(tmp_path, cfg, bars, monkeypatch):
    import eod_momentum.holdout as module
    monkeypatch.setattr(module, 'ROOT', tmp_path)
    data = tmp_path / 'data/processed/underlying.parquet'
    data.parent.mkdir(parents=True)
    bars.write_parquet(data)
    protocol = tmp_path / 'experiments/RESEARCH_PROTOCOL.md'
    protocol.parent.mkdir(parents=True)
    protocol.write_text('MOCK_PROTOCOL_UNIT_TEST_ONLY')
    seal = tmp_path / 'experiments/holdout_seal.json'
    dump(seal, {'code_hashes': code_hashes(), 'config_hash': digest(cfg), 'external_hashes': external_hashes(cfg),
                'data_hash': sha(data), 'protocol_hash': sha(protocol), 'holdout_start': cfg['holdout_start'],
                'end_inclusive': '2026-10-09', 'model': 'momentum', 'theta': 0})
    return seal, data


def test_consumed_before_any_holdout_outcome(tmp_path, cfg, bars, monkeypatch):
    seal, data = setup_seal(tmp_path, cfg, bars, monkeypatch)
    with pytest.raises(ValueError, match='Synthetic holdout forbidden'):
        evaluate(cfg, seal)
    assert seal.with_suffix('.consumed.json').exists()
    with pytest.raises(FileExistsError):
        evaluate(cfg, seal)


def test_changed_dataset_prevents_evaluation(tmp_path, cfg, bars, monkeypatch):
    seal, data = setup_seal(tmp_path, cfg, bars, monkeypatch)
    data.write_bytes(b'changed')
    with pytest.raises(ValueError, match='mismatch'):
        evaluate(cfg, seal)
    assert not seal.with_suffix('.consumed.json').exists()


def test_changed_actions_prevent_evaluation(tmp_path, cfg, bars, monkeypatch):
    actions = tmp_path / 'actions.csv'
    actions.write_text('symbol,date,kind\nSPY,2024-03-08,dividend\n')
    cfg['corporate_actions_path'] = str(actions)
    seal, _ = setup_seal(tmp_path, cfg, bars, monkeypatch)
    actions.write_text('symbol,date,kind\nSPY,2024-03-11,dividend\n')
    with pytest.raises(ValueError, match='mismatch'):
        evaluate(cfg, seal)


def test_old_development_cannot_freeze_changed_data(tmp_path, cfg, bars, monkeypatch):
    seal, data = setup_seal(tmp_path, cfg, bars, monkeypatch)
    seal.unlink()
    run = tmp_path / 'MOCK_DEVELOPMENT_TEST_ONLY'
    run.mkdir()
    dump(run / 'run_manifest.json', {'data_status': 'REAL_IMPORTED', 'config_hash': digest(cfg),
                                    'code_hashes': code_hashes(), 'protocol_status': 'PRE_REGISTERED',
                                    'data_sha256': 'wrong_old_dataset_hash',
                                    'external_hashes': external_hashes(cfg)})
    with pytest.raises(ValueError, match='Source data'):
        freeze(cfg, run, seal)
    assert not seal.exists()
