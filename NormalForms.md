# Formas normales

## Primer formulario normal (Repetición de grupos)

- Elimine los grupos repetidos en tablas individuales.
- Cree una tabla independiente para cada conjunto de datos relacionados.
- Identifique cada conjunto de datos relacionados con una clave principal.

## Segundo formulario normal (Tablas independientes para valores en varios registros)

- Cree tablas independientes para conjuntos de valores que se aplican a varios registros.
- Relaciona estas tablas con una clave externa.

## Tercer formulario normal (Campos no dependientes de la clave)

- Elimine los campos que no dependen de la clave.

## Cuarta forma normal (Dependencias multivalor)

Una tabla está en cuarta forma normal si no tiene dependencias de varios valores.
Las dependencias multivalor se producen cuando los valores de dos o más columnas
son independientes entre sí y solo dependen de la clave principal.

## Quinta forma normal (Rompecabezas)

Considerada comúnmente como el nivel más alto de normalización,
la quinta forma normal es un criterio centrado en la dependencia de la unión.
En la dependencia de unión, después de que una tabla se divide en tablas más pequeñas,
es posible reconstruir la tabla original reuniendo nuevamente las nuevas tablas,
todo ello sin perder ningún dato ni crear accidentalmente nuevas filas de datos.
Es comparable a un rompecabezas completado que, cuando se desarma,
puede volver a armarse en su forma original.

## Notas

La forma normal de Boyce-Codd, o BCNF, es una forma normal que se considera una
versión más estricta o más fuerte de la tercera forma normal.
BCNF requiere el uso de superclaves.
Se hace entre la 3 y la 4.
