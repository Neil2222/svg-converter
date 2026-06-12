import io
import re
from pathlib import Path

import numpy as np
import vtracer
from scipy import ndimage
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from PIL import Image
from pillow_heif import register_heif_opener

# HEIC/HEIF-ondersteuning (o.a. iPhone-foto's); overige formaten zitten al in Pillow.
register_heif_opener()

MAX_UPLOAD_BYTES = 20 * 1024 * 1024
# Vectorizing huge bitmaps is slow and yields bloated SVGs; cap the input size.
MAX_DIMENSION = 2000

PRESETS = {
    "logo": dict(
        colormode="color",
        color_precision=4,
        layer_difference=64,
        filter_speckle=8,
        corner_threshold=30,
    ),
    "tekening": dict(
        colormode="color",
        color_precision=6,
        layer_difference=24,
        filter_speckle=4,
        corner_threshold=60,
    ),
    "foto": dict(
        colormode="color",
        color_precision=8,
        layer_difference=12,
        filter_speckle=2,
        corner_threshold=80,
    ),
    "zwartwit": dict(
        colormode="binary",
        filter_speckle=4,
    ),
}

app = FastAPI(title="svg-converter")
README_PATH = Path(__file__).with_name("README.md")


def use_current_color(svg: str) -> str:
    """Maak zwart-wit iconen meekleurend met de CSS/textkleur."""
    svg = re.sub(r'\sfill="(?:#000(?:000)?|black|rgb\(0,\s*0,\s*0\))"', "", svg, flags=re.I)
    return re.sub(r"<svg\b(?![^>]*\sfill=)", '<svg fill="currentColor"', svg, count=1)


def remove_background(img: Image.Image, tolerance: int = 24) -> Image.Image:
    """Maak de achtergrond transparant via flood fill vanaf hoeken en randmiddens.

    Elke seed gebruikt zijn eigen pixelkleur als referentie, dus dit werkt voor
    witte én gekleurde achtergronden (bijv. zwart ingebakken hoeken bij van een
    website gekopieerde afbeeldingen). Details binnenin de afbeelding blijven
    staan. VTracer slaat transparante pixels vervolgens over bij het traceren.
    """
    arr = np.array(img)  # RGBA
    rgb = arr[..., :3].astype(np.int16)
    alpha = arr[..., 3]
    h, w = alpha.shape
    # Alleen de hoeken als seed: randmiddens raken vaak het onderwerp zelf
    # (bijv. een afgeronde rechthoek die de beeldrand raakt).
    seeds = [(0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1)]
    removed = np.zeros((h, w), dtype=bool)
    for y, x in seeds:
        if alpha[y, x] == 0 or removed[y, x]:
            continue
        mask = (np.abs(rgb - rgb[y, x]) <= tolerance).all(axis=2) & (alpha > 0)
        labels, _ = ndimage.label(mask)
        removed |= labels == labels[y, x]
    arr[removed, 3] = 0
    return Image.fromarray(arr)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/README.md", response_class=PlainTextResponse)
def readme():
    return README_PATH.read_text(encoding="utf-8")


@app.post("/api/convert")
async def convert(
    file: UploadFile = File(...),
    preset: str = Form("tekening"),
    remove_bg: bool = Form(False),
):
    if preset not in PRESETS:
        raise HTTPException(status_code=400, detail=f"Onbekende preset: {preset}")

    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Bestand is te groot (max 20 MB)")

    try:
        img = Image.open(io.BytesIO(data))
        # Bij animaties (GIF/WebP) pakt Pillow standaard het eerste frame.
        img = img.convert("RGBA")
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Kon de afbeelding niet lezen. Upload een geldig afbeeldingsbestand "
            "(bijv. JPG, PNG, WebP, GIF, HEIC, BMP of TIFF).",
        )

    # VTracer negeert alleen 100% transparante pixels en tracet al het andere
    # als volledig dekkend; zwakke schaduwen/ruis in het alphakanaal zouden
    # dus keihard zwart worden. Alles onder 50% dekking wordt daarom volledig
    # transparant gemaakt. Daarna de kleur van de dichtstbijzijnde dekkende
    # pixel uitsmeren onder de transparante gebieden ("edge bleeding"), zodat
    # LANCZOS-interpolatie bij het schalen randpixels niet met de (onzichtbare)
    # RGB-waarden onder de transparantie mengt.
    arr = np.array(img)
    arr[..., 3] = np.where(arr[..., 3] < 128, 0, arr[..., 3])
    transparent = arr[..., 3] == 0
    if transparent.any() and not transparent.all():
        idx_y, idx_x = ndimage.distance_transform_edt(
            transparent, return_distances=False, return_indices=True
        )
        arr[..., :3] = arr[idx_y, idx_x, :3]
    img = Image.fromarray(arr)

    if max(img.size) > MAX_DIMENSION:
        img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.LANCZOS)

    # Kleine afbeeldingen opschalen vóór het traceren: fijne details (zoals
    # kleine tekst) zijn anders kleiner dan de speckle-filter en verdwijnen.
    display_size = img.size
    scale = 1
    if max(img.size) < 1400:
        scale = min(4, MAX_DIMENSION // max(img.size))
        if scale > 1:
            # BILINEAR i.p.v. LANCZOS: lanczos-ringing maakt randpixels net
            # iets feller, wat na clustering tot honderden snippers leidt.
            img = img.resize((img.width * scale, img.height * scale), Image.BILINEAR)

    # Na het schalen nogmaals: interpolatie maakt randpixels halfdoorzichtig.
    arr = np.array(img)
    arr[..., 3] = np.where(arr[..., 3] < 128, 0, arr[..., 3])
    img = Image.fromarray(arr)

    if remove_bg:
        img = remove_background(img)

    buf = io.BytesIO()
    img.save(buf, format="PNG")

    try:
        svg = vtracer.convert_raw_image_to_svg(
            buf.getvalue(), img_format="png", **PRESETS[preset]
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Vectoriseren is mislukt.")

    # VTracer zet width/height zonder viewBox; zonder viewBox schaalt de SVG
    # niet mee wanneer die maten later worden aangepast.
    if "viewBox" not in svg:
        svg = re.sub(
            r'(<svg[^>]*?)\swidth="([\d.]+)"\sheight="([\d.]+)"',
            r'\1 width="\2" height="\3" viewBox="0 0 \2 \3"',
            svg,
            count=1,
        )

    # Na opschalen de weergavemaat terugzetten naar de originele afmetingen;
    # de viewBox blijft in getracede coördinaten.
    if scale > 1:
        svg = re.sub(
            r'(<svg[^>]*?)\swidth="[\d.]+"\sheight="[\d.]+"',
            rf'\1 width="{display_size[0]}" height="{display_size[1]}"',
            svg,
            count=1,
        )

    if preset == "zwartwit":
        svg = use_current_color(svg)

    return Response(content=svg, media_type="image/svg+xml")


app.mount("/", StaticFiles(directory="static", html=True), name="static")
