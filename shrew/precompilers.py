import json

from compressor.filters import FilterBase
from compressor_toolkit.precompilers import ES6Compiler, BaseCompiler

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


class NearleyFilter(BaseCompiler):
    command = 'node_modules/nearley/bin/nearleyc.js "{infile}" -o "{outfile}"'
    infile_ext = '.ne'

