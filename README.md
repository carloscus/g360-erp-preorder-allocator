# PreOrder Allocator

Analisis de compras y participacion por SKU a partir de reportes ERP.

## Flujo de uso

1. **Carga** — Selecciona uno o mas archivos XLSX exportados del ERP
2. **Seleccion** — Filtra por lineas de producto y selecciona vendedores/clientes
3. **Consolidado** — Aplica filtros por rango de fechas, ordena por SKU/linea/% y exporta a XLSX

## Requisitos

- Windows 10+
- Python 3.11
- Conexion a internet (solo la primera ejecucion)

## Instalacion y ejecucion

```bash
# Clonar o copiar la carpeta
cd g360-erp-preorder-allocator

# Ejecutar (auto-instala uv, Python 3.11, .venv y dependencias)
run.bat
```

O manualmente con uv:

```bash
uv venv .venv --python 3.11 --seed
uv sync
.venv\Scripts\python.exe main.py
```

## Version portable

La carpeta `g360-preorder-allocator-portable/` contiene los archivos minimos para trasladar a otra PC. Copia toda la carpeta, ejecuta `run.bat` y se auto-instala.

Para sincronizar cambios desde el proyecto fuente:

```bash
uv run python sync_portable.py
```

## Estructura

```
src/
├── app.py                 # Punto de entrada Flet
├── core/
│   ├── parser.py          # Parsing XLSX ERP
│   ├── models.py          # Modelos de datos
│   └── exporter.py        # Exportacion XLSX consolidado
└── ui/
    ├── upload_view.py     # Carga de archivos
    ├── selection_view.py  # Seleccion vendedor/cliente
    ├── consolidate_view.py# Filtros y exportacion
    └── theme.py           # Paletas de colores
```

## Dependencias

- flet — UI framework
- pandas — Procesamiento de datos
- openpyxl — Exportacion XLSX
- xlrd — Lectura XLS legacy
