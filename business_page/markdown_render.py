"""Markdown → HTML for Journal posts (staff-authored via admin).

Code blocks are highlighted server-side with Pygments, so articles ship no
highlighting JavaScript. Returns (html, toc) where toc is a flat list of the
article's h2 headings for the in-page contents rail."""

import markdown


def render_markdown(text):
    md = markdown.Markdown(
        extensions=['fenced_code', 'codehilite', 'tables', 'toc', 'sane_lists', 'attr_list'],
        extension_configs={
            'codehilite': {'css_class': 'hl', 'guess_lang': False, 'linenums': False},
            'toc': {'permalink': False, 'toc_depth': '2-3'},
        },
        output_format='html',
    )
    html = md.convert(text or '')
    toc = [
        {'id': tok['id'], 'name': tok['name']}
        for tok in getattr(md, 'toc_tokens', [])
        if tok.get('level') == 2
    ]
    # Wrap tables so they can scroll horizontally on narrow screens instead of
    # forcing the whole article column to overflow.
    html = html.replace('<table>', '<div class="table-scroll" tabindex="0" role="region" aria-label="Table"><table>')
    html = html.replace('</table>', '</table></div>')
    return html, toc
