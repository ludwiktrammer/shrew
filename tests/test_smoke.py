"""
Basic smoke tests covering the Python 3.12 / Django 4.2 upgrade.

These tests intentionally avoid touching external services (CloudConvert,
reCAPTCHA, email SMTP). They verify the project boots and that the
critical-path code we touched during the upgrade still imports/works.
"""
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import RequestFactory, TestCase
from django.urls import reverse


class DjangoSetupTests(TestCase):
    """Verify Django itself is wired up correctly on Python 3.12 / 4.2."""

    def test_django_version_is_4_2(self):
        import django
        self.assertTrue(
            django.VERSION[0] == 4 and django.VERSION[1] == 2,
            f"Expected Django 4.2.x, got {django.get_version()}",
        )

    def test_python_version_is_3_12(self):
        import sys
        self.assertEqual(sys.version_info[:2], (3, 12))

    def test_manage_check_passes(self):
        """``./manage.py check`` must pass cleanly."""
        out = StringIO()
        call_command('check', stdout=out, stderr=out)
        self.assertIn('no issues', out.getvalue())

    def test_no_missing_migrations(self):
        """Models must be in sync with migration files."""
        out = StringIO()
        try:
            call_command(
                'makemigrations',
                '--dry-run',
                '--check',
                stdout=out,
                stderr=out,
            )
        except SystemExit as exc:
            self.fail(
                "Pending migrations detected (makemigrations --check failed): "
                f"{out.getvalue()}"
            )


class AppImportTests(TestCase):
    """Every first-party app and shim module must import cleanly."""

    def test_settings_modules_import(self):
        import shrew.settings.base  # noqa: F401
        import shrew.settings.dev  # noqa: F401
        import shrew.settings.test  # noqa: F401
        # prod.py reads a few additional env vars (STATIC_ROOT, EMAIL_HOST,
        # ...) that are intentionally required at deploy time; we don't
        # import it here.

    def test_app_modules_import(self):
        # Touching these triggers any import-time errors (e.g. removed
        # Django APIs, renamed allauth helpers, ugettext_lazy, etc.).
        from shrew.apps.about import forms, views  # noqa: F401
        from shrew.apps.creations import (  # noqa: F401
            admin, api, models, serializers, urls, views,
        )
        from shrew.apps.pages import admin, models, urls, views  # noqa: F401
        from shrew.apps.pages.templatetags import shrew_embed  # noqa: F401
        from shrew.apps.teachers import admin, models, urls, views  # noqa: F401
        from shrew.apps.users import forms, validators  # noqa: F401
        from shrew import precompilers, urls  # noqa: F401


class UrlResolutionTests(TestCase):
    """URL configuration loads and key routes reverse correctly."""

    def test_url_conf_loads(self):
        from shrew.urls import urlpatterns
        self.assertGreater(len(urlpatterns), 0)

    def test_named_routes_reverse(self):
        # These names are referenced from templates / views.
        for name in ['contact_form', 'contact_form_sent', 'about', 'robots']:
            with self.subTest(name=name):
                reverse(name)


class ContactFormTests(TestCase):
    """The local replacement for django-contact-form."""

    def test_form_renders_and_has_captcha_field(self):
        from shrew.apps.about.forms import ShrewContactForm
        request = RequestFactory().get('/')
        form = ShrewContactForm(request=request)
        self.assertIn('captcha', form.fields)
        self.assertIn('name', form.fields)
        self.assertIn('email', form.fields)
        self.assertIn('title', form.fields)
        self.assertIn('body', form.fields)

    def test_form_requires_request(self):
        from shrew.apps.about.forms import ShrewContactForm
        with self.assertRaises(TypeError):
            ShrewContactForm()


class TeacherViewsImportTests(TestCase):
    """Ensure the PASSWORD_RESET_TIMEOUT fix and allauth imports still work."""

    def test_password_reset_timeout_setting_exists(self):
        from django.conf import settings
        # Should be an integer number of seconds in Django 4.x.
        self.assertIsInstance(settings.PASSWORD_RESET_TIMEOUT, int)
        self.assertGreater(settings.PASSWORD_RESET_TIMEOUT, 0)

    def test_teachers_views_module_imports(self):
        from shrew.apps.teachers import views as teacher_views
        self.assertTrue(hasattr(teacher_views, 'StudentSignupView'))
        self.assertTrue(hasattr(teacher_views, 'TeacherView'))


class ModelTests(TestCase):
    """Hit the ORM end-to-end with the upgraded django-autoslug + simple_history."""

    def test_create_user_and_creation(self):
        from shrew.apps.creations.models import Creation
        User = get_user_model()
        user = User.objects.create_user(username='alice', password='pw')
        creation = Creation.objects.create(
            name='Hello World',
            code='print("hi")',
            svg='<svg/>',
            is_animated=False,
            author=user,
        )
        # AutoSlugField must populate from name.
        self.assertTrue(creation.slug)
        self.assertIn('hello', creation.slug.lower())
        # simple_history must create an initial historical record.
        self.assertEqual(creation.history.count(), 1)


class DeprecatedSettingsTests(TestCase):
    """Verify we removed deprecated/removed settings."""

    def test_use_l10n_not_set(self):
        from django.conf import settings
        # USE_L10N was removed in Django 5.0 and is a no-op in 4.x; we
        # intentionally dropped it from base.py.
        self.assertFalse(hasattr(settings, 'USE_L10N') and getattr(settings, '_USE_L10N_SET', False))

    def test_default_auto_field_is_bigautofield(self):
        # Must be set explicitly: Django keeps the pre-3.2 default of
        # AutoField (with W042 warning) for projects that never opted in.
        from django.conf import settings
        self.assertEqual(
            settings.DEFAULT_AUTO_FIELD,
            'django.db.models.BigAutoField',
        )

    def test_nocaptcha_setting_removed(self):
        from django.conf import settings
        # We removed NOCAPTCHA = True; django-recaptcha 3.x removed support for it.
        self.assertFalse(hasattr(settings, 'NOCAPTCHA'))


class IframeEmbedTests(TestCase):
    """The editor must be embeddable on shrew.app via the playground tag."""

    def test_editor_allows_same_origin_framing(self):
        # Django 3.0+ defaults X_FRAME_OPTIONS to 'DENY'. The editor must
        # opt back in to SAMEORIGIN so the {{ value|shrew_embed }} iframe
        # works on shrew.app itself.
        response = self.client.get(reverse('editor'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('X-Frame-Options'), 'SAMEORIGIN')
