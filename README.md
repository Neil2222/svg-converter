# SVG Converter

Mini webserver die een afbeelding omzet naar een echte vector-SVG, met
[VTracer](https://github.com/visioncortex/vtracer) als tracing-engine.

Ondersteunde invoer: alles wat Pillow kan lezen — o.a. JPG, PNG, WebP, GIF
(eerste frame), HEIC/HEIF (via pillow-heif), AVIF, BMP, TIFF, JPEG 2000,
ICO, TGA, PCX en PPM.

## Starten

Draait als Windows-service **SvgConverter** (via NSSM, `C:\tools\nssm.exe`),
start automatisch mee met de PC. Beheer (admin-terminal):

```
nssm restart SvgConverter   # na een code-update
nssm stop SvgConverter
nssm status SvgConverter
```

Logs: `logs\out.log` en `logs\err.log`. Crasht de server, dan start NSSM
hem automatisch opnieuw.

Handmatig draaien (zonder service) kan ook:

```
uv sync
start.bat
```

De server draait dan op poort **5285** (bind op 0.0.0.0, zodat de Synology
reverse proxy erbij kan: `svg.neiltwo2.nl` → `http://<pc-ip>:5285`).

Geeft `http://localhost:5285` een keer `ERR_CONNECTION_REFUSED` terwijl de
server draait? Gebruik dan `http://127.0.0.1:5285`; de server luistert alleen
op IPv4 en `localhost` gaat eerst via IPv6 (`::1`).

## Gebruik

Open de pagina, sleep een JPG/PNG naar de dropzone en kies het type afbeelding:

- **Logo / icoon** — weinig kleuren, strakke vlakken
- **Tekening / illustratie** — standaard
- **Foto (experimenteel)** — meer kleurlagen; foto's vectoriseren blijft matig
- **Zwart-wit / lijntekening** — binaire trace

Het resultaat verschijnt naast het origineel en is te downloaden of naar het
klembord te kopiëren. Wisselen van preset converteert direct opnieuw.

**Achtergrond verwijderen** maakt de achtergrondkleur transparant via flood
fill vanaf de hoeken en randmiddens (elke seed gebruikt zijn eigen kleur als
referentie, dus wit én gekleurde achtergronden werken); details binnenin de
afbeelding blijven staan.

## Limieten

- Max 20 MB upload
- Afbeeldingen groter dan 2000 px worden eerst verkleind (sneller, kleinere SVG)
- Bewegende GIF/WebP: alleen het eerste frame wordt gevectoriseerd
- Formaten die de browser zelf niet kan tonen (TGA, JPEG 2000, HEIC, ...)
  krijgen geen preview links, maar converteren gewoon
