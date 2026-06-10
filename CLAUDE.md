# SVG Converter

## Architectuur in één zin
FastAPI app op Windows PC (poort 5285) die uploads vectoriseert met VTracer,
bereikbaar als svg.neiltwo2.nl via Synology reverse proxy.

## Werkafspraken
- Python 3.11+, package manager: uv
- Eén bestand backend (`server.py`), frontend is één statische pagina (`static/index.html`)
- Presets voor VTracer-parameters staan in `PRESETS` in server.py
- Geen database, geen state — bewust mini houden
