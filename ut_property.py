from pydantic.dataclasses import dataclass
from typing import Any
import enums

@dataclass
class Property:
    owner: Any
    name: str
    array_index: int
    property_type: int
    value: Any
    type_name: str
    is_initialized: bool
