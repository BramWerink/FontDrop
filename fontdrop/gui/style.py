"""Pastel academia: crème, inkt en salie, met een serif met karakter voor de koppen."""
from __future__ import annotations

UI_FONT_STACK = '"Inter", "Inter Display", "Segoe UI", Arial, sans-serif'
HEADLINE_FONT_STACK = '"Fraunces", Georgia, "Times New Roman", serif'

CREAM = "#F4EFE6"
INK = "#3B3630"
INK_MUTED = "#6B6358"
SAGE = "#7C8B6F"
SAGE_TINT = "#EAEEE4"
HAIRLINE = "rgba(59, 54, 48, 0.14)"

QSS = f"""
* {{
    font-family: {UI_FONT_STACK};
    color: {INK};
}}

QWidget {{
    background-color: {CREAM};
}}

QLabel#headline {{
    font-family: {HEADLINE_FONT_STACK};
    font-size: 32px;
    font-weight: 600;
    padding: 0;
    margin: 0;
}}

QLabel#kicker {{
    font-family: {HEADLINE_FONT_STACK};
    font-size: 15px;
    font-weight: 600;
}}

QFrame#rule {{
    background-color: {HAIRLINE};
    max-height: 1px;
    min-height: 1px;
    border: none;
}}

QPushButton {{
    background-color: transparent;
    color: {INK};
    font-weight: 500;
    font-size: 13px;
    padding: 12px 26px;
    border: 1px solid {INK};
    border-radius: 20px;
}}

QPushButton:hover {{
    background-color: {SAGE_TINT};
}}

QPushButton:disabled {{
    color: #B9B2A4;
    border: 1px solid #DDD6C8;
}}

QPushButton#primary {{
    background-color: {SAGE};
    color: {CREAM};
    border: 1px solid {SAGE};
}}

QPushButton#primary:hover {{
    background-color: #6D7B61;
    border: 1px solid #6D7B61;
}}

QPushButton#primary:disabled {{
    background-color: #DCE0D5;
    color: #FFFFFF;
    border: 1px solid #DCE0D5;
}}

QScrollArea {{
    border: none;
}}

QCheckBox {{
    spacing: 10px;
}}

QCheckBox::indicator {{
    width: 15px;
    height: 15px;
    border: 1px solid {INK};
    border-radius: 4px;
    background-color: {CREAM};
}}

QCheckBox::indicator:checked {{
    background-color: {SAGE};
    border: 1px solid {SAGE};
}}

QLabel.tag-new {{
    font-size: 11px;
    color: {SAGE};
}}

QLabel.tag-installed {{
    font-size: 11px;
    color: {INK_MUTED};
}}
"""
