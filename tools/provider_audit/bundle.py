"""One GitHub Secret, grouped by provider headings. Never log the supplied text."""
import re
from .catalog import PROVIDERS

HEADINGS = {
    'gemini': 'gemini', 'gemini api': 'gemini',
    'groq': 'groq', 'groq api': 'groq',
    'cloudflare': 'cloudflare', 'cloudflare ai': 'cloudflare',
    'huggface': 'huggingface', 'hugging face': 'huggingface', 'huggingface': 'huggingface',
    'pexel': 'pexels', 'pexels': 'pexels', 'pexels api': 'pexels',
    'unsplash': 'unsplash', 'unsplash api': 'unsplash',
    'inworld': 'inworld', 'inworld ai': 'inworld', 'inworld ai tts': 'inworld',
    'nasa': 'nasa', 'nasa api': 'nasa',
}


def unpack(environ):
    result = dict(environ)
    bundle = environ.get('PROVIDER_KEYS_BUNDLE', '')
    if not bundle.strip():
        return result, []
    if len(bundle.encode('utf-8')) > 47_000:
        raise ValueError('bundle_too_large')
    groups = {provider: [] for provider in PROVIDERS}
    current = None
    ignored = 0
    for raw in bundle.splitlines():
        line = raw.strip().strip('*`# ').strip()
        if not line:
            continue
        heading = re.sub(r'[^a-z0-9]+', ' ', line.lower()).strip()
        if heading in HEADINGS:
            current = HEADINGS[heading]
            continue
        if current == 'cloudflare' and re.match(r'^[a-fA-F0-9]{32}:', line):
            # Do not guess whether email/global-key credentials are Bearer API tokens.
            # Keep each account separate; discovery will explicitly reject unsupported formats.
            groups[current].extend(re.split(r'\s+(?=[a-fA-F0-9]{32}:)', line))
        elif current and re.fullmatch(r'[A-Za-z0-9_+/=-]{12,4096}', line):
            groups[current].append(line)
        else:
            ignored += 1
    notes = []
    if ignored:
        notes.append(f'bundle_ignored_noncredential_lines:{ignored}')
    for provider, values in groups.items():
        if not values:
            continue
        env = PROVIDERS[provider]
        if result.get(env, '').strip():
            notes.append(f'bundle_skipped_provider_with_individual_secret:{provider}')
        else:
            result[env] = '\n'.join(values)
    return result, notes
