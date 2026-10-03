"""Coverage for what v1 shipped with zero: routes resolving, the contact
and newsletter flows (validation, persistence, email-failure resilience),
the public API, security headers, and the legacy-URL guarantees (anchors,
redirects) this rebuild promised to keep."""

from unittest.mock import patch

from django.core import mail
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .forms import ProjectIntakeForm
from .models import CaseStudy, ContactSubmission, GeneratedAsset, Post, Subscriber
from .services_data import SERVICE_ORDER


def _case(**over):
    data = dict(slug='test-case', client='Test Client', title='A title', sector='Testing',
               summary='Summary.', problem='Problem.', system='System.', implementation='Impl.',
               outcome='Outcome.', layers=['product'], services=['software-development'],
               featured=True, is_published=True)
    data.update(over)
    return CaseStudy.objects.create(**data)


def _post(**over):
    data = dict(slug='test-post', title='A Test Post', dek='A dek.', topic='security',
               body='# Heading\n\nSome *markdown* body.\n\n## Sub\n\nMore text.',
               is_published=True)
    data.update(over)
    return Post.objects.create(**data)


class StaticRoutesTests(TestCase):
    """Every page renders, and nothing 500s."""

    def setUp(self):
        self.client = Client()
        _case()
        _post()

    def test_core_pages_200(self):
        for name in ['home', 'about', 'services', 'projects', 'contact', 'privacy', 'blog']:
            with self.subTest(name=name):
                resp = self.client.get(reverse(name))
                self.assertEqual(resp.status_code, 200)

    def test_every_service_detail_page_200(self):
        for slug in SERVICE_ORDER:
            with self.subTest(slug=slug):
                resp = self.client.get(reverse('service_detail', kwargs={'slug': slug}))
                self.assertEqual(resp.status_code, 200)
                self.assertContains(resp, 'Capabilities')

    def test_unknown_service_404(self):
        resp = self.client.get('/services/not-a-real-service/')
        self.assertEqual(resp.status_code, 404)

    def test_case_study_detail_200(self):
        case = _case(slug='another-case')
        resp = self.client.get(case.get_absolute_url())
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, case.client)

    def test_unpublished_case_study_404(self):
        case = _case(slug='hidden-case', is_published=False)
        resp = self.client.get(case.get_absolute_url())
        self.assertEqual(resp.status_code, 404)

    def test_post_detail_renders_markdown(self):
        post = _post(slug='markdown-post', body='# Hi\n\nSome `code` and a [link](https://example.com).')
        resp = self.client.get(post.get_absolute_url())
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '<h1')
        self.assertContains(resp, '<code>')

    def test_work_redirects_to_projects(self):
        resp = self.client.get('/work/')
        self.assertRedirects(resp, reverse('projects'), status_code=301)

    def test_sitemap_and_robots(self):
        self.assertEqual(self.client.get('/sitemap.xml').status_code, 200)
        self.assertEqual(self.client.get('/robots.txt').status_code, 200)
        self.assertEqual(self.client.get('/.well-known/security.txt').status_code, 200)

    def test_404_page(self):
        resp = self.client.get('/this-page-does-not-exist/')
        self.assertEqual(resp.status_code, 404)


class LegacyUrlTests(TestCase):
    """v1 anchors must keep landing in the right place — the rebuild
    promised no broken inbound links."""

    def setUp(self):
        _case(slug='legacy-case', legacy_anchor='proj-legacytest')

    def test_services_layer_anchors_present(self):
        resp = self.client.get(reverse('services'))
        html = resp.content.decode()
        for anchor_id in ['web-dev', 'crm', 'devops', 'api', 'security']:
            with self.subTest(anchor_id=anchor_id):
                self.assertIn(f'id="{anchor_id}"', html)

    def test_project_legacy_anchor_present(self):
        resp = self.client.get(reverse('projects'))
        self.assertContains(resp, 'id="proj-legacytest"')


