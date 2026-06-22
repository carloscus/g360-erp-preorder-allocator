from __future__ import annotations

import sys
from pathlib import Path

import flet as ft
import pandas as pd

from src.ui.theme import LIGHT, DARK, Paleta, Modo
from src.ui.upload_view import UploadView
from src.ui.selection_view import SelectionView
from src.ui.consolidate_view import ConsolidateView

BASE_DIR = Path(__file__).resolve().parent.parent

try:
    from g360.ui.signature import G360Signature
except ImportError:
    G360Signature = None


class G360PreOrderAllocatorApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.modo = Modo.DARK
        self.p: Paleta = DARK
        self.df: pd.DataFrame | None = None
        self.vendedores_data: dict = {}
        self.seleccion: dict[str, list[str]] = {}
        self.lineas_sel: set[str] = set()

        self.sidebar_indicator_carga = ft.Container(width=4, height=24, bgcolor=self.p.accent, border_radius=2, visible=True)
        self.sidebar_indicator_seleccion = ft.Container(width=4, height=24, bgcolor=self.p.accent, border_radius=2, visible=False)
        self.sidebar_indicator_export = ft.Container(width=4, height=24, bgcolor=self.p.accent, border_radius=2, visible=False)
        self.btn_limpiar = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.DELETE_SWEEP, size=18, color=self.p.danger),
                ft.Text("Limpiar todo", size=13, color=self.p.danger, weight=ft.FontWeight.W_500),
            ], spacing=10),
            padding=ft.Padding(12, 10, 12, 10),
            border_radius=10,
            on_click=lambda _: self._limpiar_todo(),
            on_hover=lambda e: self._sidebar_hover(e),
            visible=False,
        )

        self.main_content = ft.Container(expand=True, padding=ft.Padding(24, 20, 24, 20))
        self._setup_page()
        self._init_views()
        self._build_ui()

    def _setup_page(self):
        self.page.title = "PreOrder Allocator - G360"
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.window.min_width = 900
        self.page.window.min_height = 600
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = self.p.bg
        self.page.padding = 0
        self.page.navigation_bar = None
        self.page.appbar = None

        ico = BASE_DIR / "assets" / "images" / "cipsa.ico"
        if ico.exists():
            self.page.window.icon = str(ico)

    def _init_views(self):
        self.upload_view = UploadView(self.page, self.p, self._on_data_loaded)
        self.selection_view = SelectionView(self.page, self.p, self._on_selection_ready)
        self.consolidate_view = ConsolidateView(self.page, self.p)

    def _build_ui(self):
        sidebar = self._build_sidebar()
        self.main_content.content = self.upload_view.build()
        self.page.add(
            ft.Row([sidebar, self.main_content], spacing=0, expand=True, vertical_alignment=ft.CrossAxisAlignment.STRETCH)
        )
        self.page.update()

    def _build_sidebar(self) -> ft.Container:
        def _item(icon, text, indicator, on_click, tooltip=""):
            return ft.Container(
                content=ft.Row([
                    indicator,
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(icon, size=20, color=ft.Colors.GREY_400),
                            ft.Text(text, size=13, color=ft.Colors.GREY_400, weight=ft.FontWeight.W_500),
                        ], spacing=12),
                        padding=ft.Padding(12, 10, 12, 10),
                        border_radius=10,
                        on_click=on_click,
                        on_hover=lambda e: self._sidebar_hover(e),
                        expand=True,
                    ),
                ], spacing=0),
                tooltip=tooltip,
            )

        logo_path = str(BASE_DIR / "assets" / "images" / "Logo_cipsa_solid.svg")
        logo = ft.Image(src=logo_path, width=42, height=42) if Path(logo_path).exists() else ft.Text("CIPSA", size=18, weight=ft.FontWeight.W_900, color=self.p.accent)

        return ft.Container(
            width=200,
            padding=ft.Padding(10, 30, 10, 20),
            bgcolor=self.p.surface,
            content=ft.Column([
                ft.Container(
                    content=ft.Row([logo], alignment=ft.MainAxisAlignment.CENTER),
                    margin=ft.Margin(0, 0, 0, 30),
                ),
                ft.Text("MODULOS", size=11, weight=ft.FontWeight.W_700, color=self.p.text_secondary),
                ft.Divider(height=8, color="transparent"),
                _item(ft.Icons.UPLOAD_FILE, "Carga Masiva", self.sidebar_indicator_carga,
                      lambda _: self._switch_to("carga"), "Cargar archivos XLSX"),
                _item(ft.Icons.TUNE, "Seleccionar", self.sidebar_indicator_seleccion,
                      lambda _: self._switch_to("seleccion"), "Seleccionar vendedores y clientes"),
                _item(ft.Icons.ASSESSMENT, "Consolidado", self.sidebar_indicator_export,
                      lambda _: self._switch_to("exportar"), "Exportar reporte consolidado"),
                ft.Divider(height=20, color=self.p.border),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.DARK_MODE if self.modo == Modo.DARK else ft.Icons.LIGHT_MODE,
                                size=18, color=self.p.text_secondary),
                        ft.Text("Tema", size=11, color=self.p.text_secondary),
                        ft.Container(expand=True),
                        ft.Switch(value=self.modo == Modo.DARK, on_change=self._toggle_theme,
                                  active_color=self.p.accent),
                    ], spacing=6),
                    padding=8,
                ),
                self.btn_limpiar,
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Column([
                        ft.Divider(height=12, color=self.p.border),
                        G360Signature(mode="powered", version="2.0") if G360Signature
                        else ft.Text("powered by G360", color=self.p.accent, size=9),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(0, 0, 0, 6),
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.START, spacing=4),
        )

    def _sidebar_hover(self, e):
        e.control.bgcolor = ft.Colors.with_opacity(0.05, ft.Colors.WHITE) if e.data == "true" else None
        e.control.update()

    def _toggle_theme(self, e):
        self.modo = Modo.DARK if e.control.value else Modo.LIGHT
        self.p = DARK if self.modo == Modo.DARK else LIGHT
        self.page.theme_mode = ft.ThemeMode.DARK if self.modo == Modo.DARK else ft.ThemeMode.LIGHT
        self.page.bgcolor = self.p.bg
        self._rebuild()

    def _build_title_bar(self, current: str) -> ft.Container:
        steps_data = [("carga", "1. Carga"), ("seleccion", "2. Seleccion"), ("exportar", "3. Consolidado")]
        step_items = []
        for key, label in steps_data:
            is_active = key == current
            step_items.append(ft.Text(
                label, size=12,
                weight=ft.FontWeight.W_700 if is_active else ft.FontWeight.W_500,
                color=self.p.accent if is_active else self.p.text_secondary,
            ))
            if key != "exportar":
                step_items.append(ft.Text("\u203A", size=16, color=self.p.text_secondary))

        return ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text("PreOrder Allocator", size=16, weight=ft.FontWeight.W_800, color=self.p.text),
                    ft.Text("Analisis de compras y participacion por SKU", size=10, color=self.p.text_secondary),
                ], spacing=0),
                ft.Container(expand=True),
                ft.Row(step_items, spacing=6),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(0, 0, 0, 10),
        )

    def _switch_to(self, view: str):
        self.sidebar_indicator_carga.visible = view == "carga"
        self.sidebar_indicator_seleccion.visible = view == "seleccion"
        self.sidebar_indicator_export.visible = view == "exportar"

        if view == "carga":
            view_content = self.upload_view.build()
        elif view == "seleccion":
            view_content = self.selection_view.build()
        else:
            if self.seleccion:
                self.consolidate_view.set_data(self.vendedores_data, self.seleccion, lineas_sel=self.lineas_sel)
            view_content = self.consolidate_view.build()

        self.main_content.content = ft.Column([
            self._build_title_bar(view),
            ft.Divider(height=8, color=self.p.border),
            view_content,
        ], spacing=0, expand=True)
        self.page.update()

    def _rebuild(self):
        self.page.overlay.clear()
        self.upload_view = UploadView(self.page, self.p, self._on_data_loaded)
        self.selection_view = SelectionView(self.page, self.p, self._on_selection_ready)
        self.consolidate_view = ConsolidateView(self.page, self.p)
        if self.df is not None:
            self.selection_view.set_data(self.df)
            if self.seleccion:
                self.consolidate_view.set_data(self.vendedores_data, self.seleccion, lineas_sel=self.lineas_sel)

        current = "carga"
        if self.sidebar_indicator_seleccion.visible:
            current = "seleccion"
        elif self.sidebar_indicator_export.visible:
            current = "exportar"
        self._switch_to(current)

    def _on_data_loaded(self, df: pd.DataFrame):
        self.df = df
        self.selection_view.set_data(df)
        self.sidebar_indicator_seleccion.visible = True
        self.btn_limpiar.visible = True
        self.page.update()

    def _on_selection_ready(self, seleccion: dict[str, list[str]], lineas_sel: set[str] | None = None):
        self.seleccion = seleccion
        self.lineas_sel = lineas_sel or set()
        self.vendedores_data = self.selection_view.vendedores_data
        self.consolidate_view.set_data(self.vendedores_data, seleccion, lineas_sel=self.lineas_sel)
        self.sidebar_indicator_export.visible = True
        self._switch_to("exportar")

    def _limpiar_todo(self):
        self.df = None
        self.vendedores_data.clear()
        self.seleccion.clear()
        self.lineas_sel.clear()
        self._init_views()
        self.sidebar_indicator_carga.visible = True
        self.sidebar_indicator_seleccion.visible = False
        self.sidebar_indicator_export.visible = False
        self.btn_limpiar.visible = False
        self._switch_to("carga")


def main(page: ft.Page):
    G360PreOrderAllocatorApp(page)
