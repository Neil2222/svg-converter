# SVG Converter

Mini webserver die afbeeldingen omzet naar echte vector-SVG's met
[VTracer](https://github.com/visioncortex/vtracer) als tracing-engine.

Ondersteunde invoer: alles wat Pillow kan lezen, zoals JPG, PNG, WebP, GIF
(eerste frame), HEIC/HEIF via pillow-heif, AVIF, BMP, TIFF, JPEG 2000, ICO,
TGA, PCX en PPM.

## Snel Starten

Voor degene die de zip ontvangt:

1. Pak `svg-converter.zip` uit.
2. Dubbelklik op `start.bat`.
3. Wacht tot de installatie klaar is.
4. Ga in de browser naar `http://127.0.0.1:5285` als de pagina niet vanzelf opent.

De eerste start kan even duren en heeft internet nodig. `start.bat` maakt
automatisch een `.venv` aan en installeert de packages uit `pyproject.toml`.
Daarna start de webserver.

Laat het `start.bat`-venster open zolang je de converter gebruikt. Sluit het
venster om de server te stoppen.

Vereist: Python 3.11 of nieuwer op Windows.

## Gebruik

Open de pagina, sleep een afbeelding naar de dropzone en kies het type
afbeelding:

- **Logo / icoon**: weinig kleuren, strakke vlakken
- **Tekening / illustratie**: standaard
- **Foto (experimenteel)**: meer kleurlagen; foto's vectoriseren blijft beperkt
- **Zwart-wit / lijntekening**: binaire trace voor iconen

Bij **Zwart-wit / lijntekening** krijgt de SVG `fill="currentColor"`. Daardoor
kleurt het icoon mee met Bootstrap/CSS, bijvoorbeeld via `text-primary`,
`text-danger` of een eigen `color`.

Het resultaat verschijnt naast het origineel en is te downloaden of naar het
klembord te kopieren. Wisselen van preset converteert direct opnieuw.

Met de knop **README** rechtsboven kun je deze handleiding ook in de webapp
openen.

**Achtergrond verwijderen** maakt de achtergrondkleur transparant via flood fill
vanaf de hoeken. Details binnenin de afbeelding blijven staan.

## Limieten

- Max 20 MB upload
- Afbeeldingen groter dan 2000 px worden eerst verkleind
- Afbeeldingen kleiner dan 1400 px worden voor het traceren opgeschaald
- Bewegende GIF/WebP: alleen het eerste frame wordt gevectoriseerd
- Formaten die de browser zelf niet kan tonen, zoals TGA, JPEG 2000 en HEIC,
  krijgen geen preview links maar converteren wel

## Handmatig Starten

Als je de stappen zelf wilt uitvoeren:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m uvicorn server:app --host 0.0.0.0 --port 5285
```

Open daarna:

```text
http://127.0.0.1:5285
```

## Zip Maken

Deze sectie is alleen voor de maker vanuit de volledige projectmap, niet voor
degene die alleen `svg-converter.zip` ontvangt.

Maak een distributiezip met:

```bat
maak-zip.bat
```

Dat maakt `svg-converter.zip` met alleen deze bestanden:

- `server.py`
- `pyproject.toml`
- `start.bat`
- `README.md`
- `static/`

Niet meesturen:

- `.venv/`
- `venv/`
- `__pycache__/`
- `svg_converter.egg-info/`
- `logs/`
- `.git/`
- `CLAUDE.md`
- `maak-zip.bat`
