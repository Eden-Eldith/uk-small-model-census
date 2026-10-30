"""Download the public census snapshot and check its recorded file hashes."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import quote

from collect import ROOT, get


def main(repo, revision, overwrite):
    base = f"https://huggingface.co/datasets/{repo}/resolve/{quote(revision, safe='')}/data/"
    response = get(base + "manifest.json")
    response.raise_for_status()
    manifest = response.json()
    dest = ROOT / "data"
    for entry in manifest['files']:
        relative = Path(entry['path'])
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError(f"Invalid snapshot path: {relative}")
        target = dest / relative
        if target.exists():
            if hashlib.sha256(target.read_bytes()).hexdigest() == entry['sha256']:
                continue
            if not overwrite:
                raise FileExistsError(f"Local file differs: {target}; use --overwrite deliberately")
        r = get(base + quote(relative.as_posix(), safe='/'))
        r.raise_for_status()
        if hashlib.sha256(r.content).hexdigest() != entry['sha256']:
            raise ValueError(f"Hash mismatch: {relative}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(r.content)
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(f"Verified {len(manifest['files'])} files from {repo}@{revision}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', default='edeneldith/uk-small-model-census')
    parser.add_argument('--revision', default='main', help='Use a dataset commit SHA for an immutable snapshot')
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()
    main(args.repo, args.revision, args.overwrite)
