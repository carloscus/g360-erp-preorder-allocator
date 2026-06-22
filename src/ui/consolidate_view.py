from __future__ import annotations

import os
import re
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional

import flet as ft

from src.core.exporter import exportar_xlsx
from src.core.models import VendedorResumen
from src.ui.theme import Paleta


def _parse_date(s: str) -> Optional[datetime]:
    if not s or not isinstance(s, str):
        return None
    s = s.strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def _auto_format_date(tf: ft.TextField):
    raw = re.sub(r"\D", "", tf.value or "")
    raw = raw[:8]
    parts = []
    if len(raw) > 4:
        parts = [raw[:2], raw[2:4], raw[4:]]
    elif len(raw) > 2:
        parts = [raw[:2], raw[2:]]
    else:
        parts = [raw]
    formatted = "/".join(parts)
    if tf.value != formatted:
        tf.value = formatted


class ConsolidateView:
    def __init__(self, page: ft.Page, p: Paleta):
        self.page = page
        self.p = p
        self.vendedores: dict[str, VendedorResumen] = {}
        self.seleccion: dict[str, list[str]] = {}
        self.lineas_sel: set[str] = set()

        self.status = ft.Text("", size=13, color=p.text_secondary)
        self._prog_rows: dict[str, ft.Row] = {}
        self._prog_col = ft.Column(spacing=6, visible=False)
        self._progress_card = ft.Container(
            content=self._prog_col,
            padding=12,
            border_radius=10,
            bgcolor=self.p.glass_bg,
            border=ft.BorderSide(1, self.p.glass_border),
            blur=ft.Blur(12, 12),
        )

        self.suc_switch = ft.Switch(value=False, active_color=self.p.accent)
        self.suc_label = ft.Text("Incluir sucursales", size=12, color=self.p.text_secondary)

        self.fecha_inicio = ft.TextField(
            label="Fecha inicio",
            hint_text="dd/mm/aaaa",
            width=150,
            text_size=13,
            border_radius=8,
            bgcolor=self.p.input_bg,
            on_change=lambda e: self._on_fecha_input(e, self.fecha_inicio),
        )
        self.fecha_fin = ft.TextField(
            label="Fecha fin",
            hint_text="dd/mm/aaaa",
            width=150,
            text_size=13,
            border_radius=8,
            bgcolor=self.p.input_bg,
            on_change=lambda e: self._on_fecha_input(e, self.fecha_fin),
        )
        self.fecha_info = ft.Text("", size=11, color=self.p.text_secondary, visible=False)

    def _on_fecha_input(self, e, tf: ft.TextField):
        _auto_format_date(tf)
        self._on_fecha_change()

    def _on_fecha_change(self):
        inicio = self.fecha_inicio.value.strip()
        fin = self.fecha_fin.value.strip()
        if not inicio and not fin:
            self.fecha_info.visible = False
            self.page.update()
            return

        d1 = _parse_date(inicio)
        d2 = _parse_date(fin)
        if d1 and d2 and d1 > d2:
            self.fecha_info.value = "La fecha de inicio no puede ser mayor a la fecha fin"
            self.fecha_info.color = self.p.danger
            self.fecha_info.visible = True
            self.page.update()
            return

        total_items = 0
        items_en_rango = 0
        for vid in self.seleccion:
            ven = self.vendedores.get(vid)
            if not ven:
                continue
            for nom in self.seleccion[vid]:
                cli = ven.clientes.get(nom)
                if not cli:
                    continue
                for it in cli.items:
                    if self.lineas_sel:
                        linea_key = f"{it.id_linea} - {it.nom_linea}"
                        if linea_key not in self.lineas_sel:
                            continue
                    total_items += 1
                    fd = _parse_date(it.fecha_orig)
                    if fd is not None:
                        if (not d1 or fd >= d1) and (not d2 or fd <= d2):
                            items_en_rango += 1

        if total_items == 0:
            self.fecha_info.visible = False
        else:
            self.fecha_info.value = f"Filtrando: {items_en_rango}/{total_items} items"
            self.fecha_info.color = self.p.accent
            self.fecha_info.visible = True
        self.page.update()

    def set_data(self, vendedores: dict[str, VendedorResumen], seleccion: dict[str, list[str]], lineas_sel: set[str] | None = None):
        self.vendedores = vendedores
        self.seleccion = seleccion
        if lineas_sel is not None:
            self.lineas_sel = lineas_sel
        total = sum(len(c) for c in seleccion.values())
        self.status.value = f"Listo para exportar: {total} clientes"
        self.status.color = self.p.success
        self.fecha_inicio.value = ""
        self.fecha_fin.value = ""
        self.fecha_info.visible = False

    def _items_en_rango(self, items: list) -> list:
        inicio = self.fecha_inicio.value.strip()
        fin = self.fecha_fin.value.strip()
        if not inicio and not fin:
            return items
        d1 = _parse_date(inicio) if inicio else None
        d2 = _parse_date(fin) if fin else None
        if not d1 and not d2:
            return items
        result = []
        for it in items:
            fd = _parse_date(it.fecha_orig)
            if fd is None:
                continue
            if (not d1 or fd >= d1) and (not d2 or fd <= d2):
                result.append(it)
        return result

    def _exportar(self):
        vendedores_info = [
            (vid, vendedor.nom_vendedor)
            for vid, vendedor in self.vendedores.items()
            if self.seleccion.get(vid, [])
        ]
        if not vendedores_info:
            return

        self._prog_rows.clear()
        bars = []
        for _, nombre in vendedores_info:
            bar = ft.ProgressBar(width=380, color=self.p.accent, value=0)
            row = ft.Row([
                ft.Text(nombre, size=12, color=self.p.text, width=160),
                bar,
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER)
            self._prog_rows[nombre] = row
            bars.append(bar)
        self._prog_col.controls = list(self._prog_rows.values())
        self._prog_col.visible = True

        self.status.value = "Exportando..."
        self.status.color = self.p.accent
        self.page.update()

        def on_file_done(nombre: str):
            row = self._prog_rows.get(nombre)
            if row:
                bar = row.controls[1]
                bar.value = 1.0
                self.page.update()

        def task():
            try:
                paths = exportar_xlsx(
                    self.vendedores,
                    self.seleccion,
                    lineas_sel=self.lineas_sel,
                    carpeta=str(Path.home() / "Desktop"),
                    incluir_sucursales=self.suc_switch.value,
                    filter_items=self._items_en_rango,
                    on_file_done=on_file_done,
                )
                self.status.value = f"Reportes generados: {len(paths)} archivo(s)"
                self.status.color = self.p.success
                self.page.update()

                if paths:
                    folder = os.path.dirname(os.path.normpath(paths[0]))
                    subprocess.Popen(["explorer", folder])

            except Exception as ex:
                self.status.value = f"Error: {str(ex)}"
                self.status.color = self.p.danger
                self._prog_col.visible = False
                self.page.update()

        threading.Thread(target=task, daemon=True).start()

    def build(self) -> ft.Control:
        header = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.ASSESSMENT, color=self.p.accent, size=28),
                ft.Column([
                    ft.Text("EXPORTAR CONSOLIDADO", size=16, weight=ft.FontWeight.W_700, color=self.p.text),
                    ft.Text("Estructura: 1 archivo XLSX por vendedor, 1 hoja por cliente",
                            size=11, color=self.p.text_secondary),
                ], spacing=1),
            ], spacing=10),
            margin=ft.Margin(0, 0, 0, 12),
        )

        glass_kw = dict(
            padding=16, border_radius=10, expand=True,
            bgcolor=self.p.glass_bg,
            border=ft.BorderSide(1, self.p.glass_border),
            blur=ft.Blur(12, 12),
        )

        filtros = ft.Container(
            content=ft.Column([
                ft.Text("FILTROS", size=11, weight=ft.FontWeight.W_600, color=self.p.accent),
                ft.Divider(height=4, color="transparent"),
                ft.Text("Rango de fechas (FECHA_ORIG)", size=11, color=self.p.text_secondary),
                ft.Row([self.fecha_inicio, self.fecha_fin], spacing=8),
                self.fecha_info,
                ft.Divider(height=8, color="transparent"),
                ft.Text("Sucursales", size=11, color=self.p.text_secondary),
                ft.Row([self.suc_label, self.suc_switch], spacing=8),
            ], spacing=4),
            **glass_kw,
        )

        config = ft.Container(
            content=ft.Column([
                ft.Text("CONFIGURACION", size=11, weight=ft.FontWeight.W_600, color=self.p.accent),
                ft.Divider(height=4, color="transparent"),
                ft.Text("Los reportes se guardaran en el Escritorio.", size=11, color=self.p.text_secondary),
            ], spacing=4),
            **glass_kw,
        )

        acciones = ft.Container(
            content=ft.Column([
                self.status,
                ft.Divider(height=4, color="transparent"),
                ft.FilledButton(
                    "EXPORTAR AHORA",
                    icon=ft.Icons.FILE_DOWNLOAD_ROUNDED,
                    on_click=lambda _: self._exportar(),
                    height=44,
                ),
                self._progress_card,
            ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=16, border_radius=10,
            bgcolor=self.p.glass_bg,
            border=ft.BorderSide(1, self.p.glass_border),
            blur=ft.Blur(12, 12),
        )

        return ft.Column([
            ft.Text("Previsualizacion y exportacion del reporte consolidado",
                    size=12, color=self.p.text_secondary),
            ft.Divider(height=6, color="transparent"),
            header,
            ft.Row([filtros, config], spacing=12, vertical_alignment=ft.CrossAxisAlignment.START),
            ft.Divider(height=8, color="transparent"),
            acciones,
        ], spacing=4, expand=True)
