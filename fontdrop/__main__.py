"""Command-line tool: scan, overzicht, bevestiging, installeren, samenvatting.

Gebruik: python -m fontdrop <zips-en-mappen> [--prefer otf|ttf] [--yes] [--reinstall]
"""
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

from .dedupe import Family, build_families
from .installer import install_faces, read_registered_fonts, registry_name
from .scanner import scan


def _mark_installed(families: list[Family], registered: dict[str, str]) -> None:
    for family in families:
        for choice in family.styles:
            choice.already_installed = registry_name(choice.chosen) in registered


def _print_overview(families: list[Family]) -> None:
    print()
    print("Overzicht")
    print("=" * 60)
    for family in families:
        print(family.name)
        for choice in family.styles:
            status = "AL GEÏNSTALLEERD" if choice.already_installed else "nieuw"
            line = f"  {choice.style:<20} {choice.chosen.fmt:<4} {status}"
            print(line)
        print()


def _confirm(prompt: str) -> bool:
    answer = input(f"{prompt} [j/N]: ").strip().casefold()
    return answer in ("j", "ja", "y", "yes")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fontdrop", description="Scan, bekijk en installeer fonts uit zips en mappen.")
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--prefer", choices=["otf", "ttf"], default="otf", help="voorkeursformaat bij dubbele fonts")
    parser.add_argument("--yes", action="store_true", help="installeer direct zonder te vragen om bevestiging")
    parser.add_argument("--reinstall", action="store_true", help="installeer ook fonts die al geïnstalleerd zijn")
    args = parser.parse_args(argv)

    missing = [str(p) for p in args.inputs if not p.exists()]
    if missing:
        parser.error("niet gevonden: " + ", ".join(missing))

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    tmp = Path(tempfile.mkdtemp(prefix="fontdrop-"))
    try:
        result = scan(args.inputs, tmp)
        families = build_families(result.faces, prefer=args.prefer)

        if result.failures:
            print("Niet te lezen:")
            for source, reason in result.failures:
                print(f"  {source}: {reason}")

        if not families:
            print("Geen fonts gevonden.")
            return 1

        registered = read_registered_fonts()
        _mark_installed(families, registered)
        _print_overview(families)

        to_install = [
            choice.chosen
            for family in families
            for choice in family.styles
            if args.reinstall or not choice.already_installed
        ]
        skipped_already = [
            choice.chosen
            for family in families
            for choice in family.styles
            if not args.reinstall and choice.already_installed
        ]

        if not to_install:
            print("Alles is al geïnstalleerd. Niets te doen.")
            return 0

        print(f"{len(to_install)} font(en) te installeren, {len(skipped_already)} al aanwezig.")
        if not args.yes and not _confirm("Installeren?"):
            print("Geannuleerd. Er is niets geïnstalleerd.")
            return 1

        outcomes = install_faces(to_install)

        print()
        print("Samenvatting")
        print("=" * 60)
        installed = [o for o in outcomes if o[1] == "installed"]
        failed = [o for o in outcomes if o[1] == "failed"]
        for face in installed:
            print(f"  geïnstalleerd: {face[0].family} {face[0].style} ({face[0].fmt})")
        for face in skipped_already:
            print(f"  overgeslagen (al aanwezig): {face.family} {face.style} ({face.fmt})")
        for face, _status, reason in failed:
            print(f"  mislukt: {face.family} {face.style} ({face.fmt}) — {reason}")
        print()
        print(
            f"{len(installed)} geïnstalleerd, {len(skipped_already)} overgeslagen, "
            f"{len(failed)} mislukt"
        )
        return 0 if not failed else 2
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
