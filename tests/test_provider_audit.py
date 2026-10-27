import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from tools.provider_audit.runner import audit, write_reports
from tools.provider_audit.client import AuditError
from tools.provider_audit.catalog import classification, discover
from unittest.mock import patch


class AuditTests(unittest.TestCase):
    def test_empty_is_not_success(self):
        report, _ = audit({}, {})
        self.assertEqual(report['keys'], [])
        self.assertEqual(report['ready_for_review'], [])

    def test_each_key_separate_no_default_generation(self):
        seen = []
        def discovery(provider, credential):
            seen.append(credential)
            return [dict(id='model', task='text', free_status='unverified', test_status='not_tested')], 'catalog'
        report, _ = audit({'GEMINI_API_KEYS': 'one\ntwo', 'AUDIT_MODE': 'free-tests'}, {}, discovery,
                          lambda *args: self.fail('No free approval'))
        self.assertEqual(seen, ['one', 'two'])
        self.assertEqual(report['keys'][1]['key_id'], 'GEMINI-02')
        self.assertEqual(report['ready_for_review'], [])

    def test_approved_probe_bounded_and_failed_key_reported(self):
        def discovery(provider, key):
            if key == 'bad':
                raise AuditError('authentication_rejected_401')
            return [dict(id='model', task='text', free_status='unverified', test_status='not_tested')], 'catalog'
        policy = dict(max_generation_requests=1, approvals=[dict(provider='gemini', model='model', task='text',
            reviewed_on=date.today().isoformat(), zero_cost_without_credits=True, requires_billing=False,
            pricing_evidence_url='https://example.invalid/reviewed-pricing')])
        report, _ = audit({'GEMINI_API_KEYS': 'bad\none\ntwo', 'AUDIT_MODE': 'free-tests'}, policy,
                          discovery, lambda *args: 'nonempty_test_response')
        self.assertEqual(len(report['ready_for_review']), 1)
        self.assertEqual(report['keys'][2]['models'][0]['test_status'], 'not_tested_request_limit')
        self.assertIn('401', report['keys'][0]['access'])

    def test_exceptions_and_output_do_not_leak_secret(self):
        def discovery(provider, key):
            raise RuntimeError('request URL contains '+key)
        report, secrets = audit({'GROQ_API_KEYS': 'PRIVATE_SENTINEL'}, {}, discovery)
        with tempfile.TemporaryDirectory() as folder:
            write_reports(report, secrets, Path(folder))
            for file in Path(folder).iterdir():
                self.assertNotIn('PRIVATE_SENTINEL', file.read_text())
            self.assertEqual(json.loads((Path(folder)/'candidates.json').read_text()), [])

    def test_cloudflare_email_format_rejected_before_network(self):
        with patch('tools.provider_audit.catalog.request') as request:
            with self.assertRaises(AuditError):
                discover('cloudflare', 'a'*32+':email@example.org:token')
            request.assert_not_called()

    def test_voices_and_unknown_classification(self):
        self.assertEqual(classification('unknown-id'), 'unknown')
        self.assertEqual(classification('whisper-large-v3'), 'transcription')
        with patch('tools.provider_audit.catalog.request', return_value={'voices': [{'voiceId': 'voice-one'}]}):
            rows, _ = discover('inworld', 'not-a-real-key')
        self.assertEqual(rows[0]['kind'], 'voice')
        self.assertEqual(rows[0]['test_status'], 'not_tested')
