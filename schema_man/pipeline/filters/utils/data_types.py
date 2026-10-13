"""
# Data types in engines
"""

integers = {
    'sqlite': [
        'INTEGER'
    ],
    'mariadb': [
        'TINYINT', 'SMALLINT', 'MEDIUMINT', 'INT', 'BIGINT'
    ]
}

terminating_decimals = {
    'sqlite': [
        'NUMERIC'
    ],
    'mariadb': [
        'DECIMAL', 'NUMERIC'
    ]
}

floating_points = {
    'sqlite': [
        'REAL'
    ],
    'mariadb': [
        'FLOAT', 'DOUBLE'
    ]
}

strings = {
    'sqlite': [
        'TEXT'
    ],
    'mariadb': [
        'CHAR', 'VARCHAR',
        'TINYTEXT', 'TEXT', 'MEDIUMTEXT', 'LONGTEXT'
    ]
}

binaries = {
    'sqlite': [
        'BLOB'
    ],
    'mariadb': [
        'BINARY', 'VARBINARY',
        'TINYBLOB', 'BLOB', 'MEDIUMBLOB', 'LONGBLOB'
    ]
}

dates_and_times = {
    # SQLite has no native type: stored as TEXT (ISO 8601),
    # REAL (Julian day) or INTEGER (Unix time)
    'sqlite': [
        'TEXT', 'REAL', 'INTEGER'
    ],
    'mariadb': [
        'DATE', 'TIME', 'DATETIME', 'TIMESTAMP', 'YEAR'
    ]
}

booleans = {
    # SQLite stores booleans as INTEGER 0 / 1
    'sqlite': [
        'INTEGER'
    ],
    'mariadb': [
        'BOOLEAN', 'BOOL'  # aliases of TINYINT(1)
    ]
}

bits = {
    'sqlite': [
        'INTEGER', 'BLOB'
    ],
    'mariadb': [
        'BIT'
    ]
}

enumerations = {
    # SQLite: TEXT + CHECK (col IN (...))
    'sqlite': [
        'TEXT'
    ],
    'mariadb': [
        'ENUM', 'SET'
    ]
}

json = {
    # SQLite: TEXT with json_*() functions, JSONB stored as BLOB (3.45+)
    'sqlite': [
        'TEXT', 'BLOB'
    ],
    'mariadb': [
        'JSON'  # alias of LONGTEXT with JSON_VALID check
    ]
}

uuids = {
    'sqlite': [
        'TEXT', 'BLOB'
    ],
    'mariadb': [
        'UUID'  # MariaDB 10.7+
    ]
}

ip_addresses = {
    'sqlite': [
        'TEXT', 'BLOB'
    ],
    'mariadb': [
        'INET4', 'INET6'  # MariaDB 10.10+
    ]
}

spatial = {
    # SQLite needs the SpatiaLite extension
    'sqlite': [],
    'mariadb': [
        'GEOMETRY', 'POINT', 'LINESTRING', 'POLYGON',
        'MULTIPOINT', 'MULTILINESTRING', 'MULTIPOLYGON',
        'GEOMETRYCOLLECTION'
    ]
}


data_types = {
    'integers': integers,
    'terminating_decimals': terminating_decimals,
    'floating_points': floating_points,
    'strings': strings,
    'binaries': binaries,
    'dates_and_times': dates_and_times,
    'booleans': booleans,
    'bits': bits,
    'enumerations': enumerations,
    'json': json,
    'uuids': uuids,
    'ip_addresses': ip_addresses,
    'spatial': spatial,
}

engines = [
    'sqlite', 'mariadb'
]


def category_of(type_name, engine):
    """Return the category a type belongs to in a given engine, or None."""
    type_name = type_name.upper()
    for category, engines in data_types.items():
        if type_name in engines[engine]:
            return category
    return None
