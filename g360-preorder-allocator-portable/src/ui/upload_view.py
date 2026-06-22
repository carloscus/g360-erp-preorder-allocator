from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import flet as ft
import pandas as pd

from src.core.parser import parse_multiple
from src.core.models import ArchivoCargado
from src.ui.theme import Paleta


class UploadView:
    def __init__(self, page: ft.Page, p: Paleta, on_procesado):
        self.page = page
        self.p = p
        self.on_procesado = on_procesado
        self.archivos: list[ArchivoCargado] = []
        self.df_final: pd.DataFrame | None = None

        self.progress = ft.ProgressBar(width=400, color=p.accent, visible=False)
        self.status = ft.Text("", size=13, color=p.text_secondary)
        self.file_list = ft.Column(spacing=4)

    def build(self) -> ft.Control:
        drop_zone = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.CLOUD_UPLOAD_OUTLINED, size=48, color=self.p.accent),
                ft.Text("Arrastra archivos XLSX aqui", size=14, color=self.p.text_secondary),
                ft.Text("o", size=12, color=self.p.text_secondary),
                ft.FilledTonalButton(
                    "Seleccionar archivos",
                    icon=ft.Icons.FOLDER_OPEN,
                    on_click=lambda _: self._pick_files_dialog(),
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
            padding=40,
            bgcolor=self.p.glass_bg,
            border_radius=18,
            border=ft.BorderSide(2, self.p.glass_border),
            blur=ft.Blur(12, 12),
            animate=ft.Animation(300, ft.AnimationCurve.DECELERATE),
            on_hover=lambda e: self._on_drop_hover(e),
        )

        procesar_btn = ft.FilledButton(
            "PROCESAR ARCHIVOS",
            icon=ft.Icons.PLAY_ARROW_ROUNDED,
            disabled=True,
            on_click=lambda _: self._procesar(),
            ref=ft.Ref(),
        )
        self.btn_procesar = procesar_btn

        return ft.Column([
            ft.Text("Selecciona uno o mas archivos XLSX del reporte ERP", size=12, color=self.p.text_secondary),
            ft.Divider(height=12, color="transparent"),
            drop_zone,
            ft.Divider(height=8, color="transparent"),
            self.file_list,
            ft.Divider(height=8, color="transparent"),
            ft.Row([procesar_btn, self.progress], spacing=20),
            self.status,
        ], spacing=4)

    def _on_drop_hover(self, e):
        c = e.control
        if e.data == "true":
            c.border = ft.BorderSide(2, self.p.accent)
            c.bgcolor = ft.Colors.with_opacity(0.1, self.p.accent)
        else:
            c.border = ft.BorderSide(2, self.p.glass_border)
            c.bgcolor = self.p.glass_bg
        c.update()

    def _pick_files_dialog(self):
        def _run():
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            paths = filedialog.askopenfilenames(
                title="Seleccionar archivos XLSX",
                filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
            )
            root.destroy()
            if paths:
                self._add_files(list(paths))
        threading.Thread(target=_run, daemon=True).start()

    def _add_files(self, paths: list[str]):
        for path in paths:
            name = Path(path).name
            if path not in [a.ruta for a in self.archivos]:
                self.archivos.append(ArchivoCargado(ruta=path, nombre=name, filas=0))
                self.file_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.DESCRIPTION, size=18, color=self.p.accent),
                            ft.Text(name, size=12, color=self.p.text, expand=True),
                            ft.Text("pendiente", size=10, color=self.p.text_secondary),
                        ], spacing=8),
                        padding=8,
                        bgcolor=self.p.glass_bg,
                        border_radius=8,
                        blur=ft.Blur(8, 8),
                    )
                )
        self.btn_procesar.disabled = False
        self.status.value = f"{len(self.archivos)} archivo(s) seleccionado(s)"
        self.page.update()

    def _procesar(self):
        self.btn_procesar.disabled = True
        self.progress.visible = True
        self.status.value = "Procesando archivos..."
        self.status.color = self.p.accent
        self.page.update()

        def task():
            try:
                paths = [a.ruta for a in self.archivos if a.ruta]
                df = parse_multiple(paths)
                self.df_final = df
                for a in self.archivos:
                    a.filas = len(df)
                    a.estado = "ok"

                self.status.value = f"Listo: {len(df)} registros cargados"
                self.status.color = self.p.success
                self.progress.visible = False
                self.page.update()

                if self.on_procesado:
                    self.on_procesado(df)
            except Exception as ex:
                self.status.value = f"Error: {str(ex)}"
                self.status.color = self.p.danger
                self.progress.visible = False
                self.btn_procesar.disabled = False
                self.page.update()

        threading.Thread(target=task, daemon=True).start()
