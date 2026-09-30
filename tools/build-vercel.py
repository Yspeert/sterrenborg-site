"""Maakt de Vercel-versie van de Sterrenborg-site.

site/index.html is geschreven als artifact-pagina (zonder <!doctype>, <html>, <head>).
Dit script zet er een volledig document omheen en schrijft het naar dist/, samen met
favicon en logo's. dist/ is precies wat in de GitHub-repo komt (Vercel: preset Other,
geen build command, output directory '.').

Gebruik: python3 tools/build-vercel.py   (vanuit de sitemap)
"""
import os, re, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, "site/index.html"), encoding="utf-8").read()

# alles tot en met </style> hoort in <head>, de rest in <body>
cut = src.index("</style>") + len("</style>")
head, body = src[:cut], src[cut:]
doc = ('<!doctype html>\n<html lang="nl">\n<head>\n<meta charset="utf-8">\n'
       '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
       '<meta property="og:title" content="Sterrenborg - van beleid naar bewijs">\n'
       '<meta property="og:image" content="logo/sterrenborg-sterrenbeeld-donker.png">\n'
       f'{head}\n</head>\n<body>\n{body}\n</body>\n</html>\n')

dist = os.path.join(ROOT, "dist")
os.makedirs(os.path.join(dist, "logo"), exist_ok=True)
open(os.path.join(dist, "index.html"), "w", encoding="utf-8").write(doc)
shutil.copy(os.path.join(ROOT, "logo/favicon.svg"), dist)
for f in os.listdir(os.path.join(ROOT, "logo")):
    shutil.copy(os.path.join(ROOT, "logo", f), os.path.join(dist, "logo", f))
for f in ("tools/make-logo.py", "tools/build-vercel.py"):
    os.makedirs(os.path.join(dist, "tools"), exist_ok=True)
    shutil.copy(os.path.join(ROOT, f), os.path.join(dist, "tools"))
shutil.copy(os.path.join(ROOT, "site/index.html"), os.path.join(dist, "tools", "index.artifact.html"))
print("dist klaar:", sorted(os.listdir(dist)))
