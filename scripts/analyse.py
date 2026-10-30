"""Reproduce cohort and geographic tables from released source annotations."""
import argparse
import collections
import csv
import json
from pathlib import Path
from collect import ROOT, dump, write_csv

STATUSES = {'uk_public_location', 'non_uk_public_location', 'uk_affiliation_only', 'mixed_locations', 'unknown'}
CONNECTIONS = {'individual_public_location', 'creator_public_location', 'contributor_public_location', 'institutional_affiliation', 'conflicting_location', 'organisation_location'}

def jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]

def save_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows), encoding='utf-8')

def fields_union(records, first=()):
    result = list(first)
    for row in records:
        result.extend(k for k in row if k not in result)
    return result

def main(collection_only=False, review_dir=None):
    data = ROOT / 'data'
    with (data / 'models_all.csv').open(encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    accounts = json.loads((data / 'raw/accounts.json').read_text(encoding='utf-8'))
    collection = json.loads((data / 'collection.json').read_text(encoding='utf-8'))
    mids = {r['model_id'] for r in rows}
    if len(rows) != len(mids) or len(rows) != collection['api_unique']:
        raise ValueError('Model CSV does not match recorded unique collection')
    stats = {
        'models': len(rows), 'publisher_accounts': len(accounts),
        'model_account_types': dict(collections.Counter(r['account_type'] for r in rows)),
        'publisher_account_types': dict(collections.Counter(a['account_type'] for a in accounts.values())),
        'min_reported_parameters': min(int(r['parameters']) for r in rows),
        'max_reported_parameters': max(int(r['parameters']) for r in rows),
        'strictly_under_1b': sum(int(r['parameters']) < 1_000_000_000 for r in rows),
        'nonempty_declared_base_model': sum(r['base_model_declared'] not in ('', '[]', 'null') for r in rows),
        'snapshot_started': collection['started_at'], 'snapshot_finished': collection['finished_at'],
    }
    if collection_only:
        dump(data / 'collection_statistics.json', stats)
        print(json.dumps(stats, indent=2))
        return
    if review_dir:
        reviews = [r for i in range(1, 4) for r in jsonl(review_dir / f'locations_{i}.jsonl')]
    else:
        reviews = jsonl(data / 'researcher_locations.jsonl')
    by_account = {r['account']: r for r in reviews}
    if len(reviews) != len(by_account) or set(by_account) != set(accounts):
        raise ValueError(f'Review coverage incomplete: {len(by_account)}/{len(accounts)}; missing {sorted(set(accounts)-set(by_account))}')
    for review in reviews:
        if review['location_status'] not in STATUSES:
            raise ValueError(f"Unknown location status: {review['account']}")
        if review['location_status'] != 'unknown' and not review.get('evidence'):
            raise ValueError(f"Location lacks source evidence: {review['account']}")
        if not review.get('searched_sources'):
            raise ValueError(f"No research sources recorded: {review['account']}")
    reviews.sort(key=lambda r: r['account'].lower())
    location_fields = fields_union(reviews, ['account', 'account_type_reviewed', 'researcher_names', 'location_status', 'country', 'location_text', 'evidence', 'searched_sources', 'notes', 'uk_model_ids'])
    write_csv(data / 'researcher_locations.csv', reviews, location_fields)
    save_jsonl(data / 'researcher_locations.jsonl', reviews)

    assessments = jsonl(data / 'uk_model_evidence.jsonl')
    by_model = {r['model_id']: r for r in assessments}
    if len(assessments) != len(by_model) or not set(by_model).issubset(mids):
        raise ValueError('Model evidence has duplicate or out-of-cohort identifiers')
    for review in assessments:
        if not review.get('sources'):
            raise ValueError(f"No model sources: {review['model_id']}")
        if not set(review['uk_connection_types']).issubset(CONNECTIONS):
            raise ValueError(f"Unknown UK connection type: {review['model_id']}")
    write_csv(data / 'uk_model_evidence.csv', assessments, fields_union(assessments, ['model_id', 'researchers', 'uk_connection_types', 'scope_fit', 'training_origin', 'architecture', 'hardware', 'independence']))

    merged = []
    for row in rows:
        review = by_account[row['account']]
        assessment = by_model.get(row['model_id'])
        combined = dict(row)
        combined.update({
            'publisher_type_reviewed': review['account_type_reviewed'],
            'researcher_names': review.get('researcher_names', []),
            'publisher_location_status': review['location_status'],
            'publisher_country': review.get('country'),
            'publisher_location_text': review.get('location_text'),
            'location_evidence': review.get('evidence', []),
            'location_notes': review.get('notes', ''),
            'uk_model_assessed': assessment is not None,
            'uk_connection_types': assessment['uk_connection_types'] if assessment else [],
            'uk_person_location_documented': bool(assessment and set(assessment['uk_connection_types']) & {'individual_public_location', 'creator_public_location', 'contributor_public_location'}),
            'uk_creator_location_documented': bool(assessment and set(assessment['uk_connection_types']) & {'individual_public_location', 'creator_public_location'}),
            'uk_affiliation_documented': bool(assessment and 'institutional_affiliation' in assessment['uk_connection_types']),
            'location_conflict': bool(assessment and 'conflicting_location' in assessment['uk_connection_types']),
        })
        # Account location is not itself training provenance.
        if (review['location_status'] == 'uk_public_location' and review['account_type_reviewed'] == 'individual') or row['model_id'] in review.get('uk_model_ids', []):
            if assessment is None:
                raise ValueError(f"Missing model-level interpretation: {row['model_id']}")
        merged.append(combined)
    all_fields = list(merged[0])
    views = {
        'models_with_locations': merged,
        'uk_models': [r for r in merged if r['uk_person_location_documented']],
        'uk_creator_models': [r for r in merged if r['uk_creator_location_documented']],
        'uk_connected_models': [r for r in merged if r['uk_connection_types']],
        'uk_affiliated_models': [r for r in merged if r['uk_affiliation_documented']],
        'location_conflict_models': [r for r in merged if r['location_conflict']],
        'location_unknown_models': [r for r in merged if r['publisher_location_status'] == 'unknown'],
    }
    for name, records in views.items():
        write_csv(data / f'{name}.csv', records, all_fields)
    stats.update({
        'reviewed_accounts': len(reviews),
        'account_location_status': dict(collections.Counter(r['location_status'] for r in reviews)),
        'model_publisher_location_status': dict(collections.Counter(r['publisher_location_status'] for r in merged)),
        'reviewed_account_types': dict(collections.Counter(r['account_type_reviewed'] for r in reviews)),
        'derived_view_rows': {k: len(v) for k, v in views.items()},
        'uk_person_location_publishers': len({r['account'] for r in views['uk_models']}),
        'uk_model_assessments': len(assessments),
        'uk_connection_type_model_counts': dict(collections.Counter(t for r in assessments for t in r['uk_connection_types'])),
        'uk_person_location_model_ids': [r['model_id'] for r in views['uk_models']],
        'unknown_account_fraction': sum(r['location_status'] == 'unknown' for r in reviews) / len(reviews),
    })
    dump(data / 'statistics.json', stats)
    print(json.dumps(stats, indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--collection-only', action='store_true')
    parser.add_argument('--review-dir', type=Path, help='Import three completed account-review partitions')
    args = parser.parse_args()
    main(args.collection_only, args.review_dir)

