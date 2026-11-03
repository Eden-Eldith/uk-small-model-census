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
    independent_label = "builder" if builders["strict_independent_people"] == 1 else "builders"
    metadata = {
        "title": TITLE, "upload_type": "publication", "publication_type": "preprint",
        "publication_date": REVISION_DATE, "version": VERSION, "language": "eng",
        "access_right": "open", "license": "cc-by-4.0",
        "creators": [{"name": "O'Brien, Phillip Charles", "affiliation": "Independent researcher, Gosport, United Kingdom", "orcid": "0009-0007-3961-1182"}],
        "keywords": ["independent research", "UK AI capability", "small language models", "sovereign AI", "model discovery"],
        "description": f"<p>Using a frozen cohort of {inventory['frozen_models']} model repositories and {inventory['frozen_accounts']} publishing accounts collected on 30 October 2026, this paper investigates UK-based, from-scratch language-model builders outside university and institutional routes and examines what company-centred sovereign-AI inventories miss.</p><p>Source-linked classifications identify {builders['uk_built_people']} UK-based builders across {builders['uk_built_model_entries']} model entries, including {builders['uk_from_scratch_people']} from-scratch builders and {builders['strict_independent_people']} strict independent {independent_label}. The full {inventory['frozen_accounts']}-account appendix retains institutional, overseas, derived, untrained and unresolved records.</p>",
        "related_identifiers": [{"identifier": "https://github.com/Eden-Eldith/uk-small-model-census", "relation": "isSupplementedBy", "scheme": "url"}, {"identifier": "https://huggingface.co/datasets/edeneldith/uk-small-model-census", "relation": "isSupplementedBy", "scheme": "url"}],
        "notes": "Completed preprint with matching companion appendix, reproducible source and data. Original paper and annotations: CC BY 4.0. Original code: MIT. Third-party metadata and official statistics retain their source rights. Private logs and working notes are excluded."
    }
    metadata["description"] += "<p>The strategic argument connects capability discovery to the race through RSI, AGI and ASI, the risk of dependent vassal-state status, and the need for a national model-building programme. The 2026 Hugging Face security incident provides a concrete example of operational dependence during an emergency. The paper addresses the National Security Strategy's baseline ambition, active defence, retained expertise, regional and distributed compute, and practical routes into model-building.</p>"
    meta = target / "zenodo_metadata.json"
    metadata["description"] += "<p>The argument connects AI-assisted model development, strategic competition and deterrence, operational control of public systems, and the power, cooling, grid and regional infrastructure needed to develop domestic builders. Skills and licensing precedents inform practical routes into research.</p>"
    metadata["description"] += "<p>Rupert Lowe's posts of 24 October and 2 November 2026 connect sovereign AI, cyber defence and British technical expertise. The paper identifies this shared strategic concern from the leader of Restore Britain and connects it to the practical discovery and support of independent model builders.</p>"
    meta.write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    readme = target / "README.txt"
    revision = date.fromisoformat(REVISION_DATE)
    revision_label = f"{revision.day} {revision:%B %Y}"
    description_text = metadata["description"].replace("</p><p>", "\n\n").replace("<p>", "").replace("</p>", "")
    upload_names = PDF_NAMES + [source.name, data_zip.name]
    guide = (
        TITLE + f"\nPhillip Charles O'Brien | ORCID 0009-0007-3961-1182\nVersion {VERSION} | {revision_label}\n\n"
        "Completed preprint prepared for the author's Zenodo upload.\n\n"
        "UPLOAD\n"
        "1. Open https://zenodo.org/uploads/new. If this work already has a Zenodo record, create a new version of that record instead.\n"
        "2. Upload the four files listed below. Use the local UPLOAD_THESE_FOUR_FILES folder, or extract them from the complete ZIP. Keeping the PDFs separate makes them easy to read.\n"
        "3. Copy the metadata below into the deposit form. zenodo_metadata.json is a structured reference; uploading it alone does not populate the form.\n"
        "4. Preview the record and publish when ready. Zenodo registers the DOI on publication.\n\n"
        "FILES\n" + "\n".join(upload_names) + "\n\n"
        "The complete ZIP contains the same four public files plus this guide and metadata. Use either the four-file set or the complete ZIP; uploading both duplicates the contents.\n\n"
        "DEPOSIT FIELDS\n"
        "Resource type: Publication / Preprint\n"
        f"Title: {TITLE}\n"
        "Creator family name: O'Brien\nCreator given names: Phillip Charles\n"
        "Affiliation: Independent researcher, Gosport, United Kingdom\n"
        "ORCID: 0009-0007-3961-1182\n"
        f"Publication date: {REVISION_DATE}\nVersion: {VERSION}\nLanguage: English\n"
        "Access: Open\nLicence: Creative Commons Attribution 4.0 International (CC BY 4.0)\n"
        "Keywords: " + "; ".join(metadata["keywords"]) + "\n\n"
        "DESCRIPTION\n" + description_text + "\n\n"
        "ADDITIONAL NOTES\n" + metadata["notes"] + "\n\n"
        "RELATED WORKS\n"
        "Is supplemented by: https://github.com/Eden-Eldith/uk-small-model-census\n"
        "Is supplemented by: https://huggingface.co/datasets/edeneldith/uk-small-model-census\n\n"
        "Zenodo upload guide: https://help.zenodo.org/docs/deposit/create-new-upload/\n\n"
        f"The appendix contains all {inventory['frozen_accounts']} accounts and retains its 2 November evidence-revision date. The paper and package are dated {revision_label}.\n"
        "No Zenodo upload, DOI reservation or DOI assignment is performed by this packaging command. The original O'Brien crest is preserved. Private working material is excluded.\n"
    )
    readme.write_text(guide, encoding="utf-8")
    (target / "ZENODO_UPLOAD_DETAILS.txt").write_text(guide, encoding="utf-8")
    upload = target / "UPLOAD_THESE_FOUR_FILES"
    upload.mkdir(exist_ok=True)
    for name in PDF_NAMES:
        shutil.copyfile(ROOT / "output/pdf" / name, upload / name)
    for p in (source, data_zip):
        shutil.copyfile(p, upload / p.name)
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
