# PreOrder Allocator

> Analisis de compras y participacion por SKU a partir de reportes ERP

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)

---

## Tabla de Contenidos

- [Descripcion](#descripcion)
- [Caracteristicas](#caracteristicas)
- [Tecnologias](#tecnologias)
- [Instalacion](#instalacion)
- [Uso](#uso)
- [Estructura](#estructura)
- [Version Portable](#version-portable)
- [Ecosistema G360](#ecosistema-g360)

---

## Descripcion

Aplicacion de escritorio para analizar compras por SKU y determinar su participacion porcentual en las ventas totales de un periodo seleccionado. Carga reportes ERP en formato XLSX, permite filtrar por lineas de producto, vendedores, clientes y rango de fechas, y exporta un consolidado profesional por cliente.

---

## Caracteristicas

- **Carga multiple**: Importa uno o mas archivos XLSX del ERP con deteccion automatica de encabezados
- **Filtro por lineas**: Selecciona lineas de producto especificas para analizar
- **Seleccion granular**: Elige vendedores y clientes individuales
- **Rango de fechas**: Filtra por periodo con auto-formato dd/mm/aaaa
- **Ordenamiento en Excel**: Los datos se exportan como **Tabla de Excel** con filtros y ordenamiento por cualquier columna (SKU, LINEA, CANTIDAD, SOLES, %)
- **Sucursales**: Desglose opcional por sucursal por cliente
- **Exportacion XLSX**: Un archivo por vendedor con una hoja por cliente identificada con ID, formato profesional con encabezados verdes, totales fijos y porcentajes como formula viva `=IFERROR()`
- **Progreso por vendedor**: Barras de progreso individuales que se completan al finalizar cada archivo
- **Tema moderno**: Paletas light/dark con efecto glassmorphism, accent G360 `#00d084`
- **Version portable**: Carpeta autonoma para trasladar a cualquier PC con Windows

---

## Tecnologias

- **Core**: Python 3.11
- **UI**: Flet (Flutter-based Python framework)
- **Procesamiento**: Pandas
- **Exportacion**: Openpyxl
- **Runtime**: uv (gestor de paquetes Python)

---

## Instalacion

### Requisitos

- Windows 10+
- Python 3.11 (se instala automaticamente si no existe)
- Conexion a internet (solo la primera ejecucion)

### Pasos

```bash
git clone https://github.com/carloscus/g360-erp-preorder-allocator.git
cd g360-erp-preorder-allocator
run.bat
```

Esto:

1. Detecta o instala uv
2. Detecta o instala Python 3.11 via uv
3. Crea `.venv` con todas las dependencias
4. Crea acceso directo en el escritorio
5. Ejecuta la aplicacion

### Manual

```bash
uv venv .venv --python 3.11 --seed
uv sync
.venv\Scripts\python.exe main.py
```

---

## Uso

La aplicacion sigue un flujo de 3 pasos:

1. **Carga Masiva** — Selecciona archivos XLSX exportados del ERP. El parser detecta columnas automaticamente.
2. **Seleccion** — Filtra por lineas de producto, elige un vendedor y selecciona sus clientes.
3. **Consolidado** — Configura rango de fechas y sucursales, luego exporta a XLSX. Los datos se exportan como **Tabla de Excel**: ordena y filtra directamente desde los encabezados.

Los reportes se guardan en el Escritorio con el formato `G360_Consolidado_{vendedor}_{fecha}.xlsx`.

---

## Estructura

```
g360-erp-preorder-allocator/
├── main.py                  # Entry point
├── run.bat                  # Launcher auto-instalable (uv + Python 3.11)
├── pyproject.toml           # Configuracion del proyecto
├── sync_portable.py         # Sincroniza cambios a la version portable
├── create_shortcut.vbs      # Acceso directo en escritorio
├── INSTRUCCIONES.txt        # Instructivo para usuario final
├── assets/images/           # Iconos y logos (CIPSA, G360)
├── src/
│   ├── app.py               # App Flet principal
│   ├── core/
│   │   ├── parser.py        # Parsing y normalizacion XLSX
│   │   ├── models.py        # Modelos de datos (dataclasses)
│   │   └── exporter.py      # Generacion XLSX consolidado
│   └── ui/
│       ├── upload_view.py   # Vista de carga de archivos
│       ├── selection_view.py# Vista de seleccion vendedor/cliente
│       ├── consolidate_view.py # Vista de filtros y exportacion
│       └── theme.py         # Paletas de colores claro/oscuro
└── g360-preorder-allocator-portable/  # Version portable
```

---

## Version Portable

La carpeta `g360-preorder-allocator-portable/` contiene los archivos minimos para trasladar a otra PC. Simplemente copia toda la carpeta, ejecuta `run.bat` y se auto-instala.

Para sincronizar cambios desde el proyecto fuente:

```bash
uv run python sync_portable.py
```

---

## Ecosistema G360

Este proyecto forma parte de la familia de microherramientas **G360** para apoyo CRM y gestion de datos en escritorio, enfocadas en areas como ventas, finanzas y logistica.

**Marca**: G360
**Isotipo**: 3 puntos verticales paralelos (gris-verde-gris) + chevron `>`
**Autor**: Carlos Cusi
**Desarrollo**: Con asistencia de herramientas de codigo IA (Vibe Code)
**Powered by**: [g360-signature](https://github.com/carloscus/g360-signature)
