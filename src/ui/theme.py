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
    bg="#f0f4f8",
    surface="#ffffff",
    surface_hover="#f8fafc",
    accent="#00d084",
    accent_secondary="#6366f1",
    text="#0b1221",
    text_secondary="#64748b",
    border="#e2e8f0",
    success="#10b981",
    warning="#f59e0b",
    danger="#ef4444",
    info="#06b6d4",
    glass_bg="rgba(255, 255, 255, 0.65)",
    glass_border="rgba(226, 232, 240, 0.6)",
    input_bg="#f1f5f9",
)

DARK: Paleta = Paleta(
    bg="#0b0f19",
    surface="#161b2b",
    surface_hover="#1e2438",
    accent="#00d084",
    accent_secondary="#818cf8",
    text="#f1f5f9",
    text_secondary="#94a3b8",
    border="#1e293b",
    success="#34d399",
    warning="#fbbf24",
    danger="#f87171",
    info="#22d3ee",
    glass_bg="rgba(22, 27, 43, 0.75)",
    glass_border="rgba(30, 41, 59, 0.6)",
    input_bg="#1e2438",
)
