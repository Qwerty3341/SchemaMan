# Report

## Table status

The header of every table carries one of two statuses:

- `[ PASSES ]`: no red alert in the table. Gray alerts only report missing
  information and do not change the verdict (gray does not block the pipeline
  flow, so the evaluation continues with the next normal form).
- `[ FAILS ]`: the table has a red alert.

## Example

```txt
-------------------------------------------------------------------
Table: horario          Evaluated level: 2NF          [ FAILS ]
-------------------------------------------------------------------
*  1NF        Has a primary key and no repeating groups
*  2NF        Partial dependency: creditos depends on (materia),
              which is only part of the key (materia, grupo)
-------------------------------------------------------------------
Suggestion: Table decomposition
    Table horario:
        materia (FK, references materia)
        grupo
        aula
        PK (materia, grupo)

    Table materia:
        materia (PK)
        creditos
-------------------------------------------------------------------
```
