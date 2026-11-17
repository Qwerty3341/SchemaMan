# Backend summary

All the architecture are in ../schema_man/pipeline
Is used in the function `get_report():` from the API.py

## get_report

Method: Get
The function makes a PipeLineContext with:

```python
# The atributes are from the frontend
context = PipeLineContext(
  sql=sql,
  dialect=dialect,
  target_normal_form=normalization_level,
)
```

Then make a pipe

```python
pipeline = Pipe(
    filters=[
        ParseSqlFilter(),
        ModelSchemaFilter(),
        NFDetectionFilter(),
        ReportFilter(),
    ]
)
```

The Pipe class receive all the filters

Finally have the try/except and the return statement

```python
try:
    context = pipeline.run(context)
except ValueError as pipeline_error:
    return jsonify(valid=False, error=str(pipeline_error)), 400

return jsonify(valid=True, report=context.report)
```
