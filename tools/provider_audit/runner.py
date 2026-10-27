"""Run only on explicit request. Output contains aliases, never keys/account IDs or raw bodies."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from .catalog import PROVIDERS, TASKS, discover
from .client import AuditError
from .probes import approved, probe


HERE = Path(__file__).resolve().parent


def audit(environ, policy, discover_fn=discover, probe_fn=probe):
    mode = environ.get('AUDIT_MODE', 'inventory')
    if mode not in ('inventory', 'free-tests'):
        raise ValueError('invalid_audit_mode')
    report = {'time_utc': datetime.now(timezone.utc).isoformat(), 'mode': mode,
              'keys': [], 'not_configured': [], 'ready_for_review': [],
              'scope': 'Discovery is not a functional test or a free-tier guarantee. No automatic app import.'}
    secrets = []
    budget = max(0, min(int(policy.get('max_generation_requests', 0)), 20))
    for provider, env in PROVIDERS.items():
        values = [value.strip() for value in environ.get(env, '').splitlines() if value.strip()]
        if not values:
            report['not_configured'].append(provider)
        if len(values) > 20:
            report['keys'].append({'key_id': provider.upper()+'-CONFIG', 'provider': provider,
                                   'access': 'too_many_keys_limit_20', 'models': []})
            continue
        for number, credential in enumerate(values, 1):
            secrets.append(credential)
            if provider == 'cloudflare':
                secrets.extend(credential.split(':'))
            item = {'key_id': f'{provider.upper()}-{number:02}', 'provider': provider,
                    'access': 'not_tested', 'models': []}
            report['keys'].append(item)
            try:
                rows, note = discover_fn(provider, credential)
                item.update(access='read_endpoint_succeeded', note=note,
                            models=[r for r in rows if r])
                for row in item['models']:
                    row['task_label_ar'] = TASKS.get(row.get('task'), TASKS['unknown'])
                    if not approved(policy, provider, row):
                        row['eligibility'] = 'excluded_until_free_status_and_probe_are_reviewed'
                        continue
                    row['free_status'] = 'manual_zero_cost_policy_review_not_live_billing_verification'
                    if mode != 'free-tests':
                        continue
                    if not budget:
                        row['test_status'] = 'not_tested_request_limit'
                        continue
                    budget -= 1
                    try:
                        row['test_detail'] = probe_fn(provider, credential, row)
                        row['test_status'] = 'probe_succeeded'
                        report['ready_for_review'].append({'key_id': item['key_id'], 'provider': provider,
                                                          'model': row['id'], 'task': row['task']})
                    except AuditError as error:
                        row['test_status'] = str(error)
            except AuditError as error:
                item['access'] = str(error)
            except Exception:
                # Never echo exceptions containing URL query strings or provider response bodies.
                item['access'] = 'unexpected_response_or_configuration_no_raw_details'
    return report, secrets


def redact(text, secrets):
    for secret in sorted(set(secrets), key=len, reverse=True):
        if secret:
            text = text.replace(secret, '[REDACTED]')
    return text


def write_reports(report, secrets, folder):
    folder.mkdir(parents=True, exist_ok=True)
    payload = redact(json.dumps(report, ensure_ascii=False, indent=2), secrets)
    (folder/'report.json').write_text(payload+'\n', encoding='utf-8')
    lines = ['# تقرير المفاتيح والموديلات', '', f"التوقيت: {report['time_utc']}",
             '', 'المعرّفات مثل GEMINI-01 تشير إلى ترتيب الأسطر في Secret الخاص بالمزوّد، وليس قيمة المفتاح.',
             'التصنيف من بيانات المزوّد أو الاسم قد يكون استدلاليًا، وليس اختبارًا لقدرة الموديل.',
             'قائمة المرشحين لا تعني ضمان المجانية الدائم، ولا استيرادًا تلقائيًا إلى البرنامج.', '']
    if not report['keys']:
        lines.append('**لم توجد مفاتيح مهيأة؛ لم يُختبر أي مفتاح أو موديل.**')
    for key in report['keys']:
        lines += [f"## {key['key_id']}", f"فحص الوصول: `{key['access']}`", f"نطاق الفحص: `{key.get('note', '')}`",
                  '', '| الموديل/المصدر/الصوت | التصنيف | المجانية | الاختبار |', '|---|---|---|---|']
        for row in key['models']:
            cells = [row['id'], row.get('task_label_ar', ''), row['free_status'], row['test_status']]
            lines.append('| '+' | '.join(str(c).replace('|', '/').replace('\n', ' ') for c in cells)+' |')
        if not key['models']:
            lines.append('لا قائمة موديلات مؤكدة لهذا المفتاح ضمن الفحص الحالي.')
        lines.append('')
    lines += ['## ما اجتاز الطلب الوظيفي والسياسة المراجعة',
              f"عدد المرشحين للمراجعة: {len(report['ready_for_review'])}",
              '', 'غير المهيأ: '+', '.join(report['not_configured'])]
    (folder/'report.md').write_text(redact('\n'.join(lines)+'\n', secrets), encoding='utf-8')
    (folder/'candidates.json').write_text(redact(json.dumps(report['ready_for_review'], ensure_ascii=False, indent=2), secrets)+'\n', encoding='utf-8')


def main():
    policy = json.loads((HERE/'free_policy.json').read_text(encoding='utf-8'))
    report, secrets = audit(os.environ, policy)
    write_reports(report, secrets, Path('.runtime/provider-audit'))
    successes = sum(k['access'] == 'read_endpoint_succeeded' for k in report['keys'])
    print(f"Keys examined: {len(report['keys'])}; read endpoints succeeded: {successes}; functional candidates: {len(report['ready_for_review'])}")
    if not successes:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
