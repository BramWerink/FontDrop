"""Editoriale, typografie-gedreven stijl: wit/zwart, dunne lijnen, geen afronding, geen schaduw."""
from __future__ import annotations

# Grotesk voor UI-tekst, serif met karakter voor grote koppen. Qt valt vanzelf
# terug op het eerste beschikbare lettertype in de lijst.
UI_FONT_STACK = '"Inter Display", "Neue Haas Grotesk Text Pro", "Segoe UI", Arial, sans-serif'
HEADLINE_FONT_STACK = '"Big Caslon", "Hoefler Text", "EB Garamond", Georgia, "Times New Roman", serif'

BLACK = "#000000"
WHITE = "#ffffff"

QSS = f"""
* {{
    font-family: {UI_FONT_STACK};
    color: {BLACK};
}}

QWidget {{
    background-color: {WHITE};
}}

QLabel#headline {{
    font-family: {HEADLINE_FONT_STACK};
    font-size: 40px;
    font-weight: 700;
    padding: 0;
    margin: 0;
}}

QLabel#kicker {{
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
}}

QFrame#rule {{
    background-color: {BLACK};
    max-height: 1px;
    min-height: 1px;
    border: none;
}}

QFrame#ruleVertical {{
    background-color: {BLACK};
    max-width: 1px;
    min-width: 1px;
    border: none;
}}

QPushButton {{
    background-color: {BLACK};
    color: {WHITE};
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 1px;
    padding: 14px 28px;
    border: 1px solid {BLACK};
    border-radius: 0px;
}}

QPushButton:hover {{
    background-color: {WHITE};
    color: {BLACK};
}}

QPushButton:disabled {{
    background-color: {WHITE};
    color: #bbbbbb;
    border: 1px solid #bbbbbb;
}}

QPushButton#secondary {{
    background-color: {WHITE};
    color: {BLACK};
    border: 1px solid {BLACK};
}}

QPushButton#secondary:hover {{
    background-color: {BLACK};
    color: {WHITE};
}}

QScrollArea {{
    border: none;
}}

QCheckBox {{
    spacing: 12px;
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {BLACK};
    background-color: {WHITE};
    border-radius: 0px;
}}

QCheckBox::indicator:checked {{
    background-color: {BLACK};
}}

QLabel.smallcaps {{
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #555555;
}}
"""
