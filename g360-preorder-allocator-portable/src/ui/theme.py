from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class Modo(str, Enum):
    LIGHT = "light"
    DARK = "dark"


@dataclass
class Paleta:
    bg: str
    surface: str
    surface_hover: str
    accent: str
    accent_secondary: str
    text: str
    text_secondary: str
    border: str
    success: str
    warning: str
    danger: str
    info: str
    glass_bg: str
    glass_border: str
    input_bg: str


LIGHT: Paleta = Paleta(
    bg="#f8fafc",
    surface="#ffffff",
    surface_hover="#f1f5f9",
    accent="#059669",
    accent_secondary="#0284c7",
    text="#0f172a",
    text_secondary="#64748b",
    border="#e2e8f0",
    success="#059669",
    warning="#f59e0b",
    danger="#ef4444",
    info="#0ea5e9",
    glass_bg="rgba(255, 255, 255, 0.7)",
    glass_border="rgba(226, 232, 240, 0.8)",
    input_bg="#f1f5f9",
)

DARK: Paleta = Paleta(
    bg="#0b1220",
    surface="#1a2333",
    surface_hover="#243044",
    accent="#34d399",
    accent_secondary="#38bdf8",
    text="#f9fafb",
    text_secondary="#9ca3af",
    border="#1e293b",
    success="#34d399",
    warning="#fbbf24",
    danger="#f87171",
    info="#38bdf8",
    glass_bg="rgba(26, 35, 51, 0.8)",
    glass_border="rgba(30, 41, 59, 0.8)",
    input_bg="#1e293b",
)
