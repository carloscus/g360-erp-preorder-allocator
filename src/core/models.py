from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ArchivoCargado:
    ruta: str
    nombre: str
    filas: int
    estado: str = "ok"


@dataclass
class ItemConsolidado:
    sku: str
    nom_articulo: str
    id_linea: str
    nom_linea: str
    cantidad: float
    soles: float
    pct_cantidad: float = 0.0
    pct_soles: float = 0.0
    cod_sucursal: str = ""
    nom_sucursal: str = ""
    fecha_orig: str = ""


@dataclass
class ClienteResumen:
    id_cliente: str
    doc_cliente: str
    nom_cliente: str
    items: list[ItemConsolidado] = field(default_factory=list)
    total_cantidad: float = 0.0
    total_soles: float = 0.0

    @property
    def sku_count(self) -> int:
        return len(self.items)


@dataclass
class VendedorResumen:
    id_vendedor: str
    nom_vendedor: str
    clientes: dict[str, ClienteResumen] = field(default_factory=dict)
    _clientes_lista: list[str] = field(default_factory=list)

    @property
    def cliente_count(self) -> int:
        return len(self.clientes)

    @property
    def total_soles(self) -> float:
        return sum(c.total_soles for c in self.clientes.values())

    @property
    def nombres_cliente(self) -> list[str]:
        return sorted([c.nom_cliente for c in self.clientes.values()])


@dataclass
class EstadoApp:
    archivos: list[ArchivoCargado] = field(default_factory=list)
    vendedores: dict[str, VendedorResumen] = field(default_factory=dict)
    lineas_disponibles: list[str] = field(default_factory=list)
    df_raw: Optional["pd.DataFrame"] = None

    @property
    def total_registros(self) -> int:
        return sum(a.filas for a in self.archivos) if self.df_raw is not None else 0

    @property
    def vendedores_lista(self) -> list[str]:
        return sorted(self.vendedores.keys())
