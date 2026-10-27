"""Explicitly reviewed zero-cost text probes only. No inference from a free API key."""
from datetime import date
from urllib.parse import quote
from .client import request, AuditError


def approved(policy, provider, row):
    if provider not in ('gemini', 'groq') or row.get('task') != 'text':
        return False
    for entry in policy.get('approvals', []):
        if (entry.get('provider'), entry.get('model'), entry.get('task')) != (provider, row['id'], 'text'):
            continue
        try:
            age = (date.today()-date.fromisoformat(entry['reviewed_on'])).days
        except (ValueError, KeyError, TypeError):
            continue
        if (0 <= age <= 7 and entry.get('zero_cost_without_credits') is True
                and entry.get('requires_billing') is False
                and str(entry.get('pricing_evidence_url', '')).startswith('https://')):
            return True
    return False


def probe(provider, credential, row):
    prompt = 'Reply with exactly: OK'
    if provider == 'gemini':
        identifier = row['id'].removeprefix('models/')
        data = request('https://generativelanguage.googleapis.com/v1beta/models/'+quote(identifier, safe='')+':generateContent',
                       {'x-goog-api-key': credential},
                       {'contents': [{'parts': [{'text': prompt}]}], 'generationConfig': {'maxOutputTokens': 32}})
        text = ''.join(p.get('text', '') for c in data.get('candidates', [])
                       for p in c.get('content', {}).get('parts', []))
    elif provider == 'groq':
        data = request('https://api.groq.com/openai/v1/chat/completions',
                       {'Authorization': 'Bearer '+credential},
                       {'model': row['id'], 'messages': [{'role': 'user', 'content': prompt}], 'max_tokens': 32})
        text = ''.join(c.get('message', {}).get('content') or '' for c in data.get('choices', []))
    else:
        raise AuditError('probe_not_implemented')
    if not text.strip():
        raise AuditError('empty_text_output')
    return 'nonempty_text_response_not_a_quality_or_safety_certification'
