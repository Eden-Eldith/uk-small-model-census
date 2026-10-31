"""Reproduce the corrected, person-level UK builder classification.

Inputs are compact public evidence statements, not biography-access logs.
Builder location is separate from physical accelerator location. A dated
professional-location inference is labelled and can be counted separately
from an explicit project-location statement.
"""
import argparse
import collections
import csv
import json
from pathlib import Path


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def save_jsonl(path, values):
    path.write_text("".join(json.dumps(v, ensure_ascii=False) + "\n" for v in values), encoding="utf-8")


def save_csv(path, values):
    fields = list(dict.fromkeys(k for r in values for k in r))
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for r in values:
            writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v for k, v in r.items()})


def classify(inputs):
    people = inputs["people"]
    models = inputs["models"]
    persons = {r["person_id"]: r for r in people}
    assert len(persons) == len(people)
    assert len({r["model_id"] for r in models}) == len(models)
    for m in models:
        assert m["uk_build_status"] in ("yes", "no", "unknown", "not_applicable")
        assert set(m["builder_person_ids"]).issubset(persons)
        assert m["from_scratch"] in ("yes", "no", "unknown")
        if m["uk_build_status"] == "yes":
            assert m["builder_person_ids"] and m["builder_location_country"] == "United Kingdom"
            assert m["builder_location_evidence_type"] in ("direct_public_statement", "dated_location_inference")
            assert m["builder_location_sources"] and m["builder_location_basis"]

    rows = []
    for p in people:
        pid = p["person_id"]
        linked = [m for m in models if pid in m["builder_person_ids"]]
        uk = [m for m in linked if m["uk_build_status"] == "yes" and m["natural_language"] == "yes"]
        scratch = [m for m in uk if m["from_scratch"] == "yes"]
        institutional = p["university_ever"] == "yes" or p["institutional_affiliation_ever"] == "yes"
        independence = p["university_ever"] == "no" and p["institutional_affiliation_ever"] == "no"
        qualifying = [m for m in scratch if m["project_backing"] == "no" and m["external_project_funding"] == "no"] if independence else []
        reasons = []
        if p["university_ever"] == "yes": reasons.append("university attendance")
        if p["institutional_affiliation_ever"] == "yes": reasons.append("institutional or industry affiliation")
        if not uk: reasons.append("UK natural-language model building not established")
        if not scratch: reasons.append("UK from-scratch natural-language model building not established")
        if not linked: reasons.append("identified contribution is not an attributable model-building role")
        unknowns = []
        for field in ("university_ever", "institutional_affiliation_ever"):
            if p[field] == "unknown": unknowns.append(field)
        for m in linked:
            if m["uk_build_status"] == "unknown": unknowns.append("builder location: " + m["model_id"])
            if m["from_scratch"] == "unknown": unknowns.append("initialisation: " + m["model_id"])
        row = dict(p)
        row.update(
            institutional_route="yes" if institutional else "no" if independence else "unknown",
            uk_built_model_ids=[m["model_id"] for m in uk],
            uk_from_scratch_model_ids=[m["model_id"] for m in scratch],
            strict_independent_model_ids=[m["model_id"] for m in qualifying],
            strict_independent=bool(qualifying),
            outcome_reasons=reasons,
            unresolved_fields=unknowns,
        )
        rows.append(row)

    primary = [r for r in rows if r["analysis_scope"] == "primary_uk_connection"]
    uk = [r for r in rows if r["uk_built_model_ids"]]
    scratch = [r for r in rows if r["uk_from_scratch_model_ids"]]
    strict = [r for r in rows if r["strict_independent"]]
    uk_models = [m for m in models if m["uk_build_status"] == "yes" and m["natural_language"] == "yes"]
    stats = {
        "units": "People are deduplicated identities; models are frozen repository entries. Primary UK connections are not all UK builders.",
        "reviewed_people": len(rows),
        "primary_uk_connected_people": len(primary),
        "historical_or_collaboration_context_people": len(rows) - len(primary),
        "primary_university_ever": dict(collections.Counter(r["university_ever"] for r in primary)),
        "primary_institutional_route_people": sum(r["institutional_route"] == "yes" for r in primary),
        "primary_institutional_route_names": [r["name"] for r in primary if r["institutional_route"] == "yes"],
        "reviewed_institutional_route_people": sum(r["institutional_route"] == "yes" for r in rows),
        "uk_built_people": len(uk),
        "uk_built_names": [r["name"] for r in uk],
        "uk_built_model_entries": len(uk_models),
        "uk_built_model_ids": [m["model_id"] for m in uk_models],
        "uk_built_model_location_evidence": dict(collections.Counter(m["builder_location_evidence_type"] for m in uk_models)),
        "uk_from_scratch_people": len(scratch),
        "uk_from_scratch_names": [r["name"] for r in scratch],
        "uk_from_scratch_model_entries": len({mid for r in scratch for mid in r["uk_from_scratch_model_ids"]}),
        "uk_built_institutional_route_people": sum(r["institutional_route"] == "yes" for r in uk),
        "uk_from_scratch_institutional_route_people": sum(r["institutional_route"] == "yes" for r in scratch),
        "strict_independent_people": len(strict),
        "strict_independent_names": [r["name"] for r in strict],
        "strict_independent_model_entries": len({mid for r in strict for mid in r["strict_independent_model_ids"]}),
        "uk_built_schooling": dict(collections.Counter(r["UK_schooling"] for r in uk)),
        "assessed_model_builder_location_status": dict(collections.Counter(m["uk_build_status"] for m in models)),
        "uk_built_compute": [{"model_id": m["model_id"], "hardware": m["hardware"], "compute_source": m["compute_source"], "purchase_price_bands": m["purchase_price_bands"]} for m in uk_models],
    }
    flow = [
        {"stage": "People in primary UK-connection evidence", "people": len(primary), "definition": "Current or model-period UK connections, including contributors and later arrivals."},
        {"stage": "Attributable UK natural-language model builders", "people": len(uk), "definition": "Direct project-location statement or explicitly labelled, dated professional-location inference."},
        {"stage": "UK builders with from-scratch models", "people": len(scratch), "definition": "At least one UK-built natural-language model trained from new initialisation."},
        {"stage": "Strict independent UK from-scratch builders", "people": len(strict), "definition": "Never attended university, no institutional affiliation, and affirmative independent-project evidence."},
    ]
    return rows, models, stats, flow


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", type=Path, default=Path("data/builder_classification_inputs.json"))
    parser.add_argument("--output", type=Path, default=Path("data"))
    args = parser.parse_args()
    inputs = json.loads(args.inputs.read_text(encoding="utf-8"))
    rows, models, stats, flow = classify(inputs)
    args.output.mkdir(parents=True, exist_ok=True)
    for name, records in (("people_classification", rows), ("model_decisions", models)):
        save_jsonl(args.output / (name + ".jsonl"), records)
        save_csv(args.output / (name + ".csv"), records)
    save_csv(args.output / "builder_flow.csv", flow)
    save_json(args.output / "builder_statistics.json", stats)
    print(json.dumps({k: v for k, v in stats.items() if k not in ("uk_built_compute", "primary_institutional_route_names", "uk_built_model_ids")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
