from __future__ import annotations

import flet as ft
import pandas as pd

from src.core.models import VendedorResumen, ClienteResumen, ItemConsolidado
from src.ui.theme import Paleta


class SelectionView:
    def __init__(self, page: ft.Page, p: Paleta, on_selection_ready):
        self.page = page
        self.p = p
        self.on_selection_ready = on_selection_ready
        self.df: pd.DataFrame | None = None

        self.vendedores_data: dict[str, VendedorResumen] = {}
        self.clientes_seleccion: dict[str, set[str]] = {}
        self.vendedor_actual: str | None = None
        self.lineas_sel: set[str] = set()
        self._lineas_disponibles: list[str] = []
        self._linea_checkboxes: list[ft.Checkbox] = []
        self._todo_lineas: ft.Checkbox | None = None
        self._tiene_sucursales: bool = False

        self.vendedores_container = ft.Column(spacing=4, scroll=ft.ScrollMode.ADAPTIVE)
        self.lineas_container = ft.Column(spacing=4)
        self.resumen_container = ft.Container(
            content=ft.Text("", size=13, weight=ft.FontWeight.W_600, color=self.p.accent),
            padding=ft.Padding(10, 6, 10, 6),
            bgcolor=ft.Colors.with_opacity(0.1, self.p.accent),
            border_radius=8,
            border=ft.BorderSide(1, ft.Colors.with_opacity(0.2, self.p.accent)),
            visible=False,
            expand=True,
        )
        self.btn_generar = ft.FilledButton(
            "GENERAR REPORTE XLSX",
            icon=ft.Icons.FILE_DOWNLOAD_ROUNDED,
            disabled=True,
            on_click=lambda _: self._notificar(),
        )
        self.vendor_label = ft.Text("Selecciona un vendedor", size=13, color=self.p.text_secondary)
        self.btn_seleccionar_clientes = ft.FilledButton(
            "SELECCIONAR CLIENTES",
            icon=ft.Icons.PEOPLE,
            disabled=True,
            visible=False,
            on_click=lambda _: self._abrir_modal_clientes(),
        )
        self._modal_vid: str | None = None
        self._modal_search: ft.TextField | None = None
        self._modal_list: ft.Column | None = None
        self._modal_counter: ft.Text | None = None
        self._modal_search_text: str = ""
        self._modal_temp_sel: set[str] = set()
        self._modal_abierto: bool = False

    def set_data(self, df: pd.DataFrame):
        self.df = df
        self.clientes_seleccion.clear()
        self.vendedor_actual = None
        self._tiene_sucursales = "COD_SUCURSAL" in df.columns and "NOM_SUCURSAL" in df.columns
        self._construir_vendedores()
        self._construir_lineas()
        self._actualizar_resumen()

    def _construir_vendedores(self):
        self.vendedores_data.clear()
        self.vendedores_container.controls.clear()

        for vid, vdf in self.df.groupby("ID_VENDEDOR"):
            nom = vdf["NOM_VENDEDOR"].iloc[0]
            clientes_unicos = vdf["NOM_CLIENTE"].unique()

            ven = VendedorResumen(id_vendedor=vid, nom_vendedor=nom)
            for nc in clientes_unicos:
                cdf = vdf[vdf["NOM_CLIENTE"] == nc]
                items = []
                for _, row in cdf.iterrows():
                    item = ItemConsolidado(
                        sku=str(row["ID_ARTICULO"]),
                        nom_articulo=str(row["NOM_ARTICULO"]),
                        id_linea=str(row.get("ID_LINEA", "")),
                        nom_linea=str(row.get("NOM_LINEA", "")),
                        cantidad=float(row["CANTIDAD"]),
                        soles=float(row["SOLES"]),
                        fecha_orig=str(row.get("FECHA_ORIG", "")),
                    )
                    if self._tiene_sucursales:
                        item.cod_sucursal = str(row.get("COD_SUCURSAL", ""))
                        item.nom_sucursal = str(row.get("NOM_SUCURSAL", ""))
                    items.append(item)
                cli = ClienteResumen(
                    id_cliente=str(cdf["ID_CLIENTE"].iloc[0]),
                    doc_cliente=str(cdf["DOC_CLIENTE"].iloc[0]),
                    nom_cliente=nc,
                    items=items,
                )
                cli.total_cantidad = sum(i.cantidad for i in items)
                cli.total_soles = sum(i.soles for i in items)
                ven.clientes[nc] = cli

            self.vendedores_data[vid] = ven
            self.vendedores_container.controls.append(
                self._build_vendor_card(vid, ven)
            )

    def _build_vendor_card(self, vid: str, ven: VendedorResumen) -> ft.Container:
        badge = ft.Container(
            content=ft.Text("0", size=10, weight=ft.FontWeight.W_700, color=ft.Colors.WHITE),
            bgcolor=self.p.accent,
            border_radius=10,
            padding=ft.Padding(6, 2, 6, 2),
            visible=False,
        )
        card = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"{vid} - {ven.nom_vendedor}", size=12, weight=ft.FontWeight.W_500, color=self.p.text),
                        ft.Text(f"{len(ven.clientes)} clientes", size=10, color=self.p.text_secondary),
                    ], spacing=2),
                    expand=True,
                ),
                badge,
            ], spacing=6),
            padding=ft.Padding(12, 10, 12, 10),
            bgcolor=self.p.surface_hover,
            border_radius=10,
            on_click=lambda _, v=vid: self._seleccionar_vendedor(v),
        )
        card.data = {"badge": badge, "ven": ven}
        return card

    def _seleccionar_vendedor(self, vid: str):
        if self.vendedor_actual == vid:
            return
        self._guardar_seleccion_actual()
        self.vendedor_actual = vid
        self._actualizar_vendedores_ui()
        ven = self.vendedores_data[vid]
        self.vendor_label.value = f"{vid} - {ven.nom_vendedor}"
        sel = self.clientes_seleccion.get(vid, set())
        self.btn_seleccionar_clientes.text = f"SELECCIONAR CLIENTES ({len(sel)}/{len(ven.clientes)})"
        self.btn_seleccionar_clientes.disabled = False
        self.btn_seleccionar_clientes.visible = True
        self._actualizar_resumen()

    def _guardar_seleccion_actual(self):
        if not self._modal_vid:
            return
        if self._modal_temp_sel:
            self.clientes_seleccion[self._modal_vid] = set(self._modal_temp_sel)
        elif self._modal_vid in self.clientes_seleccion:
            del self.clientes_seleccion[self._modal_vid]

    def _actualizar_vendedores_ui(self):
        for card in self.vendedores_container.controls:
            vid = card.data["ven"].id_vendedor
            is_active = vid == self.vendedor_actual
            card.bgcolor = self.p.accent if is_active else self.p.surface_hover
            for child in card.content.controls:
                if isinstance(child, ft.Container) and hasattr(child, 'content'):
                    content = child.content
                    if isinstance(content, ft.Column):
                        for t in content.controls:
                            if isinstance(t, ft.Text):
                                t.color = ft.Colors.WHITE if is_active else self.p.text
                            elif isinstance(t, ft.Text):
                                t.color = ft.Colors.WHITE if is_active else self.p.text_secondary
            badge = card.data["badge"]
            cnt = len(self.clientes_seleccion.get(vid, set()))
            badge.visible = cnt > 0
            badge.content.value = str(cnt)
            card.update()

    def _construir_lineas(self):
        self.lineas_container.controls.clear()
        self._linea_checkboxes.clear()
        if self.df is None or "NOM_LINEA" not in self.df.columns or "ID_LINEA" not in self.df.columns:
            return

        df_lineas = self.df[["ID_LINEA", "NOM_LINEA"]].dropna().drop_duplicates()
        self._lineas_disponibles = sorted(
            f"{row['ID_LINEA']} - {row['NOM_LINEA']}"
            for _, row in df_lineas.iterrows()
        )

        self._todo_lineas = ft.Checkbox(
            label="Todas las lineas",
            value=True,
            on_change=lambda e: self._on_todas_lineas(e),
            label_style=ft.TextStyle(size=11),
        )
        self.lineas_container.controls.append(ft.Container(content=self._todo_lineas, padding=2))

        for i in range(0, len(self._lineas_disponibles), 2):
            row_controls = []
            for j in range(2):
                idx = i + j
                if idx < len(self._lineas_disponibles):
                    cb = ft.Checkbox(
                        label=self._lineas_disponibles[idx],
                        value=True,
                        on_change=lambda _: self._lineas_changed(),
                        label_style=ft.TextStyle(size=11),
                    )
                    self._linea_checkboxes.append(cb)
                    row_controls.append(
                        ft.Container(content=cb, padding=ft.Padding(20, 0, 0, 0), expand=True)
                    )
                else:
                    row_controls.append(ft.Container(expand=True))
            self.lineas_container.controls.append(
                ft.Row(row_controls, spacing=4)
            )

    def _on_todas_lineas(self, e):
        val = e.control.value
        for cb in self._linea_checkboxes:
            cb.value = val
            cb.update()
        self._lineas_changed()

    def _lineas_changed(self):
        self.lineas_sel = set()
        for cb in self._linea_checkboxes:
            if cb.value:
                self.lineas_sel.add(cb.label)
        if self._todo_lineas:
            todas = all(cb.value for cb in self._linea_checkboxes)
            if self._todo_lineas.value != todas:
                self._todo_lineas.value = todas
                self._todo_lineas.update()
        if self.vendedor_actual:
            sel = self.clientes_seleccion.get(self.vendedor_actual, set())
            ven = self.vendedores_data.get(self.vendedor_actual)
            if ven:
                total = len(ven.clientes)
                self.btn_seleccionar_clientes.text = f"SELECCIONAR CLIENTES ({len(sel)}/{total})"
        self._actualizar_resumen()

    def _abrir_modal_clientes(self):
        vid = self.vendedor_actual
        if not vid:
            return
        ven = self.vendedores_data.get(vid)
        if not ven:
            return

        self._modal_vid = vid
        self._modal_temp_sel = set(self.clientes_seleccion.get(vid, set()))
        sel_count = len(self._modal_temp_sel)

        if self._modal_search is None:
            self._modal_search = ft.TextField(
                hint_text="Buscar cliente por nombre...",
                prefix_icon=ft.Icons.SEARCH,
                on_change=lambda e: self._on_modal_search(e.control.value),
                bgcolor=self.p.input_bg,
                border_radius=8,
                text_size=13,
            )
        self._modal_search.value = self._modal_search_text

        if self._modal_list is None:
            self._modal_list = ft.Column(spacing=2, scroll=ft.ScrollMode.ADAPTIVE)

        if self._modal_counter is None:
            self._modal_counter = ft.Text("0 seleccionados", size=11, color=self.p.accent)

        self._modal_counter.value = f"{sel_count} seleccionados"
        self._build_modal_clientes(self._modal_search_text)

        header = ft.Container(
            content=ft.Row([
                ft.Text(f"{vid} - {ven.nom_vendedor}", size=11, color=self.p.text_secondary, expand=True),
                self._modal_counter,
                ft.TextButton("Todo", on_click=lambda _: self._modal_seleccionar_todo(True)),
                ft.TextButton("Ninguno", on_click=lambda _: self._modal_seleccionar_todo(False)),
            ], spacing=4),
            bgcolor=ft.Colors.with_opacity(0.05, self.p.accent),
            padding=ft.Padding(8, 4, 8, 4),
            border_radius=6,
        )

        dialog = ft.AlertDialog(
            title=ft.Text(f"Seleccionar clientes", size=16, weight=ft.FontWeight.W_700, color=self.p.text),
            content=ft.Column([
                header,
                self._modal_search,
                ft.Divider(height=4, color="transparent"),
                ft.Container(
                    content=self._modal_list,
                    height=350,
                    border_radius=8,
                    bgcolor=self.p.surface_hover,
                    padding=6,
                ),
            ], spacing=6, width=520, height=460),
            actions=[
                ft.TextButton("CANCELAR", on_click=lambda e: self._cerrar_modal(False)),
                ft.FilledButton("CONFIRMAR", on_click=lambda e: self._cerrar_modal(True)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.show_dialog(dialog)
        self._modal_abierto = True

    def _on_modal_search(self, query: str):
        self._modal_search_text = query
        self._build_modal_clientes(query)
        if self._modal_abierto:
            self._modal_list.update()
            self._modal_counter.update()

    def _build_modal_clientes(self, query: str):
        if not self._modal_list or not self._modal_vid:
            return
        self._modal_list.controls.clear()
        ven = self.vendedores_data.get(self._modal_vid)
        if not ven:
            return

        query = query.lower().strip()
        temp_sel = self._modal_temp_sel

        lineas_sel = self.lineas_sel
        todas_lineas = len(lineas_sel) == len(self._lineas_disponibles) if self._lineas_disponibles else True

        for nom_cli in sorted(ven.clientes.keys()):
            if query and query not in nom_cli.lower():
                continue
            cli = ven.clientes[nom_cli]
            if not todas_lineas and lineas_sel:
                lineas_cli = {f"{i.id_linea} - {i.nom_linea}" for i in cli.items}
                if not (lineas_cli & lineas_sel):
                    continue
            checked = nom_cli in temp_sel
            label = f"{cli.doc_cliente} | {cli.id_cliente} | {cli.nom_cliente}"
            cb = ft.Checkbox(
                label=label,
                value=checked,
                data=nom_cli,
                on_change=lambda e: self._on_modal_check_change(e),
                label_style=ft.TextStyle(size=13),
            )
            self._modal_list.controls.append(
                ft.Container(content=cb, padding=ft.Padding(4, 0, 4, 2))
            )

    def _on_modal_check_change(self, e):
        cb = e.control
        nom = cb.data
        if cb.value:
            self._modal_temp_sel.add(nom)
        else:
            self._modal_temp_sel.discard(nom)
        self._actualizar_modal_counter()
        if self._modal_counter:
            self._modal_counter.update()

    def _actualizar_modal_counter(self):
        if not self._modal_counter:
            return
        self._modal_counter.value = f"{len(self._modal_temp_sel)} seleccionados"

    def _modal_seleccionar_todo(self, val: bool):
        if not self._modal_list or not self._modal_vid:
            return
        ven = self.vendedores_data.get(self._modal_vid)
        if not ven:
            return
        self._modal_temp_sel = set(ven.clientes.keys()) if val else set()
        for container in self._modal_list.controls:
            cb = container.content
            if isinstance(cb, ft.Checkbox):
                cb.value = val
                cb.update()
        self._actualizar_modal_counter()
        if self._modal_counter:
            self._modal_counter.update()

    def _cerrar_modal(self, confirmar: bool):
        if self._modal_search:
            self._modal_search_text = self._modal_search.value
        self._modal_abierto = False
        self.page.pop_dialog()

        if confirmar and self._modal_vid:
            if self._modal_temp_sel:
                self.clientes_seleccion[self._modal_vid] = set(self._modal_temp_sel)
            elif self._modal_vid in self.clientes_seleccion:
                del self.clientes_seleccion[self._modal_vid]

            ven = self.vendedores_data.get(self._modal_vid)
            if ven:
                self.btn_seleccionar_clientes.text = f"SELECCIONAR CLIENTES ({len(self._modal_temp_sel)}/{len(ven.clientes)})"

        self._modal_vid = None
        self._actualizar_vendedores_ui()
        self._actualizar_resumen()
        self.page.update()

    def _actualizar_resumen(self):
        total = sum(len(s) for s in self.clientes_seleccion.values())
        partes = []
        for vid, s in self.clientes_seleccion.items():
            if s:
                ven = self.vendedores_data.get(vid)
                if ven:
                    partes.append(f"{ven.nom_vendedor}: {len(s)}")
        text = f"{total} cliente(s) seleccionado(s)" + (f" ({', '.join(partes)})" if partes else "")
        self.resumen_container.content.value = text
        self.resumen_container.visible = total > 0
        self.btn_generar.disabled = total == 0
        self.page.update()

    def _notificar(self):
        seleccion = {}
        for vid, clientes in self.clientes_seleccion.items():
            if clientes:
                seleccion[vid] = list(clientes)
        if self.on_selection_ready:
            self.on_selection_ready(seleccion, lineas_sel=self.lineas_sel)

    def build(self) -> ft.Control:
        return ft.Column([
            ft.Text("1. Filtra por lineas  2. Elige un vendedor  3. Selecciona sus clientes", size=12, color=self.p.text_secondary),
            ft.Divider(height=8, color="transparent"),
            ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Text("LINEAS (filtro)", size=11, weight=ft.FontWeight.W_600, color=self.p.accent),
                        ft.Container(expand=True, content=self.lineas_container),
                    ], spacing=4, expand=True),
                    padding=10, bgcolor=self.p.surface, border_radius=10, border=ft.BorderSide(1, self.p.border),
                    expand=True,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("VENDEDORES", size=11, weight=ft.FontWeight.W_600, color=self.p.accent),
                        ft.Container(expand=True, content=self.vendedores_container),
                    ], spacing=4, expand=True),
                    padding=10, bgcolor=self.p.surface, border_radius=10, border=ft.BorderSide(1, self.p.border),
                    expand=True,
                ),
            ], spacing=12, expand=True),
            ft.Divider(height=4, color="transparent"),
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.PEOPLE, size=14, color=self.p.accent),
                        ft.Text("CLIENTES DE", size=11, weight=ft.FontWeight.W_600, color=self.p.accent),
                        self.vendor_label,
                    ], spacing=4),
                    ft.Container(
                        content=self.btn_seleccionar_clientes,
                        alignment=ft.alignment.Alignment(0, 0),
                        padding=ft.Padding(0, 6, 0, 6),
                    ),
                ], spacing=4),
                padding=10, bgcolor=self.p.surface, border_radius=10, border=ft.BorderSide(1, self.p.border),
            ),
            ft.Divider(height=4, color="transparent"),
            ft.Row([self.resumen_container, self.btn_generar], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ], spacing=4, expand=True, scroll=ft.ScrollMode.ADAPTIVE)
