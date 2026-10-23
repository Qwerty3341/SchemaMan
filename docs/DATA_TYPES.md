# Data Types

## GenericType enum

Defines the generic types used by the schema model.
`UNKNOWN` is used when a type cannot be mapped.

## GENERIC_TYPES dict

Maps sqlglot types to the GenericType enum.
Shared by all engines.

## Engine class

Defines how a dialect is translated:

- `dialect`: the sqlglot dialect name
- `overrides`: engine-specific mappings (optional)
- `fallback`: function for types not in the map (optional)

## ENGINES dict

The supported engines:

- `sqlite`: uses `sqlite_affinity` as fallback
- `mysql`: also used for MariaDB

## Functions

### sqlite_affinity

Handles SQLite's arbitrary type names by applying
SQLite's affinity rules in order. Unknown names fall
back to `DECIMAL`.

### generic_type_of

Translates a sqlglot type for the selected engine.
Resolution order: engine overrides, then GENERIC_TYPES,
then the engine fallback. Unknown engine raises
`ValueError`; unmapped type returns `UNKNOWN`.
