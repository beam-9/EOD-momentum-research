"""Synthetic engineering benchmark only, never market performance evidence."""

def main():
    import json
    import sys
    import time
    import tracemalloc
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    sys.path[:0] = [str(root / 'src'), str(root / 'tests')]
    from conftest import synthetic
    from eod_momentum.common import config
    from eod_momentum.data import audit
    from eod_momentum.engine import simulate
    from eod_momentum.features import build_features

    out = []
    for start, end, label in [('2024-03-04', '2024-03-08', '1_week'), ('2023-01-03', '2023-12-29', '1_year')]:
        tracemalloc.start()
        t = time.perf_counter()
        bars = synthetic(start, end, ('SPY', 'QQQ'))
        normalized = time.perf_counter()
        quality, valid = audit(bars, start, end, ['SPY', 'QQQ'])
        features, _ = build_features(valid, start, end, config())
        feature_end = time.perf_counter()
        for f in features:
            simulate(f, valid[(f['symbol'], f['date'])], 1)
        done = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        out.append({'sample': label, 'classification': 'SYNTHETIC_ENGINEERING_ONLY', 'bars': len(bars),
                    'features': len(features), 'generate_normalize_seconds': normalized - t,
                    'audit_features_seconds': feature_end - normalized, 'replay_seconds': done - feature_end,
                    'total_wall_seconds': done - t, 'peak_python_tracemalloc_bytes': peak,
                    'native_memory_included': False, 'price_frame_estimated_bytes': bars.estimated_size()})
    path = root / 'results/verification/profile.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2) + '\n')
    print(path)

if __name__ == "__main__":
    main()
