# PyInstaller-spec voor een standalone one-file .exe (geen Python nodig).
# Bouwen via build-exe.bat of: python -m PyInstaller --noconfirm --clean svg-converter.spec
from PyInstaller.utils.hooks import collect_all, collect_submodules

# Gebundelde databestanden. README/static draaien de webapp; de bronbestanden
# zitten erbij zodat de "Download app (.zip)"-knop ook vanuit de exe werkt.
datas = [
    ("static", "static"),
    ("README.md", "."),
    ("server.py", "."),
    ("pyproject.toml", "."),
    ("start.bat", "."),
]
binaries = []
hiddenimports = collect_submodules("uvicorn")

# Pakketten met eigen binaries/datafiles die PyInstaller niet vanzelf vindt.
for pkg in ("pillow_heif", "vtracer", "scipy"):
    pkg_datas, pkg_binaries, pkg_hidden = collect_all(pkg)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hidden

a = Analysis(
    ["server.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="svg-converter",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
