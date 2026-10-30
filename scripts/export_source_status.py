"""Export retrieval provenance without copying complete personal profiles."""
import collections
import json
from collect import ROOT, dump, write_csv


def main():
    cards = [json.loads(p.read_text(encoding='utf-8')) for p in sorted((ROOT / 'work/model_cards').glob('*.status.json'))]
    profiles = [json.loads(p.read_text(encoding='utf-8')) for p in sorted((ROOT / 'work/profiles').glob('*.json'))]
    accounts = json.loads((ROOT / 'data/raw/accounts.json').read_text(encoding='utf-8'))
    collection = json.loads((ROOT / 'data/collection.json').read_text(encoding='utf-8'))
    if {p['account'] for p in profiles} != set(accounts) or len(cards) != collection['api_unique']:
        raise ValueError('Incomplete source retrieval provenance')
    write_csv(ROOT / 'data/model_card_sources.csv', cards, ['model_id', 'url', 'status', 'retrieved_at', 'sha256'])
    write_csv(ROOT / 'data/profile_sources.csv', profiles, ['account', 'profile_url', 'api_url', 'api_status', 'html_status', 'retrieved_at'])
    dump(ROOT / 'data/source_retrieval_statistics.json', {
        'model_cards': len(cards), 'model_card_http_status': dict(collections.Counter(p['status'] for p in cards)),
        'profiles': len(profiles), 'profile_html_http_status': dict(collections.Counter(p['html_status'] for p in profiles)),
        'profile_api_http_status': dict(collections.Counter(p['api_status'] for p in profiles)),
    })
    print('Saved retrieval URLs, timestamps, statuses and model-card hashes')


if __name__ == '__main__':
    main()
