"""Structural checks only: a valid report does not establish factual accuracy."""
import json
import re
import sys


def words(text):
    return len(re.findall(r"\b[\w]+(?:[-'][\w]+)*\b", text))


def audit(source, delivery):
    errors = []
    if words(source['brief']) > 1500:
        errors.append('Brief exceeds the 1500-word pilot limit.')
    titles = delivery.get('titles', [])
    if len(titles) != 3 or not all(isinstance(t, str) and t.strip() for t in titles):
        errors.append('Provide exactly three non-empty titles.')
    for key, limit in [('script', 600), ('description', 150)]:
        value = delivery.get(key, '')
        if not isinstance(value, str) or not value.strip():
            errors.append('Missing ' + key)
        elif words(value) > limit:
            errors.append(key + ' exceeds ' + str(limit) + ' words.')
    claims = delivery.get('claim_map', [])
    if not claims:
        errors.append('Missing claim map.')
    for item in claims:
        if not item.get('claim') or not item.get('source_ids'):
            errors.append('Every mapped claim needs text and source IDs.')
        for source_id in item.get('source_ids', []):
            if source_id not in source['facts']:
                errors.append('Unknown source ID: ' + source_id)
    return {'structural_errors': errors,
            'script_words': words(delivery.get('script', '')),
            'description_words': words(delivery.get('description', '')),
            'semantic_review_required': True,
            'review': ['Read each claim against the cited fact.',
                       'Check numbers, exclusions and implied promises.',
                       'Read aloud; review hook, transitions and CTA.']}


if __name__ == '__main__':
    source = json.load(open(sys.argv[1], encoding='utf-8'))
    delivery = json.load(open(sys.argv[2], encoding='utf-8'))
    report = audit(source, delivery)
    print(json.dumps(report, indent=2))
    sys.exit(bool(report['structural_errors']))
