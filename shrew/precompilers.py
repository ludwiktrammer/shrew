import json

from compressor.filters import FilterBase
from compressor_toolkit.precompilers import ES6Compiler, SCSSCompiler, get_all_static


class DartSCSSCompiler(SCSSCompiler):
    """
    Variant of compressor_toolkit's ``SCSSCompiler`` that targets Dart Sass
    (the ``sass`` npm package) instead of the deprecated ``node-sass``.

    Dart Sass uses ``--load-path`` instead of ``--include-path`` for SCSS
    import directories, and accepts the output path as a positional argument
    rather than via shell redirection.
    """
    options = (
        ('node_sass_bin', 'node_modules/.bin/sass'),
        ('postcss_bin', 'node_modules/.bin/postcss'),
        ('paths', ' '.join('--load-path {}'.format(s) for s in get_all_static())),
        ('node_modules', 'node_modules'),
        ('autoprefixer_browsers', 'ie >= 9, > 5%'),
    )


class SkulptModuleFilter(FilterBase):
    JS_PREFIX = 'if (window.skulptModules === undefined) {window.skulptModules = {};}\n'
    def input(self, **kwargs):
        filename = self.filename.split('/')[-1]
        return '{}window.skulptModules["src/lib/{}"]={};'.format(self.JS_PREFIX, filename, json.dumps(self.content))


class SkulptModuleES6Filter(ES6Compiler):
    def input(self, **kwargs):
        content = super().input(**kwargs)
        filename = self.filename.split('/')[-1]
        return '{}window.skulptModules["src/lib/{}"]={};'.format(
            SkulptModuleFilter.JS_PREFIX,
            filename,
            json.dumps(content),
        )
