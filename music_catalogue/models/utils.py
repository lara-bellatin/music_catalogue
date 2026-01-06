def _maybe(model_cls, data):
    if not data:
        return None
    return model_cls.from_dict(data)

def _list_maybe(model_cls, data):
    if not data:
        return []
    return [model_cls.from_dict(item) for item in data]