from __future__ import annotations

import logging
import re
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

COLUMNAS_HISTORIAL = (
    "ANHO", "MES", "DOC_CLIENTE", "ID_CLIENTE", "NOM_CLIENTE",
    "ID_LOCALIDAD_UBIGEO", "NOM_DEPARTAMENTO", "NOM_PROVINCIA", "NOM_DISTRITO",
    "ID_LINEA", "NOM_LINEA", "ID_GRUPO", "NOM_GRUPO", "ID_TIPO", "NOM_TIPO",
    "ID_FAMILIA", "NOM_FAMILIA", "ESTADO_LINEA",
    "ID_ARTICULO", "NOM_ARTICULO",
    "ID_VENDEDOR", "NOM_VENDEDOR", "CANAL DE DISTRIBUCION",
    "COD_SUCURSAL", "NOM_SUCURSAL",
    "TPO_DOC", "SERIE_DOC", "NRO_DOC", "ORD_COMPRA", "ID_GUIA",
    "FECHA_ORIG", "REFERENCIA", "FECHA_REF", "MONEDA",
    "CANTIDAD", "SOLES", "DOLARES", "NOM_CONDICION_PAGO", "ID_PEDIDO",
    "FECHA_VENC", "DIVISION", "FEC_CARGO",
)

COLUMNAS_REQUERIDAS = ["ID_ARTICULO", "NOM_ARTICULO", "ID_LINEA", "NOM_LINEA",
                       "ID_CLIENTE", "NOM_CLIENTE", "DOC_CLIENTE",
                       "ID_VENDEDOR", "NOM_VENDEDOR", "CANTIDAD", "SOLES"]


def _limpiar_col(col) -> str:
    if pd.isna(col):
        return ""
    return str(col).replace("\ufeff", "").strip().upper()


def _identificar_headers(df: pd.DataFrame) -> pd.DataFrame:
    keywords = {"ANHO", "ANO", "DOC_CLIENTE", "ID_ARTICULO", "NRO_DOC", "NOM_CLIENTE"}
    header_idx = -1
    for i, row in df.iterrows():
        vals = {_limpiar_col(v) for v in row.values if pd.notna(v)}
        if len(keywords.intersection(vals)) >= 2:
            header_idx = i
            break
    if header_idx != -1:
        df.columns = [_limpiar_col(c) for c in df.iloc[header_idx]]
        df = df.iloc[header_idx + 1:].reset_index(drop=True)
    else:
        df.columns = [_limpiar_col(c) for c in df.columns]
    if not df.empty:
        last = df.iloc[-1].astype(str)
        if last.str.contains(r"TOTAL|TOTALES", case=False, na=False).any():
            df = df.iloc[:-1]
    return df


def _normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    mapeo = {
        "ANO": "ANHO", "AÑO": "ANHO",
        "PRECIO_UNI": "PRECIO_UNID", "PRECIO UNID": "PRECIO_UNID",
        "PRECIO UNITARIO": "PRECIO_UNID",
        "COD_ARTICULO": "ID_ARTICULO", "SKU": "ID_ARTICULO",
        "ARTICULO": "NOM_ARTICULO", "DESCRIPCION": "NOM_ARTICULO",
        "LINEA": "NOM_LINEA", "COD_LINEA": "ID_LINEA",
        "CLIENTE": "NOM_CLIENTE", "COD_CLIENTE": "ID_CLIENTE",
        "RUC_CLIENTE": "DOC_CLIENTE",
        "VENDEDOR": "NOM_VENDEDOR", "COD_VENDEDOR": "ID_VENDEDOR",
        "CANT": "CANTIDAD", "QTY": "CANTIDAD", "UNIDADES": "CANTIDAD",
        "MONTO_SOLES": "SOLES", "TOTAL_SOLES": "SOLES", "MONTO": "SOLES",
    }
    df.columns = [mapeo.get(c, c) for c in df.columns]
    faltantes = [c for c in COLUMNAS_REQUERIDAS if c not in df.columns]
    if faltantes:
        raise ValueError(f"Columnas criticas faltantes: {', '.join(faltantes)}")
    return df


def _limpiar_datos(df: pd.DataFrame) -> pd.DataFrame:
    cols_str = ["ID_ARTICULO", "NRO_DOC", "ID_CLIENTE", "DOC_CLIENTE",
                "TPO_DOC", "SERIE_DOC", "ID_LINEA", "ID_VENDEDOR", "COD_SUCURSAL"]
    for col in cols_str:
        if col in df.columns:
            df[col] = (df[col].astype(str)
                       .str.replace(r"\.0$", "", regex=True)
                       .str.strip()
                       .replace("nan", ""))
    for col in ["CANTIDAD", "SOLES"]:
        if col in df.columns:
            df[col] = (pd.to_numeric(
                df[col].astype(str).str.strip(),
                errors="coerce"
            ).fillna(0))
    return df


def parse_xlsx(path: str) -> pd.DataFrame:
    df = pd.read_excel(path, dtype=str)
    df = _identificar_headers(df)
    df = _normalizar_columnas(df)
    df = _limpiar_datos(df)
    logger.info(f"Archivo parseado: {path} -> {len(df)} registros")
    return df


def parse_multiple(paths: list[str]) -> pd.DataFrame:
    dfs = []
    for p in paths:
        try:
            dfs.append(parse_xlsx(p))
        except Exception as e:
            logger.error(f"Error parseando {p}: {e}")
            raise
    return pd.concat(dfs, ignore_index=True)
