import json
import unittest
try:
    from tools.provider_audit.sealed import new_challenge, seal, unseal
except ModuleNotFoundError as error:
    if error.name.startswith('cryptography'):
        raise unittest.SkipTest('Optional sealed transport dependency not installed')
    raise


class SealedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.private, cls.challenge = new_challenge('123', 'owner/repo')

    def test_round_trip_contains_no_plaintext_credentials(self):
        credentials = {'GEMINI_API_KEYS': 'SENTINEL_PRIVATE_KEY'}
        envelope = seal(credentials, self.challenge)
        self.assertNotIn('SENTINEL_PRIVATE_KEY', json.dumps(envelope))
        self.assertEqual(unseal(envelope, self.private, self.challenge), credentials)

    def test_ciphertext_tampering_is_rejected(self):
        envelope = seal({'HF_API_KEYS': 'sentinel'}, self.challenge)
        data = envelope['ciphertext']
        envelope['ciphertext'] = ('A' if data[0] != 'A' else 'B') + data[1:]
        with self.assertRaises(Exception):
            unseal(envelope, self.private, self.challenge)

    def test_replay_to_another_job_is_rejected(self):
        envelope = seal({'GROQ_API_KEYS': 'sentinel'}, self.challenge)
        with self.assertRaisesRegex(ValueError, 'wrong_job_context'):
            unseal(envelope, self.private, dict(self.challenge, run_id='456'))

    def test_context_is_authenticated_not_just_compared(self):
        envelope = seal({'GROQ_API_KEYS': 'sentinel'}, self.challenge)
        changed = dict(self.challenge, run_id='456')
        envelope['context']['run_id'] = '456'
        with self.assertRaises(Exception):
            unseal(envelope, self.private, changed)

    def test_payload_cannot_enable_generation_or_change_code_execution(self):
        for name in ('AUDIT_MODE', 'GH_TOKEN', 'PYTHONPATH', 'BASH_ENV'):
            with self.assertRaisesRegex(ValueError, 'unsupported_credential_variable'):
                seal({name: 'malicious'}, self.challenge)
