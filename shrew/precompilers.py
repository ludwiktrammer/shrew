import json

from compressor.filters import FilterBase

class SkulptModuleFilter(FilterBase):
    JS_PREFIX = 'if (window.skulptModules === undefined) {window.skulptModules = {};}\n'
    def input(self, **kwargs):
        filename = self.filename.split('/')[-1]
        return '{}window.skulptModules["src/lib/{}"]={};'.format(self.JS_PREFIX, filename, json.dumps(self.content))
