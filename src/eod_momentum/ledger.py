"""Append-only hash chain; existing trial entries cannot be silently replaced."""
import fcntl
import json
import os

from .common import digest, utcnow


def append(path, record):
    reserved = {'trial_id', 'registered_at', 'previous_hash', 'hash'}
    if reserved.intersection(record):
        raise ValueError('Reserved trial metadata cannot be overridden')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a+') as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        fh.seek(0)
        lines = [json.loads(line) for line in fh if line.strip()]
        previous = 'GENESIS'
        for row in lines:
            stored = row.pop('hash')
            if row['previous_hash'] != previous or digest(row) != stored:
                raise ValueError('TRIAL_LEDGER_TAMPERED')
            previous = stored
        rec = {'trial_id': len(lines) + 1, 'registered_at': utcnow().isoformat(),
               'previous_hash': previous, **record}
        rec['hash'] = digest(rec)
        fh.write(json.dumps(rec, sort_keys=True, default=str) + '\n')
        fh.flush()
        os.fsync(fh.fileno())
    return rec
