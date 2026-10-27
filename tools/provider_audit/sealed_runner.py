"""Explicit, inventory-only audit with a one-use encrypted credential handoff."""
import base64
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, build_opener
from cryptography.hazmat.primitives import serialization
from .client import NoRedirect
from .runner import audit, write_reports, status_summary
from .sealed import new_challenge, unseal, context

HERE = Path(__file__).resolve().parent


def paths():
    root = Path(os.environ['RUNNER_TEMP'])
    return root/'provider-audit-key.pem', root/'provider-audit-challenge.json'


def notice(title, value):
    escaped = value.replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A')
    print(f'::notice title={title}::{escaped}', flush=True)


def prepare():
    key_path, challenge_path = paths()
    private, challenge = new_challenge(os.environ['GITHUB_RUN_ID'], os.environ['GITHUB_REPOSITORY'])
    key_bytes = private.private_bytes(serialization.Encoding.PEM,
                                     serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    with os.fdopen(os.open(key_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'wb') as output:
        output.write(key_bytes)
    challenge_path.write_text(json.dumps(challenge))
    notice('Sealed audit public challenge', json.dumps(challenge, separators=(',', ':')))
    # Actions annotations appear only after the job completes. A separate completed
    # check publishes this PUBLIC challenge while the receiver job is waiting.
    payload = dict(name='sealed-challenge-'+os.environ['GITHUB_RUN_ID'],
                   head_sha=os.environ['GITHUB_SHA'], status='completed', conclusion='success',
                   output=dict(title='Public encryption challenge; not a provider result',
                               summary=json.dumps(challenge, separators=(',', ':'))))
    request = Request('https://api.github.com/repos/'+os.environ['GITHUB_REPOSITORY']+'/check-runs',
                      data=json.dumps(payload).encode(),
                      headers={'Authorization': 'Bearer '+os.environ['GH_TOKEN'],
                               'Accept': 'application/vnd.github+json',
                               'Content-Type': 'application/json',
                               'User-Agent': 'ExplicitSealedProviderAudit/1'})
    with build_opener(NoRedirect()).open(request, timeout=20) as response:
        response.read(100000)


def fetch_envelope(repository, ref):
    url = (f'https://api.github.com/repos/{repository}/contents/'
           f'tools/provider_audit/sealed-request.json?ref={quote(ref, safe="")}')
    request = Request(url, headers={'Authorization': 'Bearer '+os.environ['GH_TOKEN'],
                                   'Accept': 'application/vnd.github+json',
                                   'User-Agent': 'ExplicitSealedProviderAudit/1'})
    try:
        with build_opener(NoRedirect()).open(request, timeout=15) as response:
            raw = response.read(150001)
        if len(raw) > 150000:
            raise ValueError('delivery_too_large')
        body = json.loads(raw)
        return json.loads(base64.b64decode(body['content']))
    except HTTPError as error:
        status = error.code
        error.close()
        if status == 404:
            return None
        raise RuntimeError('delivery_unavailable') from None


def receive():
    key_path, challenge_path = paths()
    private = serialization.load_pem_private_key(key_path.read_bytes(), password=None)
    key_path.unlink()
    challenge = json.loads(challenge_path.read_text())
    challenge_path.unlink()
    config = json.loads((HERE/'sealed-run-request.json').read_text())
    ref = config['delivery_ref']
    if not re.fullmatch(r'arena/[A-Za-z0-9/_-]{1,150}', ref):
        raise ValueError('invalid_delivery_ref')
    repository = os.environ['GITHUB_REPOSITORY']
    deadline = time.monotonic() + 600
    while time.monotonic() < deadline:
        envelope = fetch_envelope(repository, ref)
        if envelope and envelope.get('context') == context(challenge):
            credentials = unseal(envelope, private, challenge)
            del private, envelope
            # Never inherit a generation mode or charge policy from the delivery.
            report, secrets = audit(dict(credentials, AUDIT_MODE='inventory'), {})
            del credentials
            folder = Path('.runtime/provider-audit')
            write_reports(report, secrets, folder)
            del secrets, report
            sanitized = (folder/'report.json').read_bytes()
            publish_report(sanitized)
            safe_report = json.loads(sanitized)
            notice('Provider audit status', status_summary(safe_report))
            return 0 if any(k['access'] == 'read_endpoint_succeeded' for k in safe_report['keys']) else 2
        time.sleep(5)
    raise TimeoutError('encrypted_delivery_timeout')


def publish_report(sanitized):
    packed = base64.b64encode(gzip.compress(sanitized, mtime=0)).decode('ascii')
    if len(packed) > 120000:
        raise ValueError('report_exceeds_annotation_budget_use_artifact')
    # GitHub truncates annotation messages at 4096 characters. Keep ample margin.
    chunks = [packed[i:i+3000] for i in range(0, len(packed), 3000)]
    for index, chunk in enumerate(chunks, 1):
        notice(f'Provider audit report {index}/{len(chunks)}', chunk)
    notice('Provider audit report SHA256', hashlib.sha256(sanitized).hexdigest())


def clean():
    for path in paths():
        path.unlink(missing_ok=True)


def main():
    # No tracebacks: transport/authentication exception strings may contain sensitive data.
    try:
        command = sys.argv[1]
        if command == 'prepare':
            prepare()
        elif command == 'receive':
            raise SystemExit(receive())
        elif command == 'clean':
            clean()
        else:
            raise ValueError('invalid_command')
    except Exception:
        notice('Sealed audit failure', 'Setup, delivery or audit failed; no raw error details are logged.')
        raise SystemExit(2) from None


if __name__ == '__main__':
    main()
