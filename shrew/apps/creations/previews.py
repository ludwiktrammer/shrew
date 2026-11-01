"""Render social previews locally and keep content-addressed PNGs in MEDIA_ROOT."""
import fcntl
import hashlib
import os
from pathlib import Path
import struct
import subprocess
import tempfile

from django.conf import settings
from django.template.loader import render_to_string


class PreviewRenderError(Exception):
    pass


def social_preview_svg(creation):
    svg = creation.svg.replace(
        'viewBox="0 0 100 100"', 'viewBox="-45.25 0 190.5 100"', 1,
    )
    if creation.is_animated:
        svg = svg.replace(
            '</svg>', render_to_string('creations/_play.svg') + '\n</svg>',
        )
    return svg


def _source_key(svg):
    # Bump this prefix when changing renderer settings or output dimensions.
    return hashlib.sha256(b'rsvg-convert:1200x630:v1\0' + svg.encode('utf-8')).hexdigest()


def social_preview_key(creation):
    return _source_key(social_preview_svg(creation))


def _render_png(svg):
    try:
        result = subprocess.run(
            [settings.RSVG_CONVERT_BIN, '--format=png', '--width=1200', '--height=630'],
            input=svg.encode('utf-8'), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise PreviewRenderError('rsvg-convert failed to generate a preview') from exc
    png = result.stdout
    if (len(png) < 24 or png[:8] != b'\x89PNG\r\n\x1a\n'
            or png[12:16] != b'IHDR' or struct.unpack('>II', png[16:24]) != (1200, 630)):
        raise PreviewRenderError('rsvg-convert returned an invalid 1200x630 PNG')
    return png


def get_social_preview_url(creation):
    svg = social_preview_svg(creation)
    key = _source_key(svg)
    relative_path = Path('social-previews') / key[:2] / (key + '.png')
    output = Path(settings.MEDIA_ROOT) / relative_path
    if not output.is_file():
        output.parent.mkdir(parents=True, exist_ok=True)
        # Keep the lock file: unlinking it can let different workers lock
        # different inodes and render the same image concurrently.
        with output.with_suffix('.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            if not output.is_file():
                png = _render_png(svg)
                temporary_path = None
                try:
                    with tempfile.NamedTemporaryFile(
                        dir=output.parent, prefix='.' + key + '-', suffix='.tmp', delete=False,
                    ) as temporary:
                        temporary_path = Path(temporary.name)
                        temporary.write(png)
                        os.fchmod(temporary.fileno(), 0o644)
                    # Publish only the complete file, on the same filesystem.
                    os.replace(temporary_path, output)
                finally:
                    if temporary_path is not None:
                        temporary_path.unlink(missing_ok=True)
    return settings.MEDIA_URL.rstrip('/') + '/' + relative_path.as_posix()
