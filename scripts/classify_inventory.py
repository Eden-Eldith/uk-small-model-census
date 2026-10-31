"""Reproduce the frozen account/model inventory from compact public annotations.

Annotations describe source evidence; this program applies the fixed categories
and aggregates accounts. Platform account type is separate from reviewed entity
type. A public location or later affiliation is never promoted to build location.
"""
import argparse
import collections
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROVENANCE = {'from_scratch', 'derived', 'untrained', 'mirror', 'unresolved'}
INDIVIDUAL_TYPES = {'individual', 'individual_project', 'individual_business', 'individual_publication'}
UNCERTAIN_TYPES = {'unknown', 'individual_or_research_lab', 'individual_or_collective'}


def readl(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def write_csv(path, rows):
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v
                         for k, v in row.items()} for row in rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=ROOT / 'data')
    parser.add_argument('--annotations-dir', type=Path)
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--model-decisions', type=Path)
    parser.add_argument('--people', type=Path, help='Public person classifications, joined only by IDs or explicit account links.')
    args = parser.parse_args()
    annotation_dir = args.annotations_dir or args.data_dir
    out = args.output_dir or args.data_dir
    out.mkdir(parents=True, exist_ok=True)
    with (args.data_dir / 'models_all.csv').open(encoding='utf-8', newline='') as stream:
        frozen = list(csv.DictReader(stream))
    with (args.data_dir / 'accounts.csv').open(encoding='utf-8', newline='') as stream:
        frozen_accounts = list(csv.DictReader(stream))
    annotations = {r['model_id']: r for r in readl(annotation_dir / 'model_inventory_annotations.jsonl')}
    account_annotations = {r['account']: r for r in readl(annotation_dir / 'account_inventory_annotations.jsonl')}
    assert len(frozen) == len({r['model_id'] for r in frozen}) == 917
    assert len(frozen_accounts) == len({r['account'] for r in frozen_accounts}) == 495
    assert set(annotations) == {r['model_id'] for r in frozen}
    assert set(account_annotations) == {r['account'] for r in frozen_accounts}
    decisions = {}
    if args.model_decisions:
        decisions = {r['model_id']: r for r in readl(args.model_decisions)}
        assert set(decisions).issubset(annotations)
    people = {}
    if args.people:
        people = {r['person_id']: r for r in readl(args.people)}
    models = []
    for original in sorted(frozen, key=lambda r: r['model_id'].lower()):
        mid = original['model_id']
        ann = annotations[mid]
        assert ann['model_provenance'] in PROVENANCE
        row = {k: original[k] for k in ['model_id', 'account', 'model_url', 'parameters', 'revision', 'created_at']}
        row.update(ann)
        if mid in decisions:
            row.update({k: v for k, v in decisions[mid].items() if k != 'model_id'})
            row['provenance_evidence_level'] = 'detailed_model_assessment'
            if row.get('from_scratch') in ['yes', 'no']:
                row['own_from_scratch_lineage'] = row['from_scratch']
            if row['model_provenance'] in {'from_scratch', 'derived', 'mirror'}:
                row['trained_status'] = 'yes'
        row.setdefault('uk_build_status', 'unknown')
        if row['uk_build_status'] == 'yes':
            assert row.get('builder_location_basis') or row.get('basis') or row.get('uk_build_basis')
        models.append(row)
    by_account = collections.defaultdict(list)
    for row in models:
        by_account[row['account']].append(row)
    accounts = []
    for original in sorted(frozen_accounts, key=lambda r: r['account'].lower()):
        account = original['account']
        ann = account_annotations[account]
        linked = by_account[account]
        person_ids = set(ann.get('linked_person_ids', []))
        person_ids.update(p['person_id'] for p in people.values() if account in p.get('accounts', []))
        person_ids.update(pid for m in linked for pid in m.get('identified_person_ids', []))
        person_rows = [people[pid] for pid in sorted(person_ids) if pid in people]
        kind = ann['reviewed_account_type']
        identity_class = ('individual' if kind in INDIVIDUAL_TYPES else
                          'unresolved_entity_type' if kind in UNCERTAIN_TYPES else
                          'organisation_or_collective')
        pc = dict(sorted(collections.Counter(m['model_provenance'] for m in linked).items()))
        bc = dict(sorted(collections.Counter(m['uk_build_status'] for m in linked).items()))
        reasons = list(ann.get('outcome_reasons', []))
        if identity_class == 'organisation_or_collective':
            reasons.append('organisation_or_collective_publisher')
        if ann['location_status'] == 'non_uk_public_location':
            reasons.append('documented_non_uk_geographic_connection')
        if all(m['model_provenance'] in {'derived', 'untrained', 'mirror'} for m in linked):
            reasons.append('all_frozen_releases_derived_untrained_or_mirrors')
        if all(m.get('natural_language') in ['no', False] for m in linked):
            reasons.append('non_natural_language_models')
        row = {'account': account, 'platform_account_type': original['account_type'],
               'reviewed_account_type': kind, 'account_identity_class': identity_class,
               'display_name': original['display_name'], 'profile_url': original['profile_url'],
               'model_count': len(linked), 'model_ids': [r['model_id'] for r in linked]}
        row.update(ann)
        row['linked_person_ids'] = sorted(person_ids)
        if person_rows:
            row['university_ever_by_linked_person'] = {p['person_id']: p['university_ever'] for p in person_rows}
            row['institutional_affiliation_ever_by_person'] = {p['person_id']: p['institutional_affiliation_ever'] for p in person_rows}
            row['strict_independent_person_ids'] = [p['person_id'] for p in person_rows if p['strict_independent']]
            row['person_classifications'] = [{k: p[k] for k in [
                'person_id', 'name', 'university_ever', 'institutional_affiliation_ever',
                'institutional_route', 'UK_schooling', 'strict_independent', 'outcome_reasons',
                'unresolved_fields', 'sources'] if k in p} for p in person_rows]
            reasons.extend(f"{p['person_id']}: {reason}" for p in person_rows for reason in p['outcome_reasons'])
        else:
            row['institutional_affiliation_ever_by_person'] = {}
            row['strict_independent_person_ids'] = []
            row['person_classifications'] = []
        row['institutional_backing_at_build_by_model'] = {
            m['model_id']: {'institutional_affiliation_at_build': m.get('institutional_affiliation_at_build', 'unknown'),
                            'project_backing': m.get('project_backing', 'unknown'),
                            'external_project_funding': m.get('external_project_funding', 'unknown')}
            for m in linked}
        row['compute_by_model'] = {m['model_id']: {
            'hardware': m.get('hardware', m.get('compute_used', 'not established')),
            'source': m.get('compute_source', 'unknown'),
            'physical_country': m.get('physical_compute_country', m.get('compute_country', 'unknown'))}
            for m in linked}
        row.update(model_provenance_counts=pc, uk_build_counts=bc,
                   outcome_reasons=list(dict.fromkeys(reasons)))
        accounts.append(row)
    stats = {
        'frozen_models': len(models), 'frozen_accounts': len(accounts),
        'platform_account_types': dict(collections.Counter(r['platform_account_type'] for r in accounts)),
        'reviewed_account_types': dict(collections.Counter(r['reviewed_account_type'] for r in accounts)),
        'account_identity_classes': dict(collections.Counter(r['account_identity_class'] for r in accounts)),
        'account_location_status': dict(collections.Counter(r['location_status'] for r in accounts)),
        'model_provenance': dict(collections.Counter(r['model_provenance'] for r in models)),
        'provenance_evidence_levels': dict(collections.Counter(r['provenance_evidence_level'] for r in models)),
        'trained_status': dict(collections.Counter(r['trained_status'] for r in models)),
        'own_from_scratch_lineage': dict(collections.Counter(r['own_from_scratch_lineage'] for r in models)),
        'uk_build_status': dict(collections.Counter(r['uk_build_status'] for r in models)),
        'accounts_with_recorded_public_names_or_aliases': sum(bool(r['person_names']) for r in accounts),
        'accounts_all_releases_derived_untrained_or_mirrors': sum(
            'all_frozen_releases_derived_untrained_or_mirrors' in r['outcome_reasons'] for r in accounts),
        'accounts_with_any_from_scratch_release': sum(r['model_provenance_counts'].get('from_scratch', 0) > 0 for r in accounts),
        'accounts_with_any_unknown_provenance': sum(r['model_provenance_counts'].get('unresolved', 0) > 0 for r in accounts),
        'unresolved_location_models': sum(r['model_count'] for r in accounts if r['location_status'] == 'unknown'),
        'classified_people': len(people),
        'confirmed_strict_independent_people': len({pid for r in accounts for pid in r['strict_independent_person_ids']}),
        'unit_notes': 'Location categories are geographic connections, not all residence or build-time location. Account identity classes do not enumerate unique builders. Whole-cohort provenance includes explicit publisher declarations; detailed UK eligibility uses separately linked model and person evidence. Reason counts overlap.',
    }
    write_csv(out / 'account_inventory.csv', accounts)
    write_csv(out / 'model_inventory.csv', models)
    for name, records in [('account_inventory', accounts), ('model_inventory', models)]:
        (out / f'{name}.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in records), encoding='utf-8')
    (out / 'inventory_statistics.json').write_text(json.dumps(stats, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
