import unittest
from tools.provider_audit.runner import audit, status_summary


class StatusTests(unittest.TestCase):
    def test_missing_credentials_are_explicit_without_network(self):
        def forbidden(*args):
            self.fail('Empty credentials must not make requests')
        report, _ = audit({}, {}, forbidden, forbidden)
        self.assertEqual(status_summary(report),
                         'credentials_examined=0; read_endpoints_succeeded=0; '
                         'functional_candidates=0; unconfigured_providers=8; configuration_errors=0')

    def test_untrusted_fields_never_enter_annotation(self):
        sentinel = 'SECRET%0A::error::INJECTED'
        report = dict(keys=[dict(key_id=sentinel, access=sentinel, models=[sentinel])],
                      ready_for_review=[], not_configured=[sentinel])
        summary = status_summary(report)
        self.assertNotIn(sentinel, summary)
        self.assertNotIn('::', summary)
        self.assertIn('credentials_examined=1;', summary)

    def test_config_error_is_not_counted_as_a_tested_key(self):
        report, _ = audit({'GROQ_API_KEYS': '\n'.join(['fake'] * 21)}, {})
        summary = status_summary(report)
        self.assertIn('credentials_examined=0;', summary)
        self.assertIn('configuration_errors=1', summary)
