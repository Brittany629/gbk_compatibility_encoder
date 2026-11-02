"""GBK compatibility encoder.

Re-exports the public API so that ``from gbk_compatibility_encoder import ...``
works without reaching into the submodule.
"""

from .core import (
    PUA_TABLE,
    EncodedChar,
    encode_char,
    encode_string,
    is_pua_extension,
)

__all__ = [
    "PUA_TABLE",
    "EncodedChar",
    "encode_char",
    "encode_string",
    "is_pua_extension",
]
