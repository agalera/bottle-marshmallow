import functools

import bottle


JSON_CONTENT_TYPE = 'application/json'


class MarshmallowPlugin(object):
    name = 'MarshmallowPlugin'
    api = 2
    keyword = 'schemas'

    def apply(self, callback, route):
        schemas = {}
        for namespace in route.config:
            if self.keyword == namespace[:len(self.keyword)]:
                old = schemas
                final = namespace.split('.')[-1]
                for key in namespace.split('.')[1:]:
                    if key not in old:
                        if final == key:
                            # create instance
                            old[key] = route.config[namespace]()
                            continue
                        old[key] = {}
                    old = old[key]

        if not schemas:
            return callback

        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            shortcut = {
                'url': kwargs,
                'body': bottle.request.json or {},
                'query_string': {
                    k: v for k, v in bottle.request.query.items()
                }
            }

            for k in schemas:
                tmp = schemas[k].dump(shortcut[k])
                if tmp.errors:
                    raise bottle.HTTPError(
                        {'errors': tmp['errors'], 'validation': k}
                    )

                # update original reference
                shortcut[k] = shortcut[k].update(tmp.data)
            return callback(*args, **kwargs)

        return wrapper
