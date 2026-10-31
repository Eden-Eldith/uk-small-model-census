"""Stage only the explicit public census files; private research remains local."""
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "work/release/halloween_v1_1/dataset"
VERSION = "1.1.0"
TITLE = "What About the Independents Then: Investigating Small Large Language Models in the UK"
PUBLIC_FILES = [
    "accounts.csv", "models_all.csv", "collection.json", "collection_statistics.json",
    "raw/accounts.json", "raw/models.jsonl", "schema.json",
    "account_inventory_annotations.jsonl", "model_inventory_annotations.jsonl",
    "builder_classification_inputs.json", "account_inventory.csv", "account_inventory.jsonl",
    "model_inventory.csv", "model_inventory.jsonl", "inventory_statistics.json",
    "people_classification.csv", "people_classification.jsonl", "model_decisions.csv",
    "model_decisions.jsonl", "builder_statistics.json", "builder_flow.csv",
    "provenance_comparisons.json", "context/uk_hardware_prices.csv",
    "context/england_imd2025_local_authorities.csv", "context/census_context.json",
    "context/dfe_education_context.csv", "builder_descriptive_summary.csv",
    "context/README.md",
]
PUBLIC_FILES += [f"raw/api_page_{i:03d}.json" for i in range(10)]
PUBLIC_FILES += [f"raw/ui_page_{i:03d}.json" for i in range(31)]
PAPER_FILES = ["main.tex", "abstract.tex", "methods.tex", "results.tex", "sovereignty.tex",
               "generated_counts.tex", "summary_table.tex", "references.bib", "figures/obrien-crest.png"]
CODE_FILES = [".gitignore", "README.md", "METHODS.md", "CITATION.cff", "dataset_card.md",
              "LICENSE", "DATA_LICENSE.md", "requirements.txt", "config/filters.json"]
SCRIPT_FILES = ["analyse.py", "collect.py", "enrich_github.py", "download_data.py",
                "classify_builders.py", "classify_inventory.py", "build_revision.py",
                "build_appendix.py", "build_paper.ps1", "prepare_release.py", "package_review.py"]
CODE_FILES += ["scripts/" + n for n in SCRIPT_FILES] + ["paper/" + n for n in PAPER_FILES]
PDF_NAMES = ["What_About_the_Independents_Then_2026-10-31.pdf",
             "UK_Small_Model_Census_Appendix_2026-10-31.pdf"]


def main():
    stage = STAGE.resolve()
    expected_parent = (ROOT / "work/release").resolve()
    assert expected_parent in stage.parents and stage.name == "dataset"
    stage.mkdir(parents=True, exist_ok=True)
    for name in PUBLIC_FILES:
        source = ROOT / "data" / name
        if not source.is_file():
            raise FileNotFoundError(source)
        target = stage / "data" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    manifest = {"version": VERSION, "title": TITLE, "study_date": "2026-10-30",
                "revision_date": "2026-10-31", "files": []}
    for name in sorted(PUBLIC_FILES):
        p = stage / "data" / name
        manifest["files"].append({"path": name, "bytes": p.stat().st_size,
                                  "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    (stage / "data/manifest.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    shutil.copyfile(ROOT / "dataset_card.md", stage / "README.md")
    shutil.copyfile(ROOT / "DATA_LICENSE.md", stage / "LICENSE.md")
    (stage / "config").mkdir(exist_ok=True)
    shutil.copyfile(ROOT / "config/filters.json", stage / "config/filters.json")
    (stage / "paper").mkdir(exist_ok=True)
    for name in PDF_NAMES:
        shutil.copyfile(ROOT / "output/pdf" / name, stage / "paper" / name)
    print(json.dumps({"public_data_files": len(PUBLIC_FILES), "stage": str(stage)}))
    return manifest

if __name__ == "__main__":
    main()
