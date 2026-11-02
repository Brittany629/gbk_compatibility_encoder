import unittest

from gbk_compatibility_encoder import (
    PUA_TABLE,
    EncodedChar,
    encode_char,
    encode_string,
    is_pua_extension,
)


class TestPuaTable(unittest.TestCase):
    def test_table_is_not_empty(self):
        self.assertGreater(len(PUA_TABLE), 0)

    def test_every_value_is_two_bytes(self):
        for cp, data in PUA_TABLE.items():
            self.assertEqual(len(data), 2, msg=hex(cp))
            self.assertGreaterEqual(data[0], 0xA1)
            self.assertLessEqual(data[0], 0xFE)

    def test_keys_are_in_pua_range(self):
        for cp in PUA_TABLE:
            self.assertTrue(0xE000 <= cp <= 0xF8FF, msg=hex(cp))

    def test_lookup_helper_matches_table(self):
        self.assertTrue(is_pua_extension(0xE000))
        self.assertFalse(is_pua_extension(0x4E00))


class TestEncodeChar(unittest.TestCase):
    def test_ascii_uses_standard_codec(self):
        result = encode_char(ord("A"))
        self.assertIsInstance(result, EncodedChar)
        self.assertEqual(result.data, b"A")
        self.assertFalse(result.is_pua)

    def test_common_han_character(self):
        result = encode_char(ord("\u4e00"))
        self.assertEqual(result.data, b"\xd2\xbb")
        self.assertFalse(result.is_pua)

    def test_pua_character_uses_extension(self):
        result = encode_char(0xE000)
        self.assertEqual(result.data, b"\xaa\xa1")
        self.assertTrue(result.is_pua)

    def test_pua_character_that_standard_codec_rejects(self):
        # Python's gbk codec refuses U+E000; the extension table must supply it.
        with self.assertRaises(UnicodeEncodeError):
            "\ue000".encode("gbk")
        result = encode_char(0xE000)
        self.assertEqual(result.data, b"\xaa\xa1")

    def test_unmappable_returns_none(self):
        # U+1F600 has no GBK representation and is outside the PUA table.
        self.assertIsNone(encode_char(0x1F600))

    def test_surrogate_returns_none(self):
        self.assertIsNone(encode_char(0xD800))
        self.assertIsNone(encode_char(0xDFFF))

    def test_out_of_range_returns_none(self):
        self.assertIsNone(encode_char(-1))
        self.assertIsNone(encode_char(0x110000))

    def test_non_int_raises_type_error(self):
        with self.assertRaises(TypeError):
            encode_char("A")


class TestEncodeString(unittest.TestCase):
    def test_plain_ascii(self):
        self.assertEqual(encode_string("hello"), b"hello")

    def test_plain_han(self):
        self.assertEqual(encode_string("\u4e00"), b"\xd2\xbb")

    def test_mixed_text_with_pua(self):
        text = "A\ue000B"
        self.assertEqual(encode_string(text), b"A\xaa\xa1B")

    def test_multiple_pua_characters(self):
        text = "\ue000\ue001\ue002"
        self.assertEqual(encode_string(text), b"\xaa\xa1\xaa\xa2\xaa\xa3")

    def test_empty_string(self):
        self.assertEqual(encode_string(""), b"")

    def test_unmappable_raises_with_position(self):
        with self.assertRaises(UnicodeEncodeError) as ctx:
            encode_string("A\U0001F600B")
        self.assertEqual(ctx.exception.start, 1)
        self.assertEqual(ctx.exception.end, 2)

    def test_non_str_raises_type_error(self):
        with self.assertRaises(TypeError):
            encode_string(b"hello")

    def test_round_trip_through_gbk_for_standard_text(self):
        text = "\u4e2d\u6587"
        self.assertEqual(encode_string(text).decode("gbk"), text)


if __name__ == "__main__":
    unittest.main()
