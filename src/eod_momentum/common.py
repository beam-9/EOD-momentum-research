from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
from datetime import datetime, timezone
from importlib.metadata import distributions
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

ET = ZoneInfo('America/New_York')
UTC = timezone.utc
_source_root = Path(__file__).resolve().parents[2]
ROOT = Path(os.getenv('EOD_MOMENTUM_ROOT', str(
    _source_root if (_source_root / 'config/default.yaml').exists() else Path.cwd()))).resolve()


def utcnow():
    return datetime.now(UTC)


def stamp(day, hm):
    return datetime.fromisoformat(f'{day}T{hm}:00').replace(tzinfo=ET).astimezone(UTC)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + '\n')


def config(path=None):
    return yaml.safe_load(Path(path or ROOT / 'config/default.yaml').read_text())


def environment():
    result = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True)
    return {'python': platform.python_version(), 'platform': platform.platform(),
            'git_commit': (result.stdout.strip() if result.returncode == 0
                           else 'UNCOMMITTED_REPOSITORY'),
            'dependencies': {d.metadata['Name']: d.version for d in distributions()}}


def code_hashes():
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT / 'src').rglob('*.py'))}


def external_hashes(cfg):
    path = cfg.get("corporate_actions_path")
    return {"corporate_actions": sha(path) if path else None}
