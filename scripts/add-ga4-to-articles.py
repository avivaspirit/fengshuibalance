"""Bulk-add GA4 snippet to all existing fengshuibalance article HTML files.
Run once from repo root: python scripts/add-ga4-to-articles.py
Safe: skips files that already have the snippet. Only adds before </head>.
"""
import os
import time

GA_SNIPPET = '''<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-30SJEY0LYC"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-30SJEY0LYC');
</script>'''

MARKER = 'G-30SJEY0LYC'
articles_dir = os.path.join(os.path.dirname(__file__), '..', 'articles')
count = 0
skipped = 0
errors = 0

start = time.time()

for fname in sorted(os.listdir(articles_dir)):
    if not fname.endswith('.html'):
        continue
    fpath = os.path.join(articles_dir, fname)
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            html = f.read()
        if MARKER in html:
            skipped += 1
            continue
        html = html.replace('</head>', GA_SNIPPET + '\n</head>')
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(html)
        count += 1
        if count % 500 == 0:
            print(f'  ... {count} files done ({time.time()-start:.1f}s)')
    except Exception as e:
        errors += 1
        print(f'  ERROR: {fname}: {e}')

elapsed = time.time() - start
print(f'\nDone: {count} added, {skipped} already had GA4, {errors} errors ({elapsed:.1f}s)')
