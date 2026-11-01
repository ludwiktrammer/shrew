from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import shutil
import stat
import struct
import subprocess
import tempfile
import threading
import time
from types import SimpleNamespace
from unittest import mock, skipUnless
import zlib

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.template.loader import render_to_string
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from shrew.apps.creations.models import Creation
from shrew.apps.creations.previews import (
    PreviewRenderError, get_social_preview_url, social_preview_key, social_preview_svg,
)


SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
       '<circle cx="50" cy="50" r="40" fill="red"/></svg>')


def png_fixture():
    def chunk(kind, data):
        return (struct.pack('>I', len(data)) + kind + data
                + struct.pack('>I', zlib.crc32(kind + data)))
    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('>IIBBBBB', 1200, 630, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress((b'\0' + b'\xff\0\0\xff' * 1200) * 630))
            + chunk(b'IEND', b''))


PNG = png_fixture()


class PreviewStorageTests(SimpleTestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        override = self.settings(MEDIA_ROOT=self.directory.name, MEDIA_URL='/media/')
        override.enable()
        self.addCleanup(override.disable)
        self.creation = SimpleNamespace(svg=SVG, is_animated=False)

    def output_path(self, url):
        return Path(self.directory.name) / url.removeprefix('/media/')

    def test_framing_and_play_overlay(self):
        self.assertIn('viewBox="-45.25 0 190.5 100"', social_preview_svg(self.creation))
        overlay = render_to_string('creations/_play.svg')
        self.assertNotIn(overlay, social_preview_svg(self.creation))
        self.creation.is_animated = True
        prepared = social_preview_svg(self.creation)
        self.assertIn(overlay, prepared)
        self.assertEqual(prepared.count('</svg>'), 1)
        self.assertEqual(self.creation.svg, SVG)

    @mock.patch('shrew.apps.creations.previews.subprocess.run')
    def test_saved_png_survives_cache_clear_without_rendering_again(self, run):
        run.return_value.stdout = PNG
        url = get_social_preview_url(self.creation)
        cache.clear()
        self.assertEqual(get_social_preview_url(self.creation), url)
        self.assertEqual(run.call_count, 1)
        self.assertEqual(self.output_path(url).read_bytes(), PNG)
        self.assertEqual(stat.S_IMODE(self.output_path(url).stat().st_mode), 0o644)
        self.assertEqual(run.call_args.kwargs['input'], social_preview_svg(self.creation).encode())
        self.assertEqual(run.call_args.kwargs['timeout'], 10)

    @mock.patch('shrew.apps.creations.previews._render_png', return_value=PNG)
    def test_content_and_animation_changes_produce_new_files(self, render):
        original = get_social_preview_url(self.creation)
        self.creation.svg = SVG.replace('red', 'blue')
        changed = get_social_preview_url(self.creation)
        self.creation.is_animated = True
        animated = get_social_preview_url(self.creation)
        self.assertEqual(len({original, changed, animated}), 3)
        self.assertTrue(all(self.output_path(url).is_file() for url in (original, changed, animated)))
        self.assertEqual(render.call_count, 3)

    def test_overlay_template_changes_invalidate_key(self):
        self.creation.is_animated = True
        key = social_preview_key(self.creation)
        with mock.patch('shrew.apps.creations.previews.render_to_string', return_value='<g/>'):
            self.assertNotEqual(social_preview_key(self.creation), key)

    def test_concurrent_requests_render_once(self):
        barrier = threading.Barrier(4)

        def request():
            barrier.wait(timeout=5)
            return get_social_preview_url(self.creation)

        def render(svg):
            time.sleep(0.05)
            return PNG

        with mock.patch('shrew.apps.creations.previews._render_png', side_effect=render) as renderer:
            with ThreadPoolExecutor(max_workers=4) as executor:
                urls = list(executor.map(lambda _: request(), range(4)))
        self.assertEqual(len(set(urls)), 1)
        self.assertEqual(renderer.call_count, 1)
        self.assertEqual(self.output_path(urls[0]).read_bytes(), PNG)

    @mock.patch('shrew.apps.creations.previews.subprocess.run')
    def test_timeout_leaves_no_png_and_retry_succeeds(self, run):
        run.side_effect = subprocess.TimeoutExpired('rsvg-convert', 10)
        with self.assertRaises(PreviewRenderError):
            get_social_preview_url(self.creation)
        self.assertEqual(list(Path(self.directory.name).rglob('*.png')), [])
        run.side_effect = None
        run.return_value.stdout = PNG
        url = get_social_preview_url(self.creation)
        self.assertEqual(self.output_path(url).read_bytes(), PNG)

    @mock.patch('shrew.apps.creations.previews.subprocess.run')
    def test_invalid_or_wrong_size_output_is_not_persisted(self, run):
        for output in (b'not a png', PNG[:16] + struct.pack('>II', 1, 1) + PNG[24:]):
            with self.subTest(output=output[:24]):
                run.return_value.stdout = output
                with self.assertRaises(PreviewRenderError):
                    get_social_preview_url(self.creation)
        self.assertEqual(list(Path(self.directory.name).rglob('*.png')), [])

    @mock.patch('shrew.apps.creations.previews._render_png', return_value=PNG)
    def test_failed_publish_cleans_up_temporary_file(self, render):
        with mock.patch('shrew.apps.creations.previews.os.replace', side_effect=OSError('disk full')):
            with self.assertRaises(OSError):
                get_social_preview_url(self.creation)
        self.assertEqual(list(Path(self.directory.name).rglob('*.png')), [])
        self.assertEqual(list(Path(self.directory.name).rglob('*.tmp')), [])

    @skipUnless(shutil.which(settings.RSVG_CONVERT_BIN), 'rsvg-convert is not installed')
    def test_real_renderer(self):
        self.creation.is_animated = True
        url = get_social_preview_url(self.creation)
        png = self.output_path(url).read_bytes()
        self.assertEqual(png[:8], b'\x89PNG\r\n\x1a\n')
        self.assertEqual(struct.unpack('>II', png[16:24]), (1200, 630))
        self.assertEqual(get_social_preview_url(self.creation), url)


class PreviewViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = get_user_model().objects.create_user(username='preview-owner')
        cls.creation = Creation.objects.create(
            name='Preview', author=user, code='Circle()', svg=SVG, is_animated=True,
        )

    def preview_url(self, kind):
        return reverse('creations:' + kind + '-preview', kwargs={
            'user': self.creation.author.username, 'slug': self.creation.slug,
        })

    def test_svg_download_and_facebook_variant(self):
        plain = self.client.get(self.preview_url('svg'))
        self.assertEqual(plain.content.decode(), SVG)
        self.assertEqual(plain['Content-Security-Policy'], 'sandbox')
        social = self.client.get(self.preview_url('svg') + '?facebook')
        self.assertEqual(social.content.decode(), social_preview_svg(self.creation))

    @mock.patch('shrew.apps.creations.views.get_social_preview_url')
    def test_png_redirects_to_local_media(self, preview):
        preview.return_value = '/media/social-previews/ab/abcdef.png'
        response = self.client.get(self.preview_url('png'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], preview.return_value)
        self.assertIn('public', response['Cache-Control'])
        self.assertIn('max-age=300', response['Cache-Control'])

    @mock.patch('shrew.apps.creations.views.get_social_preview_url')
    def test_failed_renderer_only_fails_preview_and_is_not_cached(self, preview):
        for error in (PreviewRenderError('renderer failed'), OSError('disk full')):
            with self.subTest(error=error), self.assertLogs('shrew.apps.creations.views', level='ERROR'):
                preview.side_effect = error
                response = self.client.get(self.preview_url('png'))
            self.assertEqual(response.status_code, 503)
            self.assertEqual(response['Cache-Control'], 'no-store')
            self.assertEqual(response['Retry-After'], '60')
        self.assertEqual(self.client.get(self.preview_url('svg')).status_code, 200)

    @mock.patch('shrew.apps.creations.views.get_social_preview_url')
    def test_unknown_creation_does_not_invoke_renderer(self, preview):
        response = self.client.get(self.preview_url('png').replace('preview.png', 'missing.png'))
        self.assertEqual(response.status_code, 404)
        preview.assert_not_called()

    @mock.patch('shrew.apps.creations.previews.subprocess.run')
    def test_share_page_versions_image_without_rendering(self, run):
        response = self.client.get(self.creation.get_absolute_url())
        self.assertContains(response, self.preview_url('png') + '?v=' + social_preview_key(self.creation))
        self.assertContains(response, 'property="og:image:type" content="image/png"')
        run.assert_not_called()
