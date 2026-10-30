"""Build the public dataset staging folder from completed evidence tables."""
import hashlib
import json
import shutil
from pathlib import Path

from collect import ROOT, dump, now


def main():
    required = ['models_all.csv', 'models_with_locations.csv', 'researcher_locations.jsonl',
                'researcher_locations.csv', 'uk_models.csv', 'uk_model_evidence.jsonl',
                'uk_model_evidence.csv', 'statistics.json', 'collection.json', 'schema.json']
    missing = [name for name in required if not (ROOT / 'data' / name).exists()]
    if missing:
        raise ValueError(f"Incomplete release: {missing}")
    paths = sorted(p for p in (ROOT / 'data').rglob('*') if p.is_file() and p.name != 'manifest.json')
    manifest = {'created_at': now(), 'study_date': '2026-10-30',
                'files': [{'path': p.relative_to(ROOT / 'data').as_posix(),
                           'bytes': p.stat().st_size,
                           'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]}
    dump(ROOT / 'data/manifest.json', manifest)
    stage = ROOT / 'work/release/dataset'
    stage.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT / 'data', stage / 'data', dirs_exist_ok=True)
    shutil.copyfile(ROOT / 'dataset_card.md', stage / 'README.md')
    shutil.copyfile(ROOT / 'DATA_LICENSE.md', stage / 'LICENSE.md')
    shutil.copytree(ROOT / 'config', stage / 'config', dirs_exist_ok=True)
    print(json.dumps({'staging_directory': str(stage), 'manifest_files': len(paths),
                      'data_bytes': sum(p.stat().st_size for p in paths)}, indent=2))


if __name__ == '__main__':
    main()
