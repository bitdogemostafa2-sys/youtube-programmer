"""One-job credential envelopes: RSA-OAEP-SHA256 + AES-256-GCM.

Only ciphertext may be transported through the public repository. The private
key belongs to a single ephemeral CI job; it is never returned to the sender.
"""
import base64
import json
import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from .catalog import PROVIDERS


def encoded(value):
    return base64.b64encode(value).decode('ascii')


def decoded(value):
    return base64.b64decode(value, validate=True)


def context(challenge):
    return {k: challenge[k] for k in ('version', 'run_id', 'repository', 'nonce')}


def associated_data(challenge):
    return json.dumps(context(challenge), sort_keys=True, separators=(',', ':')).encode()


def oaep():
    return padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None)


def new_challenge(run_id, repository):
    private = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    challenge = dict(version=1, run_id=str(run_id), repository=repository,
                     nonce=encoded(os.urandom(32)), public_key=private.public_key().public_bytes(
                         serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode())
    return private, challenge


def validate_credentials(credentials):
    if not isinstance(credentials, dict) or not credentials:
        raise ValueError('invalid_credential_mapping')
    if set(credentials) - set(PROVIDERS.values()):
        raise ValueError('unsupported_credential_variable')
    if any(not isinstance(v, str) or len(v.encode()) > 47000 for v in credentials.values()):
        raise ValueError('invalid_credential_value')
    if len(json.dumps(credentials).encode()) > 64000:
        raise ValueError('credentials_too_large')


def seal(credentials, challenge):
    validate_credentials(credentials)
    public = serialization.load_pem_public_key(challenge['public_key'].encode())
    if not isinstance(public, rsa.RSAPublicKey) or public.key_size < 3072:
        raise ValueError('invalid_public_key')
    key, nonce = AESGCM.generate_key(bit_length=256), os.urandom(12)
    ciphertext = AESGCM(key).encrypt(nonce, json.dumps(credentials).encode(), associated_data(challenge))
    return dict(context=context(challenge), wrapped_key=encoded(public.encrypt(key, oaep())),
                iv=encoded(nonce), ciphertext=encoded(ciphertext))


def unseal(envelope, private, challenge):
    if envelope.get('context') != context(challenge):
        raise ValueError('wrong_job_context')
    if len(json.dumps(envelope)) > 100000:
        raise ValueError('envelope_too_large')
    key = private.decrypt(decoded(envelope['wrapped_key']), oaep())
    plaintext = AESGCM(key).decrypt(decoded(envelope['iv']), decoded(envelope['ciphertext']),
                                    associated_data(challenge))
    credentials = json.loads(plaintext)
    validate_credentials(credentials)
    return credentials
