import io

import vtracer
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from PIL import Image

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


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/convert")
async def convert(file: UploadFile = File(...), preset: str = Form("tekening")):
    if preset not in PRESETS:
        raise HTTPException(status_code=400, detail=f"Onbekende preset: {preset}")

    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Bestand is te groot (max 20 MB)")

    try:
        img = Image.open(io.BytesIO(data))
        img = img.convert("RGBA")
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Kon de afbeelding niet lezen. Upload een geldige JPG of PNG.",
        )

    if max(img.size) > MAX_DIMENSION:
        img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="PNG")

    try:
        svg = vtracer.convert_raw_image_to_svg(
            buf.getvalue(), img_format="png", **PRESETS[preset]
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Vectoriseren is mislukt.")

    return Response(content=svg, media_type="image/svg+xml")


app.mount("/", StaticFiles(directory="static", html=True), name="static")
