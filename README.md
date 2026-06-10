# SVG Converter

Mini webserver die een JPG of PNG omzet naar een echte vector-SVG, met
[VTracer](https://github.com/visioncortex/vtracer) als tracing-engine.

## Starten

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

## Limieten

- Max 20 MB upload
- Afbeeldingen groter dan 2000 px worden eerst verkleind (sneller, kleinere SVG)
