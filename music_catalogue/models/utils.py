from typing import Any, Dict, List

from pydantic import BaseModel


def _parse(model_cls: BaseModel, data: Dict) -> Any:
    if not data:
        return None
    return model_cls.from_dict(data)


def _parse_list(model_cls: BaseModel, data: Dict) -> List[Any]:
    if not data:
        return []
    return [_parse(model_cls, item) for item in data if _parse(model_cls, item) is not None]
