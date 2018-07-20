import re

from django import template

register = template.Library()

EMBED_TEMPLATE = """
<div class="embed-outer"><div class="embed-container editor-embed">
<iframe scrolling="no" src="\g<1>?embedded"></iframe>
</div></div>
"""
EDITOR_PATTERN = re.compile(
    # matches /editor and show/*/*/edit
    r"^\s*(https://shrew\.app/(editor|show/[-\w]+/[-\w]+/edit)/?)\s*$",
    flags=re.MULTILINE | re.IGNORECASE,
)


@register.filter(name='shrew_embed')
def shrew_embed(value):
    return EDITOR_PATTERN.sub(EMBED_TEMPLATE, value)
