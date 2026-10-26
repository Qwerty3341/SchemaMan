# Report

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
