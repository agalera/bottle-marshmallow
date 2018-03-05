import functools

import bottle


JSON_CONTENT_TYPE = 'application/json'


def _wrapper(schemas, output, callback, *args, **kwargs):
    shortcut = {
        'url': kwargs,
        'body': bottle.request.json or {},
        'query_string': {
            k: v for k, v in bottle.request.query.items()
        }
    }

    for k in schemas:
        tmp = schemas[k].load(shortcut[k])
        if tmp.errors:
            raise bottle.HTTPError(
                {'errors': tmp['errors'], 'validation': k}
            )

        # update original reference
        shortcut[k] = shortcut[k].update(tmp.data)

    if not output:
        return callback(*args, **kwargs)
    return output.load(callback(*args, **kwargs))


def serializers(schemas):
    def decorator(func):
        schemas = {}
        output = None

        for key in schemas:
            # create instance
            if key == 'output':
                output = schemas[key]()
            else:
                schemas[key] = schemas[key]()

        @functools.wraps(func)
        def wrapper(*a, **kw):
                return _wrapper(schemas, output, func, *a, **kw)
        return wrapper
    return decorator


class MarshmallowPlugin(object):
    name = 'MarshmallowPlugin'
    api = 2
    keyword = 'schemas'

    def apply(self, callback, route):
        schemas = {}
        output = None
        for namespace in route.config:
            if self.keyword == namespace[:len(self.keyword)]:
                old = schemas
                final = namespace.split('.')[-1]
                for key in namespace.split('.')[1:]:
                    if key not in old:
                        if final == key:
                            # create instance
                            if key == 'output':
                                output = route.config[namespace]()
                            else:
                                old[key] = route.config[namespace]()
                            continue
                        old[key] = {}
                    old = old[key]

        if not schemas:
            return callback

        @functools.wraps(callback)
        def wrapper(*a, **kw):
            return _wrapper(schemas, output, callback, *a, **kw)
        return wrapper
