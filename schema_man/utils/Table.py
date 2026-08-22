class Table:
    """
    Represents a table with rows and columns.
    *args
        table_name
        number_of_columns
        columns (column_name: column_type)
        foreign keys (column_name: foreign_table.column_name)
    """

    def __init__(self, table_name: str, number_of_columns: int, primary_key: str, columns: dict[str,  str], foreign_keys: dict[str, str]):
        self.primary_key = primary_key
        self.table_name = table_name
        self.number_of_columns = number_of_columns
        self.columns = columns

    # Getters

    def get_table_name(self):
        return self.table_name

    def get_column_names(self):
        """docstring for get_column_names"""
        return self.columns

    def get_number_of_columns(self):
        return self.number_of_columns

    def get_foreign_keys(self):
        return self.foreign_keys