class ContactFormTests(TestCase):
    def test_only_name_email_message_required(self):
        form = ProjectIntakeForm(data={'name': 'A', 'email': 'a@example.com', 'message': 'A real message here.'})
        self.assertTrue(form.is_valid(), form.errors)

    def test_short_message_rejected(self):
        form = ProjectIntakeForm(data={'name': 'A', 'email': 'a@example.com', 'message': 'hi'})
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)

    def test_missing_name_and_bad_email_rejected(self):
        form = ProjectIntakeForm(data={'name': '', 'email': 'not-an-email', 'message': 'A real message here.'})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('email', form.errors)

    def test_honeypot_marks_spam(self):
        form = ProjectIntakeForm(data={'name': 'Bot', 'email': 'a@example.com', 'message': 'spam message here',
                                       'website': 'http://spam.example'})
        self.assertTrue(form.is_valid())
        self.assertTrue(form.is_spam)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ContactSubmissionFlowTests(TestCase):
    def _post(self, **over):
        data = {'name': 'Jamie', 'email': 'jamie@example.com', 'message': 'A real project brief, long enough.'}
        data.update(over)
        return self.client.post(reverse('contact'), data)

    def test_valid_submission_saves_and_redirects_and_emails_both_sides(self):
        resp = self._post()
        self.assertRedirects(resp, reverse('contact_thanks'))
        sub = ContactSubmission.objects.get(email='jamie@example.com')
        self.assertEqual(sub.name, 'Jamie')
        self.assertEqual(len(mail.outbox), 2)  # staff notification + sender auto-reply

    def test_invalid_submission_rerenders_with_errors_no_save(self):
        resp = self._post(email='not-an-email')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(ContactSubmission.objects.filter(name='Jamie').exists())

    def test_honeypot_pretends_success_but_saves_nothing(self):
        resp = self._post(website='http://spam.example')
        self.assertRedirects(resp, reverse('contact'))
        self.assertFalse(ContactSubmission.objects.filter(email='jamie@example.com').exists())

    def test_email_failure_still_saves_the_submission(self):
        with patch('business_page.intake.send_mail', side_effect=OSError('smtp down')):
            resp = self._post(email='resilient@example.com')
        self.assertRedirects(resp, reverse('contact_thanks'))
        self.assertTrue(ContactSubmission.objects.filter(email='resilient@example.com').exists())

    def test_api_intake_mirrors_html_validation(self):
        resp = self.client.post(reverse('api_intake'), data={'name': '', 'email': 'bad', 'message': 'hi'},
                                content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        body = resp.json()
        self.assertIn('name', body['errors'])
        self.assertIn('email', body['errors'])
        self.assertIn('message', body['errors'])

    def test_api_intake_valid_returns_201(self):
        resp = self.client.post(reverse('api_intake'), data={
            'name': 'API', 'email': 'api@example.com', 'message': 'A real brief via the API.',
        }, content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(resp.json()['ok'])


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class NewsletterTests(TestCase):
    def test_subscribe_creates_unconfirmed_subscriber_and_sends_confirmation(self):
        resp = self.client.post(reverse('newsletter_signup'), {'email': 'sub@example.com', 'next': '/blog/'})
        self.assertRedirects(resp, '/blog/')
        sub = Subscriber.objects.get(email='sub@example.com')
        self.assertFalse(sub.is_active)
        self.assertEqual(len(mail.outbox), 1)

    def test_confirm_activates_subscriber(self):
        sub = Subscriber.objects.create(email='confirm@example.com')
        resp = self.client.get(reverse('newsletter_confirm', kwargs={'token': sub.token}))
        self.assertEqual(resp.status_code, 200)
        sub.refresh_from_db()
        self.assertTrue(sub.is_active)

    def test_unsubscribe_deactivates(self):
        sub = Subscriber.objects.create(email='unsub@example.com')
        sub.confirmed_at = sub.created_at
        sub.save()
        self.client.get(reverse('newsletter_unsubscribe', kwargs={'token': sub.token}))
        sub.refresh_from_db()
        self.assertFalse(sub.is_active)

    def test_bad_token_404s(self):
        resp = self.client.get(reverse('newsletter_confirm', kwargs={'token': 'not-a-real-token'}))
        self.assertEqual(resp.status_code, 404)

    def test_honeypot_silently_no_ops(self):
        self.client.post(reverse('newsletter_signup'), {'email': 'spam@example.com', 'website': 'http://spam.example'})
        self.assertFalse(Subscriber.objects.filter(email='spam@example.com').exists())


class SecurityHeadersTests(TestCase):
    def test_headers_present_on_every_response(self):
        resp = self.client.get(reverse('home'))
        self.assertIn('Content-Security-Policy', resp)
        self.assertIn("'nonce-", resp['Content-Security-Policy'])
        self.assertNotIn('unsafe-inline', resp['Content-Security-Policy'].split('script-src')[1].split(';')[0])
        self.assertEqual(resp['X-Frame-Options'], 'DENY')
        self.assertEqual(resp['X-Content-Type-Options'], 'nosniff')

    @override_settings(DEBUG=False, SECURE_HSTS_SECONDS=31536000, ALLOWED_HOSTS=['testserver'])
    def test_hsts_sent_in_production_mode(self):
        # HSTS is deliberately OFF in DEBUG (dev/test over plain HTTP should
        # never tell a browser to force HTTPS) and ON once DEBUG=False, via
        # Django's own SecurityMiddleware — not a hand-written header.
        resp = self.client.get(reverse('home'), secure=True)
        self.assertIn('Strict-Transport-Security', resp)
        self.assertIn('max-age=31536000', resp['Strict-Transport-Security'])

    def test_nonce_is_unique_per_request(self):
        r1 = self.client.get(reverse('home'))
        r2 = self.client.get(reverse('home'))
        n1 = r1['Content-Security-Policy'].split("nonce-")[1].split("'")[0]
        n2 = r2['Content-Security-Policy'].split("nonce-")[1].split("'")[0]
        self.assertNotEqual(n1, n2)


class ApiReadEndpointTests(TestCase):
    def setUp(self):
        _case()
        _post()

    def test_services_index(self):
        body = self.client.get(reverse('api_services')).json()
        self.assertEqual(len(body['layers']), 5)

    def test_projects_index_and_detail(self):
        body = self.client.get(reverse('api_projects')).json()
        slugs = [r['slug'] for r in body['results']]
        self.assertIn('test-case', slugs)  # plus the migration-seeded case studies
        detail = self.client.get(reverse('api_project_detail', kwargs={'slug': 'test-case'})).json()
        self.assertEqual(detail['client'], 'Test Client')

    def test_posts_index(self):
        body = self.client.get(reverse('api_posts')).json()
        slugs = [r['slug'] for r in body['results']]
        self.assertIn('test-post', slugs)  # plus the migration-seeded articles

    def test_search_index_covers_all_content_types(self):
        body = self.client.get(reverse('api_search_index')).json()
        groups = {item['group'] for item in body['items']}
        self.assertTrue({'Pages', 'Capabilities', 'Work', 'Journal', 'Contact'} <= groups)


class HiggsfieldWebhookTests(TestCase):
    @override_settings(HIGGSFIELD_WEBHOOK_TOKEN='test-token')
    def test_wrong_token_forbidden(self):
        resp = self.client.post('/api/v1/hooks/higgsfield/wrong-token/', data='{}',
                                content_type='application/json')
        self.assertEqual(resp.status_code, 403)

    @override_settings(HIGGSFIELD_WEBHOOK_TOKEN='test-token')
    def test_unknown_request_id_404(self):
        resp = self.client.post('/api/v1/hooks/higgsfield/test-token/',
                                data='{"request_id": "does-not-exist", "status": "completed"}',
                                content_type='application/json')
        self.assertEqual(resp.status_code, 404)

    @override_settings(HIGGSFIELD_WEBHOOK_TOKEN='test-token')
    def test_valid_webhook_updates_asset(self):
        asset = GeneratedAsset.objects.create(slot='test.slot', model_slug='x/y', prompt='p',
                                              request_id='req-123', status='queued')
        resp = self.client.post('/api/v1/hooks/higgsfield/test-token/',
                                data='{"request_id": "req-123", "status": "completed", "video": {"url": "https://example.com/v.mp4"}}',
                                content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        asset.refresh_from_db()
        self.assertEqual(asset.status, 'completed')
        self.assertEqual(asset.result_url, 'https://example.com/v.mp4')
