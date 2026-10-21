# Filters

## ParseSqlFilter

This filter uses sqlglot to check if the user send us a valid SQL schema.

If the schema is empty the apply method will raise and ValueError exception

Then will made and try/except to verify if it is possible to use the "parse_one" method (make and AST) if the parse_one returns a ParseError (error from sqlglot) the filter raises a ValueError

If the "parse_one" was made successfully the filter return the context

## ModelSchemaFilter
This filter have multiple methods.

The apply method just uses a self.model_schema method to pass the AST to a
generic syntax
