import io
import re

import numpy as np
import vtracer
from scipy import ndimage
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
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


def remove_white_background(img: Image.Image, threshold: int = 240) -> Image.Image:
    """Maak witte achtergrond transparant via flood fill vanaf de randen.

    Alleen near-white gebieden die de rand raken worden verwijderd; witte
    details binnenin de afbeelding blijven staan. VTracer slaat transparante
    pixels vervolgens over bij het traceren.
    """
    arr = np.array(img)  # RGBA
    near_white = (arr[..., :3] >= threshold).all(axis=2) & (arr[..., 3] > 0)
    labels, _ = ndimage.label(near_white)
    border_labels = np.unique(
        np.concatenate([labels[0, :], labels[-1, :], labels[:, 0], labels[:, -1]])
    )
    border_labels = border_labels[border_labels != 0]
    if border_labels.size:
        arr[np.isin(labels, border_labels), 3] = 0
    return Image.fromarray(arr)


@app.get("/health")
def health():
    return {"status": "ok"}


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

    if max(img.size) > MAX_DIMENSION:
        img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.LANCZOS)

    if remove_bg:
        img = remove_white_background(img)

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

    return Response(content=svg, media_type="image/svg+xml")


app.mount("/", StaticFiles(directory="static", html=True), name="static")
