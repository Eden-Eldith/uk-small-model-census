"""Build the matching source, data and author-managed Zenodo deposit package."""
import hashlib
import json
import shutil
import zipfile
from datetime import date
from prepare_release import ROOT, STAGE, VERSION, REVISION_DATE, TITLE, CODE_FILES, PDF_NAMES, main as stage_release


def zip_files(target, pairs):
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for source, name in pairs:
            z.write(source, name)
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None


def main():
    manifest = stage_release()
    target = ROOT / "output/zenodo"
    target.mkdir(parents=True, exist_ok=True)
    source = target / "UK_Small_Model_Census_LaTeX_Source.zip"
    zip_files(source, [(ROOT / n, n) for n in CODE_FILES])
    data_zip = target / f"UK_Small_Model_Census_Data_v{VERSION}.zip"
    data_names = [item["path"] for item in manifest["files"]] + ["manifest.json"]
    data_pairs = [(STAGE / "data" / name, "data/" + name) for name in data_names]
    data_pairs += [(STAGE / "README.md", "README.md"), (STAGE / "LICENSE.md", "LICENSE.md"),
                   (STAGE / "config/filters.json", "config/filters.json")]
    zip_files(data_zip, data_pairs)
    builders = json.loads((ROOT / "data/builder_statistics.json").read_text(encoding="utf-8"))
    inventory = json.loads((ROOT / "data/inventory_statistics.json").read_text(encoding="utf-8"))
    metadata = {
        "title": TITLE, "upload_type": "publication", "publication_type": "preprint",
        "publication_date": REVISION_DATE, "version": VERSION, "language": "eng",
        "access_right": "open", "license": "cc-by-4.0",
        "creators": [{"name": "O'Brien, Phillip Charles", "affiliation": "Independent researcher, Gosport, United Kingdom", "orcid": "0009-0007-3961-1182"}],
        "keywords": ["independent research", "UK AI capability", "small language models", "sovereign AI", "model discovery"],
        "description": f"<p>Frozen {inventory['frozen_models']}-model, {inventory['frozen_accounts']}-account discovery cohort. The paper investigates UK-based, from-scratch language-model builders outside university and institutional routes and examines what company-centred sovereign-AI inventories miss.</p><p>Recalculated source-linked classifications identify {builders['uk_built_people']} UK-based builders across {builders['uk_built_model_entries']} model entries, including {builders['uk_from_scratch_people']} from-scratch builders and {builders['strict_independent_people']} strict independent builders. The full {inventory['frozen_accounts']}-account appendix retains institutional, overseas, derived, untrained and unresolved records.</p>",
        "related_identifiers": [{"identifier": "https://github.com/Eden-Eldith/uk-small-model-census", "relation": "isSupplementedBy", "scheme": "url"}, {"identifier": "https://huggingface.co/datasets/edeneldith/uk-small-model-census", "relation": "isSupplementedBy", "scheme": "url"}],
        "notes": "Review draft awaiting author approval for formal release and Zenodo deposit. Repository synchronisation records ongoing work. Packaging does not upload to Zenodo or assign a DOI. Matching PDFs, source and data are included. Private logs and working notes are excluded."
    }
    metadata["description"] += "<p>The strategic argument connects capability discovery to the race through RSI, AGI and ASI, the risk of dependent vassal-state status, and the need for a national model-building programme. The 2026 Hugging Face security incident provides a concrete example of operational dependence during an emergency. The paper addresses the National Security Strategy's baseline ambition, active defence, retained expertise, regional and distributed compute, and practical routes into model-building.</p>"
    meta = target / "zenodo_metadata.json"
    meta.write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    readme = target / "README.txt"
    revision = date.fromisoformat(REVISION_DATE)
    revision_label = f"{revision.day} {revision:%B %Y}"
    readme.write_text(TITLE+f"\nPhillip Charles O'Brien | ORCID 0009-0007-3961-1182\nVersion {VERSION} | {revision_label}\n\nThis package contains the paper, full {inventory['frozen_accounts']}-account appendix, LaTeX/source archive, matching dataset, and deposit metadata. Review draft: formal release and Zenodo deposit await author approval. Repository updates record ongoing work. No Zenodo upload or DOI assignment is performed by this command.\n\nOriginal paper and annotations: CC BY 4.0. Code: MIT. Third-party metadata and official statistics retain their source rights. The original O'Brien crest is preserved. Private working material is excluded.\n", encoding="utf-8")
    package = target / "UK_Small_Model_Census_Zenodo_Package.zip"
    pairs = [(ROOT / "output/pdf" / n, n) for n in PDF_NAMES]
    pairs += [(source, source.name), (data_zip, data_zip.name), (meta, meta.name), (readme, "README.txt")]
    zip_files(package, pairs)
    (STAGE / "release").mkdir(exist_ok=True)
    for p in (source, data_zip, meta, package):
        shutil.copyfile(p, STAGE / "release" / p.name)
    print(json.dumps({"package": str(package), "sha256": hashlib.sha256(package.read_bytes()).hexdigest(), "data_files": len(manifest["files"])}))

if __name__ == "__main__":
    main()
