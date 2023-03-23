import orjson


def orjson_dumps(v, *, default):
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(v, default=default).decode()


def orjson_loads(*args, **kwargs):
    return orjson.loads(*args, **kwargs)
