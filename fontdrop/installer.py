"""Installatie per gebruiker op Windows 11: kopie naar %LOCALAPPDATA% en registratie in HKCU."""
from __future__ import annotations

import ctypes
import os
import shutil
import winreg
from pathlib import Path

from .scanner import FontFace

REG_PATH = r"Software\Microsoft\Windows NT\CurrentVersion\Fonts"
FONT_DIR = Path(os.environ["LOCALAPPDATA"]) / "Microsoft" / "Windows" / "Fonts"

_gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
_user32 = ctypes.WinDLL("user32", use_last_error=True)
_gdi32.AddFontResourceW.argtypes = [ctypes.c_wchar_p]
_gdi32.AddFontResourceW.restype = ctypes.c_int


def registry_name(face: FontFace) -> str:
    """Weergavenaam zoals Windows die in het register gebruikt, bv. 'Arial Bold (TrueType)'."""
    base = face.family if face.style.casefold() == "regular" else f"{face.family} {face.style}"
    kind = "OpenType" if face.fmt == "OTF" else "TrueType"
    return f"{base} ({kind})"


def read_registered_fonts() -> dict[str, str]:
    """Alle geregistreerde fonts van deze gebruiker: weergavenaam -> bestandsnaam."""
    values: dict[str, str] = {}
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH)
    except FileNotFoundError:
        return values
    with key:
        index = 0
        while True:
            try:
                name, data, _ = winreg.EnumValue(key, index)
            except OSError:
                break
            values[name] = str(data)
            index += 1
    return values


def _unique_target(source: Path) -> Path:
    """Doelnaam in de gebruikersmap; bestaande andere fonts met dezelfde naam worden niet overschreven."""
    target = FONT_DIR / source.name
    counter = 2
    while target.exists() and target.read_bytes() != source.read_bytes():
        target = FONT_DIR / f"{source.stem}_{counter}{source.suffix}"
        counter += 1
    return target


def install_faces(faces: list[FontFace]) -> list[tuple[FontFace, str, str]]:
    """Installeert fonts. Geeft per font (face, 'installed'|'failed', reden) terug."""
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    copied: dict[Path, Path] = {}
    outcomes: list[tuple[FontFace, str, str]] = []
    key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE)
    try:
        for face in faces:
            try:
                if face.path not in copied:
                    target = _unique_target(face.path)
                    if not target.exists():
                        shutil.copy2(face.path, target)
                    copied[face.path] = target
                target = copied[face.path]
                winreg.SetValueEx(key, registry_name(face), 0, winreg.REG_SZ, target.name)
                _gdi32.AddFontResourceW(str(target))
                outcomes.append((face, "installed", ""))
            except OSError as exc:
                outcomes.append((face, "failed", str(exc)))
    finally:
        winreg.CloseKey(key)
    # Laat lopende programma's weten dat er nieuwe fonts zijn.
    _user32.SendMessageTimeoutW(0xFFFF, 0x001D, 0, 0, 0x0002, 1000, None)
    return outcomes
