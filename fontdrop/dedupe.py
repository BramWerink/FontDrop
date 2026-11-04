"""Deduplicatie op interne fontnaam (family + style) en keuze tussen OTF en TTF."""
from __future__ import annotations

from dataclasses import dataclass, field

from .scanner import FontFace


@dataclass
class StyleChoice:
    style: str
    chosen: FontFace
    alternatives: list[FontFace] = field(default_factory=list)  # zelfde stijl, overige kopieën
    already_installed: bool = False


@dataclass
class Family:
    name: str
    styles: list[StyleChoice]


def _key(text: str) -> str:
    return " ".join(text.split()).casefold()


def build_families(faces: list[FontFace], prefer: str = "otf") -> list[Family]:
    if prefer not in ("otf", "ttf"):
        raise ValueError("prefer moet 'otf' of 'ttf' zijn")
    prefer_fmt = prefer.upper()

    groups: dict[tuple[str, str], list[FontFace]] = {}
    display: dict[str, str] = {}
    for face in faces:
        family_key = _key(face.family)
        groups.setdefault((family_key, _key(face.style)), []).append(face)
        display.setdefault(family_key, face.family.strip())

    families: dict[str, list[StyleChoice]] = {}
    for (family_key, _style_key), candidates in groups.items():
        candidates.sort(key=lambda f: (f.source, str(f.path), f.face_index))
        preferred = [f for f in candidates if f.fmt == prefer_fmt]
        chosen = (preferred or candidates)[0]
        alternatives = [f for f in candidates if f is not chosen]
        families.setdefault(family_key, []).append(
            StyleChoice(style=chosen.style, chosen=chosen, alternatives=alternatives)
        )

    result = []
    for family_key in sorted(families, key=lambda k: display[k].casefold()):
        styles = sorted(families[family_key], key=lambda s: s.style.casefold())
        result.append(Family(name=display[family_key], styles=styles))
    return result
