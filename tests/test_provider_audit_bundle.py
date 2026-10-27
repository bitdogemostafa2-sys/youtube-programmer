import unittest
from tools.provider_audit.bundle import unpack
from tools.provider_audit.runner import audit


class BundleTests(unittest.TestCase):
    def test_grouped_markdown_and_multiple_keys(self):
        text = '**Gemini API**\nDUMMY_GEMINI_FIRST\nDUMMY_GEMINI_SECOND\n\n**Groq API**\nDUMMY_GROQ_FIRST\n**Huggface**\nDUMMY_HF_FIRST\n**Inworld AI (TTS)**\nDUMMY_INWORLD_BASE64==\n'
        env, notes = unpack({'PROVIDER_KEYS_BUNDLE': text})
        self.assertEqual(env['GEMINI_API_KEYS'].splitlines(), ['DUMMY_GEMINI_FIRST', 'DUMMY_GEMINI_SECOND'])
        self.assertEqual(env['HF_API_KEYS'], 'DUMMY_HF_FIRST')
        self.assertEqual(env['INWORLD_API_KEYS'], 'DUMMY_INWORLD_BASE64==')
        self.assertEqual(notes, [])

    def test_existing_individual_secret_wins(self):
        env, notes = unpack({'PROVIDER_KEYS_BUNDLE': 'Groq\nDUMMY_BUNDLE_TOKEN', 'GROQ_API_KEYS': 'DUMMY_EXISTING_TOKEN'})
        self.assertEqual(env['GROQ_API_KEYS'], 'DUMMY_EXISTING_TOKEN')
        self.assertEqual(notes, ['bundle_skipped_provider_with_individual_secret:groq'])

    def test_cloudflare_accounts_remain_separate_no_auth_guessing(self):
        first = 'a'*32+':email@example.invalid:DUMMY_GLOBAL_KEY'
        second = 'b'*32+':DUMMY_BEARER_TOKEN'
        env, _ = unpack({'PROVIDER_KEYS_BUNDLE': f'**Cloudflare AI**\n{first} {second}'})
        self.assertEqual(env['CLOUDFLARE_ACCOUNTS'].splitlines(), [first, second])

    def test_inventory_never_generates_and_preserves_order(self):
        seen = []
        def discover(provider, secret):
            seen.append((provider, secret))
            return [], 'test_only'
        report, _ = audit({'PROVIDER_KEYS_BUNDLE': 'Gemini\nDUMMY_FIRST_KEY\nDUMMY_SECOND_KEY'}, {}, discover,
                          lambda *args: self.fail('Generation must not happen'))
        self.assertEqual([key['key_id'] for key in report['keys']], ['GEMINI-01', 'GEMINI-02'])
        self.assertEqual(len(seen), 2)

    def test_all_headings_and_no_secrets_in_notes(self):
        bundle = 'intro text\n**Pexel**\nDUMMY_PEXELS_KEY\n**Unsplash API**\nDUMMY_UNSPLASH_KEY\n**NASA API**\nDUMMY_NASA_KEY\nnot a credential'
        env, notes = unpack({'PROVIDER_KEYS_BUNDLE': bundle})
        for name in ['PEXELS_API_KEYS', 'UNSPLASH_API_KEYS', 'NASA_API_KEYS']:
            self.assertTrue(env[name].startswith('DUMMY_'))
        self.assertNotIn('DUMMY', str(notes))

    def test_size_limit_is_sanitized(self):
        with self.assertRaisesRegex(ValueError, '^bundle_too_large$'):
            unpack({'PROVIDER_KEYS_BUNDLE': 'x'*47001})
