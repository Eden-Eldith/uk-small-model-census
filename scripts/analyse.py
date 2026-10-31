"""Reproduce the corrected census from the released evidence inputs."""
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if __name__ == "__main__":
    subprocess.run([sys.executable, str(ROOT / "scripts/classify_builders.py")], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(ROOT / "scripts/classify_inventory.py"), "--model-decisions", str(ROOT / "data/model_decisions.jsonl"), "--people", str(ROOT / "data/people_classification.jsonl")], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(ROOT / "scripts/build_revision.py")], cwd=ROOT, check=True)
