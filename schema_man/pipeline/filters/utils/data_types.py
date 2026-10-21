"""Translate SQL dialect types into types used by the schema model."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from enum import StrEnum

from sqlglot import exp


DType = exp.DataType.Type


class GenericType(StrEnum):
    INTEGER = "INTEGER"
    DECIMAL = "DECIMAL"
    FLOAT = "FLOAT"
    STRING = "STRING"
    BINARY = "BINARY"
    DATE = "DATE"
    TIME = "TIME"
    DATETIME = "DATETIME"
    BOOLEAN = "BOOLEAN"
    BIT = "BIT"
    ENUM = "ENUM"
    JSON = "JSON"
    UUID = "UUID"
    SPATIAL = "SPATIAL"
    UNKNOWN = "UNKNOWN"


# SQLGlot normalizes many dialect-specific aliases to these common data types.
GENERIC_TYPES: dict[DType, GenericType] = {
    DType.TINYINT: GenericType.INTEGER,
    DType.SMALLINT: GenericType.INTEGER,
    DType.MEDIUMINT: GenericType.INTEGER,
    DType.INT: GenericType.INTEGER,
    DType.BIGINT: GenericType.INTEGER,
    # Unsigned integer variants (MariaDB)
    DType.UTINYINT: GenericType.INTEGER,
    DType.USMALLINT: GenericType.INTEGER,
    DType.UMEDIUMINT: GenericType.INTEGER,
    DType.UINT: GenericType.INTEGER,
    DType.UBIGINT: GenericType.INTEGER,
    DType.DECIMAL: GenericType.DECIMAL,
    DType.FLOAT: GenericType.FLOAT,
    DType.DOUBLE: GenericType.FLOAT,
    DType.CHAR: GenericType.STRING,
    DType.NCHAR: GenericType.STRING,
    DType.VARCHAR: GenericType.STRING,
    DType.NVARCHAR: GenericType.STRING,
    DType.TINYTEXT: GenericType.STRING,
    DType.TEXT: GenericType.STRING,
    DType.MEDIUMTEXT: GenericType.STRING,
    DType.LONGTEXT: GenericType.STRING,
    DType.BINARY: GenericType.BINARY,
    DType.VARBINARY: GenericType.BINARY,
    DType.TINYBLOB: GenericType.BINARY,
    DType.BLOB: GenericType.BINARY,
    DType.MEDIUMBLOB: GenericType.BINARY,
    DType.LONGBLOB: GenericType.BINARY,
    DType.DATE: GenericType.DATE,
    DType.TIME: GenericType.TIME,
    DType.DATETIME: GenericType.DATETIME,
    DType.TIMESTAMP: GenericType.DATETIME,
    DType.TIMESTAMPTZ: GenericType.DATETIME,
    DType.YEAR: GenericType.DATE,
    DType.BOOLEAN: GenericType.BOOLEAN,
    DType.BIT: GenericType.BIT,
    DType.ENUM: GenericType.ENUM,
    DType.SET: GenericType.ENUM,
    DType.JSON: GenericType.JSON,
    DType.UUID: GenericType.UUID,
    DType.GEOMETRY: GenericType.SPATIAL,
    DType.POINT: GenericType.SPATIAL,
    DType.LINESTRING: GenericType.SPATIAL,
    DType.POLYGON: GenericType.SPATIAL,
    DType.MULTILINESTRING: GenericType.SPATIAL,
    DType.MULTIPOLYGON: GenericType.SPATIAL,
}


def sqlite_affinity(type_name: str) -> GenericType:
    """Return SQLite's type affinity for a declared type name.

    SQLite permits arbitrary declared type names. Its affinity rules apply in
    this order, so an unknown name falls back to NUMERIC/DECIMAL affinity.
    """
    normalized = type_name.upper()
    if "INT" in normalized:
        return GenericType.INTEGER
    if any(marker in normalized for marker in ("CHAR", "CLOB", "TEXT")):
        return GenericType.STRING
    if "BLOB" in normalized:
        return GenericType.BINARY
    if any(marker in normalized for marker in ("REAL", "FLOA", "DOUB")):
        return GenericType.FLOAT
    return GenericType.DECIMAL


@dataclass(frozen=True)
class Engine:
    dialect: str
    overrides: Mapping[DType, GenericType] = field(default_factory=dict)
    fallback: Callable[[str], GenericType | None] | None = None


ENGINES: dict[str, Engine] = {
    "sqlite": Engine(dialect="sqlite", fallback=sqlite_affinity),
    # SQLGlot parses MariaDB using its MySQL dialect.
    "mysql": Engine(dialect="mysql"),
}


def generic_type_of(data_type: exp.DataType, engine: str) -> GenericType:
    """Translate a parsed SQLGlot type for the selected engine.

    An unknown engine is a caller/configuration error. A type that cannot be
    mapped for a known engine is represented as ``GenericType.UNKNOWN``.
    """
    try:
        engine_config = ENGINES[engine.lower()]
    except KeyError as error:
        supported = ", ".join(sorted(ENGINES))
        message = f"Unsupported engine {engine!r}; expected one of: {supported}"
        raise ValueError(message) from error

    generic_type = engine_config.overrides.get(data_type.this)
    if generic_type is None:
        generic_type = GENERIC_TYPES.get(data_type.this)
    if generic_type is not None:
        return generic_type

    if engine_config.fallback is not None:
        declared_type = data_type.sql(dialect=engine_config.dialect)
        fallback_type = engine_config.fallback(declared_type)
        if fallback_type is not None:
            return fallback_type

    return GenericType.UNKNOWN
