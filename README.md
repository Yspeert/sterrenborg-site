# Sterrenborg

Statische one-pager voor Sterrenborg. `index.html` is de hele site: geen build, geen dependencies.

- Vercel: framework preset **Other**, geen build command, output directory `.`
- Logo's in `logo/` (SVG en PNG, licht en donker, drie varianten). Opnieuw maken: `python3 tools/make-logo.py`
- Wijzigingen aan de pagina: bewerk `tools/index.artifact.html` en draai `python3 tools/build-vercel.py`
