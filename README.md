# Cerberus plugin
Cerberus plugin for bottle

## installation

Via pip:
```pip install bottle-marshmallow```

Or clone:
```git clone https://github.com/kianxineki/bottle-marshmallow.git```


## example:
```python
from bottle import post, install, run
from bottle_marshmallow import MarshmallowPlugin
from marshmallow import Schema, fields


class ExampleSchema(Schema):
    name = fields.Str()


class QuerySchema(Schema):
    name = fields.Str()


@post('/marshmallow/<ex>', schemas={'body': ExampleSchema,
                                    'query_string': QuerySchema})
def test_marshmallow(ex):
    from bottle import request
    print("query_string", request.query.get('name'), type(request.query.get('name')))
    print("url", ex, type(ex))
    print("body", request.json.get('name'), type(request.json.get('name')))


install(MarshmallowPlugin())
run(host="0.0.0.0", port="9988")

```

# Schemas

## Optional keys

body: schema for request.json

url: schema for url (no query string)

query_string: schema for query strings

# Schema

marshmallow: http://marshmallow.readthedocs.io
