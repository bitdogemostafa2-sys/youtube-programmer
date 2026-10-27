"""Bounded HTTPS, fixed hosts, no redirects/retries, sanitized failures."""
import json
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError, URLError

HOSTS = {
    'generativelanguage.googleapis.com', 'api.groq.com', 'api.cloudflare.com',
    'huggingface.co', 'api.pexels.com', 'api.unsplash.com', 'api.inworld.ai', 'api.nasa.gov',
}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class AuditError(Exception):
    pass


def request(url, headers=None, body=None):
    from urllib.parse import urlparse
    parsed = urlparse(url)
    if parsed.scheme != 'https' or parsed.hostname not in HOSTS or parsed.username or parsed.port not in (None, 443):
        raise AuditError('endpoint_not_allowed')
    headers = dict(headers or {})
    headers['User-Agent'] = 'YoutubeProgrammer-ExplicitAudit/1'
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers['Content-Type'] = 'application/json'
    try:
        with build_opener(NoRedirect()).open(Request(url, data=data, headers=headers), timeout=20) as response:
            raw = response.read(4_000_001)
            if len(raw) > 4_000_000:
                raise AuditError('response_too_large_no_retry')
            try:
                return json.loads(raw)
            except (ValueError, UnicodeError):
                raise AuditError('invalid_json_response') from None
    except HTTPError as error:
        status = error.code
        error.close()
        label = {401: 'authentication_rejected', 402: 'payment_required',
                 403: 'access_rejected', 429: 'quota_or_rate_limit'}.get(status, 'http_error')
        raise AuditError(f'{label}_{status}') from None
    except (URLError, TimeoutError, OSError):
        raise AuditError('network_or_timeout_no_retry') from None
