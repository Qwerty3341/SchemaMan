PRAGMA foreign_keys = ON;

-- Tabla 1: diseño correcto (esperado: Verde hasta BCNF)
CREATE TABLE alumno (
    alumno_id   INTEGER PRIMARY KEY,
    matricula   TEXT    NOT NULL UNIQUE,
    nombre      TEXT    NOT NULL,
    correo      TEXT    NOT NULL UNIQUE
    -- FD: (alumno_id) -> (matricula, nombre, correo)
    -- FD: (matricula) -> (alumno_id, nombre, correo)
);

-- Tabla 2: grupo repetitivo + dependencia transitiva
-- (esperado: 1FN Amarillo por telefono1..3, 3FN Rojo por depto_id -> nombre_depto)
CREATE TABLE profesor (
    profesor_id   INTEGER PRIMARY KEY,
    nombre        TEXT NOT NULL,
    telefono1     TEXT,
    telefono2     TEXT,
    telefono3     TEXT,
    depto_id      INTEGER NOT NULL,
    nombre_depto  TEXT    NOT NULL
    -- FD: (profesor_id) -> (nombre, depto_id)
    -- FD: (depto_id) -> (nombre_depto)
);

-- Tabla 3: llave compuesta con dependencias parciales
-- (esperado: 2FN Rojo, porque nombre_curso y creditos dependen solo de curso_id)
CREATE TABLE inscripcion (
    alumno_id     INTEGER NOT NULL,
    curso_id      INTEGER NOT NULL,
    nombre_curso  TEXT    NOT NULL,
    creditos      INTEGER NOT NULL,
    calificacion  REAL,
    PRIMARY KEY (alumno_id, curso_id),
    FOREIGN KEY (alumno_id) REFERENCES alumno(alumno_id)
    -- FD: (alumno_id, curso_id) -> (calificacion)
    -- FD: (curso_id) -> (nombre_curso, creditos)
);

-- Tabla 4: dos hechos independientes en una sola tabla
-- (esperado: BCNF Verde y 4FN Rojo por la MVD)
CREATE TABLE curso_profesor_libro (
    curso_id     INTEGER NOT NULL,
    profesor_id  INTEGER NOT NULL,
    libro        TEXT    NOT NULL,
    PRIMARY KEY (curso_id, profesor_id, libro),
    FOREIGN KEY (profesor_id) REFERENCES profesor(profesor_id)
    -- MVD: (curso_id) ->> (profesor_id)
);
