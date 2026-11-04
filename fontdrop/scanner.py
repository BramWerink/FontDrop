"""Uitpakken van zips (incl. geneste zips) en recursief zoeken naar fontbestanden."""
from __future__ import annotations

import itertools
import os
import shutil
import zipfile
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

from fontTools.ttLib import TTCollection, TTFont

FONT_EXTENSIONS = {".otf", ".ttf", ".ttc"}
ZIP_EXTENSION = ".zip"
MAX_ZIP_DEPTH = 5


@dataclass(frozen=True)
class FontFace:
    """Eén font-stijl zoals die in het fontbestand zelf is vastgelegd."""

    family: str
    style: str
    fmt: str  # "OTF" of "TTF"
    path: Path  # locatie in de tijdelijke map
    source: str  # bron waar het vandaan komt (zip of map, met nesting)
    face_index: int = 0  # index binnen een .ttc


@dataclass
class ScanResult:
    faces: list[FontFace] = field(default_factory=list)
    failures: list[tuple[str, str]] = field(default_factory=list)  # (bron, reden)


def _skip_name(name: str) -> bool:
    """Verborgen bestanden/mappen, ._-bestanden en __MACOSX negeren."""
    return name == "__MACOSX" or name.startswith(".")


def _read_faces(path: Path, source: str) -> list[FontFace]:
    if path.suffix.lower() == ".ttc":
        collection = TTCollection(str(path), lazy=True)
        try:
            return [_face(font, path, source, i) for i, font in enumerate(collection.fonts)]
        finally:
            collection.close()
    font = TTFont(str(path), lazy=True)
    try:
        return [_face(font, path, source, 0)]
    finally:
        font.close()


def _face(font: TTFont, path: Path, source: str, index: int) -> FontFace:
    name = font["name"]
    # nameID 16/17 (typografische familie) heeft voorrang; anders 1/2.
    if name.getDebugName(16):
        family = name.getDebugName(16)
        style = name.getDebugName(17) or "Regular"
    else:
        family = name.getDebugName(1)
        style = name.getDebugName(2) or "Regular"
    if not family:
        raise ValueError("geen familienaam in de name-tabel")
    fmt = "OTF" if ("CFF " in font or "CFF2" in font) else "TTF"
    return FontFace(family.strip(), style.strip(), fmt, path, source, index)


def _add_font(path: Path, source: str, result: ScanResult) -> None:
    try:
        result.faces.extend(_read_faces(path, source))
    except Exception as exc:  # fontTools gooit uiteenlopende fouten bij kapotte fonts
        result.failures.append((f"{source} / {path.name}", f"kon font niet lezen: {exc}"))


def _extract_zip(zip_path: Path, dest: Path, label: str, result: ScanResult) -> bool:
    try:
        zf = zipfile.ZipFile(zip_path)
    except (zipfile.BadZipFile, OSError) as exc:
        result.failures.append((label, f"zip niet te openen: {exc}"))
        return False
    with zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            parts = PurePosixPath(info.filename.replace("\\", "/")).parts
            if any(_skip_name(p) or p in ("..", "") or ":" in p for p in parts):
                continue
            if PurePosixPath(parts[-1]).suffix.lower() not in FONT_EXTENSIONS | {ZIP_EXTENSION}:
                continue
            target = dest.joinpath(*parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as src, open(target, "wb") as dst:
                shutil.copyfileobj(src, dst)
    return True


def _scan_folder(folder: Path, label: str, workdir: Path, depth: int,
                 result: ScanResult, counter: itertools.count) -> None:
    for dirpath, dirnames, filenames in os.walk(folder):
        dirnames[:] = [d for d in dirnames if not _skip_name(d)]
        for filename in filenames:
            if _skip_name(filename):
                continue
            path = Path(dirpath) / filename
            ext = path.suffix.lower()
            if ext in FONT_EXTENSIONS:
                _add_font(path, label, result)
            elif ext == ZIP_EXTENSION:
                _scan_zip(path, f"{label} > {filename}", workdir, depth + 1, result, counter)


def _scan_zip(zip_path: Path, label: str, workdir: Path, depth: int,
              result: ScanResult, counter: itertools.count) -> None:
    if depth > MAX_ZIP_DEPTH:
        result.failures.append((label, f"zip-nesting dieper dan {MAX_ZIP_DEPTH}"))
        return
    dest = workdir / f"z{next(counter):03d}"
    dest.mkdir(parents=True)
    if _extract_zip(zip_path, dest, label, result):
        _scan_folder(dest, label, workdir, depth, result, counter)


def scan(inputs: list[Path], workdir: Path) -> ScanResult:
    """Scan alle opgegeven zips en mappen. Uitgepakte bestanden komen in workdir."""
    result = ScanResult()
    counter = itertools.count(1)
    for item in inputs:
        if item.is_dir():
            _scan_folder(item, item.name, workdir, 0, result, counter)
        elif item.suffix.lower() == ZIP_EXTENSION:
            _scan_zip(item, item.name, workdir, 0, result, counter)
        else:
            result.failures.append((item.name, "geen map of zip"))
    return result
