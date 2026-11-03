# gbk_compatibility_encoder

Encodes Unicode text to GBK bytes, including the Private Use Area code points
that Microsoft's CP936 extension maps but the standard GBK codec rejects.

```python
from gbk_compatibility_encoder import encode_char, encode_string

# The standard codec cannot encode U+E000, but CP936 maps it to 0xAA 0xA1.
encode_char(0xE000)
# EncodedChar(data=b'\xaa\xa1', is_pua=True)

encode_string("A\ue000B")
# b'A\xaa\xa1B'
```

## Why this exists

Windows decodes a handful of GBK byte pairs into the Private Use Area rather
than into real Unicode characters. When that text is later moved to a
non-Windows system, Python's `gbk` codec refuses to encode it back, because
those PUA code points are not part of the standard GBK mapping. The usual
workarounds are to install a third-party codec or to register a global codec
search function; both change process-wide state and are awkward to test.

This library keeps the mapping in a plain dict and exposes it through two
functions. The trade-off is that the table is a fixed snapshot of the CP936
extension rather than a general-purpose codec: it covers the U+E000..U+E4C5
range that Windows actually emits, and nothing outside it. If you need a
codec that participates in `str.encode("gbk")`, this is not it.

## API

- `PUA_TABLE`: `dict[int, bytes]` mapping PUA code points to their GBK bytes.
- `EncodedChar`: a `NamedTuple` with fields `data: bytes` and `is_pua: bool`.
- `encode_char(code_point: int) -> EncodedChar | None`: encodes one code point,
  returning `None` when neither the standard codec nor the extension table can
  represent it. Raises `TypeError` for non-integer input.
- `encode_string(text: str) -> bytes`: encodes a whole string. The standard
  codec is tried first; only on failure does it fall back to per-character
  encoding. Raises `UnicodeEncodeError` (with the offending index) for
  characters that cannot be represented.
- `is_pua_extension(code_point: int) -> bool`: whether the code point is in
  `PUA_TABLE`.

## The awkward edge

The standard codec is tried on the whole string before any per-character
fallback. That means a string containing only representable characters takes
one codec call, while a string with a single PUA character takes a slower path
for every character. It also means `encode_string` raises `UnicodeEncodeError`
for unmappable characters rather than silently dropping them, so callers who
want lossy behaviour must catch the exception themselves.
