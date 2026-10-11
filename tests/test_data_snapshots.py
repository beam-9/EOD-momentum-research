"""Storage regression fixtures only; no licensed data or network access."""
import json

import polars as pl
import pytest

from eod_momentum import data
from eod_momentum.common import sha


@pytest.fixture
def storage(tmp_path, monkeypatch):
    monkeypatch.setattr(data, 'ROOT', tmp_path)
    return tmp_path


def toy_frame(price):
    return pl.DataFrame({'symbol': ['TEST_ONLY'], 'open': [float(price)]})


def active_paths(root):
    return root / 'data/processed/underlying.parquet', root / 'data/manifests/underlying.json'


def snapshot_manifest(root, dataset, manifest):
    return root / f'data/manifests/snapshots/underlying/{sha(dataset)}/{sha(manifest)}.json'


def test_replacement_retains_both_dataset_versions_and_original_manifest(storage):
    first = data.persist(toy_frame(100), 'underlying', {'source': 'TOY_FIRST'})
    _, manifest = active_paths(storage)
    original_data, original_manifest = first.read_bytes(), manifest.read_bytes()
    original_hash = sha(first)
    original_manifest_snapshot = snapshot_manifest(storage, first, manifest)
    result = data.persist(toy_frame(101), 'underlying', {'source': 'TOY_SECOND'})
    assert result == first
    record = json.loads(manifest.read_text())
    assert record['sha256'] == sha(result)
    assert record['rows'] == 1
    previous = record['previous_snapshot']
    assert previous['sha256'] == original_hash
    assert (storage / previous['data_path']).read_bytes() == original_data
    assert (storage / previous['manifest_path']).read_bytes() == original_manifest
    assert original_manifest_snapshot.read_bytes() == original_manifest
    assert (storage / record['snapshot_data_path']).read_bytes() == result.read_bytes()
    assert snapshot_manifest(storage, result, manifest).read_bytes() == manifest.read_bytes()


def test_identical_data_different_provenance_retains_both_manifests(storage):
    dataset = data.persist(toy_frame(100), 'underlying', {'source': 'TOY_A'})
    _, manifest = active_paths(storage)
    first_hash, first_manifest = sha(dataset), manifest.read_bytes()
    first_snapshot = snapshot_manifest(storage, dataset, manifest)
    data.persist(toy_frame(100), 'underlying', {'source': 'TOY_B'})
    assert sha(dataset) == first_hash
    second_snapshot = snapshot_manifest(storage, dataset, manifest)
    assert first_snapshot != second_snapshot
    assert first_snapshot.read_bytes() == first_manifest
    assert second_snapshot.read_bytes() == manifest.read_bytes()
    assert len(list((storage / 'data/processed/snapshots/underlying').glob('*.parquet'))) == 1


@pytest.mark.parametrize('corrupt_manifest', [False, True])
def test_existing_snapshot_corruption_refuses_replacement_leaves_active_untouched(storage,
                                                                                 corrupt_manifest):
    dataset = data.persist(toy_frame(100), 'underlying', {'source': 'TOY_A'})
    _, manifest = active_paths(storage)
    original_data, original_manifest = dataset.read_bytes(), manifest.read_bytes()
    record = json.loads(original_manifest)
    snapshot = (snapshot_manifest(storage, dataset, manifest) if corrupt_manifest else
                storage / record['snapshot_data_path'])
    snapshot.write_bytes(b'TEST_ONLY_CORRUPTION')
    with pytest.raises(ValueError, match='Snapshot integrity failure'):
        data.persist(toy_frame(101), 'underlying', {'source': 'TOY_B'})
    assert dataset.read_bytes() == original_data
    assert manifest.read_bytes() == original_manifest
    assert snapshot.read_bytes() == b'TEST_ONLY_CORRUPTION'


def test_legacy_dataset_manifest_is_retained_byte_for_byte(storage):
    dataset, manifest = active_paths(storage)
    dataset.parent.mkdir(parents=True)
    manifest.parent.mkdir(parents=True)
    toy_frame(100).write_parquet(dataset)
    manifest.write_text(json.dumps({'source': 'TOY_LEGACY', 'sha256': sha(dataset), 'rows': 1}))
    original = manifest.read_bytes()
    data.persist(toy_frame(101), 'underlying', {'source': 'TOY_NEW'})
    previous = json.loads(manifest.read_text())['previous_snapshot']
    assert (storage / previous['manifest_path']).read_bytes() == original


def test_missing_legacy_manifest_is_explicitly_unknown(storage):
    dataset, manifest = active_paths(storage)
    dataset.parent.mkdir(parents=True)
    toy_frame(100).write_parquet(dataset)
    original = dataset.read_bytes()
    data.persist(toy_frame(101), 'underlying', {'source': 'TOY_NEW'})
    previous = json.loads(manifest.read_text())['previous_snapshot']
    assert previous['manifest_path'] is None
    assert previous['provenance_status'] == 'UNKNOWN_MISSING_MANIFEST'
    assert (storage / previous['data_path']).read_bytes() == original


def test_mismatched_legacy_manifest_fails_before_active_replacement(storage):
    dataset, manifest = active_paths(storage)
    dataset.parent.mkdir(parents=True)
    manifest.parent.mkdir(parents=True)
    toy_frame(100).write_parquet(dataset)
    manifest.write_text(json.dumps({'sha256': 'WRONG_TEST_ONLY_HASH'}))
    original_data, original_manifest = dataset.read_bytes(), manifest.read_bytes()
    with pytest.raises(ValueError, match='Active manifest does not match dataset'):
        data.persist(toy_frame(101), 'underlying', {'source': 'TOY_NEW'})
    assert dataset.read_bytes() == original_data
    assert manifest.read_bytes() == original_manifest


def test_conflicting_replacement_snapshot_fails_before_changing_active(storage):
    dataset = data.persist(toy_frame(100), 'underlying', {'source': 'TOY_A'})
    _, manifest = active_paths(storage)
    original_data, original_manifest = dataset.read_bytes(), manifest.read_bytes()
    replacement = storage / 'replacement.parquet'
    toy_frame(101).write_parquet(replacement)
    conflict = storage / f'data/processed/snapshots/underlying/{sha(replacement)}.parquet'
    conflict.write_bytes(b'TEST_ONLY_CONFLICT')
    with pytest.raises(ValueError, match='Snapshot integrity failure'):
        data.persist(toy_frame(101), 'underlying', {'source': 'TOY_B'})
    assert dataset.read_bytes() == original_data
    assert manifest.read_bytes() == original_manifest
    assert conflict.read_bytes() == b'TEST_ONLY_CONFLICT'
