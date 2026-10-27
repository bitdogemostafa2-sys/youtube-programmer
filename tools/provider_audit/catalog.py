"""Discovery is not price verification, account entitlement, or a successful generation."""
import re
from urllib.parse import urlencode
from .client import request, AuditError

PROVIDERS = {
    'gemini': 'GEMINI_API_KEYS', 'groq': 'GROQ_API_KEYS',
    'cloudflare': 'CLOUDFLARE_ACCOUNTS', 'huggingface': 'HF_API_KEYS',
    'pexels': 'PEXELS_API_KEYS', 'unsplash': 'UNSPLASH_API_KEYS',
    'inworld': 'INWORLD_API_KEYS', 'nasa': 'NASA_API_KEYS',
}
TASKS = {
    'text': 'كتابة نصوص واسكربتات', 'image': 'توليد الصور', 'video': 'توليد الفيديو',
    'tts': 'تعليق صوتي', 'sfx': 'مؤثرات صوتية', 'transcription': 'تفريغ صوت',
    'embedding': 'تمثيل نصي للبحث؛ ليس توليد محتوى', 'unknown': 'غير محسوم',
    'source': 'مصدر مواد جاهزة؛ ليس موديل توليد',
}


def classification(identifier, task=''):
    value = (identifier+' '+str(task)).lower()
    for pattern, result in [
        ('text-to-speech|text_to_speech|tts|orpheus', 'tts'),
        ('automatic-speech-recognition|whisper|speech-to-text', 'transcription'),
        ('text-to-video|veo', 'video'), ('text-to-image|imagen|flux|stable-diffusion|image-generation|gemini[^ ]*-image', 'image'),
        ('sound-effect|text-to-audio', 'sfx'), ('embedding|embed-', 'embedding'),
        ('text-generation|llama|gemma|qwen|gpt-oss|gemini', 'text'),
    ]:
        if re.search(pattern, value):
            return result
    return 'unknown'


def model(identifier, task='', kind='model', **extra):
    if not isinstance(identifier, str) or not re.fullmatch(r'[A-Za-z0-9_/@:.-]{1,180}', identifier):
        return None
    return dict(id=identifier, kind=kind, task=classification(identifier, task),
                classification_basis='provider_task_or_name_inference_not_a_functional_test',
                free_status='unverified', test_status='not_tested', **extra)


def discover(provider, credential):
    bearer = {'Authorization': 'Bearer '+credential}
    if provider == 'gemini':
        rows, page = [], ''
        for _ in range(5):
            query = {'pageSize': 1000}
            if page:
                query['pageToken'] = page
            data = request('https://generativelanguage.googleapis.com/v1beta/models?'+urlencode(query),
                           {'x-goog-api-key': credential})
            rows.extend(model(x.get('name'), methods=x.get('supportedGenerationMethods', []))
                        for x in data.get('models', []))
            page = data.get('nextPageToken', '')
            if not page:
                return rows, 'catalog_only_not_account_entitlement'
        return rows, 'partial_catalog_page_limit'
    if provider == 'groq':
        data = request('https://api.groq.com/openai/v1/models', bearer)
        return [model(x.get('id')) for x in data.get('data', [])], 'catalog_only'
    if provider == 'cloudflare':
        parts = credential.split(':')
        if len(parts) != 2 or not re.fullmatch(r'[a-fA-F0-9]{32}', parts[0]) or not parts[1]:
            raise AuditError('expected_ACCOUNT_ID_colon_API_TOKEN_no_email')
        account, token = parts
        rows = []
        for page in range(1, 6):
            data = request(f'https://api.cloudflare.com/client/v4/accounts/{account}/ai/models/search?per_page=100&page={page}',
                           {'Authorization': 'Bearer '+token})
            if not data.get('success'):
                raise AuditError('cloudflare_catalog_rejected')
            result = data.get('result', [])
            rows.extend(model(x.get('name'), x.get('task', {})) for x in result)
            total = data.get('result_info', {}).get('total_pages')
            if (total is not None and page >= total) or (total is None and len(result) < 100):
                return rows, 'catalog_only_not_free_tier_confirmation'
        return rows, 'partial_catalog_page_limit'
    if provider == 'huggingface':
        request('https://huggingface.co/api/whoami-v2', bearer)
        return [], 'authentication_only_hub_models_are_not_account_scoped_free_inference_models'
    if provider == 'inworld':
        data = request('https://api.inworld.ai/tts/v1/voices', {'Authorization': 'Basic '+credential})
        rows = []
        for item in data.get('voices', []):
            row = model(item.get('voiceId') or item.get('id'), kind='voice')
            if row:
                row.update(task='tts', classification_basis='tts_voice_endpoint_not_speech_test')
            rows.append(row)
        return rows, 'voice_inventory_only_no_audio_generated'
    if provider == 'pexels':
        request('https://api.pexels.com/v1/search?query=nature&per_page=1', {'Authorization': credential})
        return [dict(id='photo-search', kind='source', task='source', free_status='unverified',
                     test_status='read_request_succeeded', scope='photo_search_only_not_video_or_download')], 'not_a_model_provider'
    if provider == 'unsplash':
        request('https://api.unsplash.com/search/photos?query=nature&per_page=1', {'Authorization': 'Client-ID '+credential})
        return [dict(id='photo-search', kind='source', task='source', free_status='unverified',
                     test_status='read_request_succeeded', scope='search_only_not_download')], 'not_a_model_provider'
    if provider == 'nasa':
        request('https://api.nasa.gov/planetary/apod?'+urlencode({'api_key': credential, 'date': '2024-01-01'}))
        return [dict(id='APOD', kind='source', task='source', free_status='unverified',
                     test_status='read_request_succeeded', scope='APOD_only')], 'not_a_model_provider'
    raise AuditError('unsupported_provider')
