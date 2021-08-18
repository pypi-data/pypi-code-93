from unittest import TestCase
import dle_encoder


START_MARKER = dle_encoder.STX_CHAR
END_MARKER = dle_encoder.ETX_CHAR
DLE_CHAR = dle_encoder.DLE_CHAR
TEST_ARRAY_0 = bytearray(5)
TEST_ARRAY_1 = bytearray([0x00, DLE_CHAR, 0x00])
TEST_ARRAY_2 = bytearray([0x00, START_MARKER, 0x00])
TEST_ARRAY_3 = bytearray([0x00, dle_encoder.CARRIAGE_RETURN, START_MARKER])


class TestEncoder(TestCase):
    def test_encoding(self):
        encoded = dle_encoder.encode_dle(TEST_ARRAY_0)
        expected = bytearray()
        expected.append(START_MARKER)
        expected.extend(TEST_ARRAY_0)
        expected.append(END_MARKER)
        self.assertEqual(encoded, expected)

        encoded = dle_encoder.encode_dle(TEST_ARRAY_1)
        expected = bytearray()
        expected.append(START_MARKER)
        expected.append(0x00)
        expected.append(DLE_CHAR)
        expected.append(DLE_CHAR)
        expected.append(0x00)
        expected.append(END_MARKER)
        self.assertEqual(encoded, expected)

        encoded = dle_encoder.encode_dle(TEST_ARRAY_2)
        expected = bytearray()
        expected.append(START_MARKER)
        expected.append(0x00)
        expected.append(DLE_CHAR)
        expected.append(START_MARKER + 0x40)
        expected.append(0x00)
        expected.append(END_MARKER)
        self.assertEqual(encoded, expected)

        encoded = dle_encoder.encode_dle(TEST_ARRAY_3, add_stx_etx=True, encode_cr=True)
        expected = bytearray()
        expected.append(START_MARKER)
        expected.append(0x00)
        expected.append(DLE_CHAR)
        expected.append(dle_encoder.CARRIAGE_RETURN + 0x40)
        expected.append(DLE_CHAR)
        expected.append(START_MARKER + 0x40)
        expected.append(END_MARKER)
        self.assertEqual(encoded, expected)

    def test_decoding(self):
        self.generic_decoding_test(array=TEST_ARRAY_0)
        self.generic_decoding_test(array=TEST_ARRAY_1)
        self.generic_decoding_test(array=TEST_ARRAY_2)
        self.generic_decoding_test(array=TEST_ARRAY_3, decode_cr=True)

        # End marker invalid. Everything except end marker is decoded
        encoded = dle_encoder.encode_dle(TEST_ARRAY_2)
        encoded[len(encoded) - 1] = 0x00
        err_code, decoded, bytes_decoded = dle_encoder.decode_dle(encoded)
        self.assertEqual(err_code, dle_encoder.DleErrorCodes.DECODING_ERROR)
        self.assertEqual(bytes_decoded, len(encoded) - 1)

        # Start byte invalid. Nothing is decoded
        encoded = dle_encoder.encode_dle(TEST_ARRAY_1)
        encoded[0] = 0x00
        err_code, decoded, bytes_decoded = dle_encoder.decode_dle(encoded)
        self.assertEqual(err_code, dle_encoder.DleErrorCodes.DECODING_ERROR)
        self.assertEqual(bytes_decoded, 0)

        # Second value after DLE not properly escaped, so only two bytes are decoded
        encoded = dle_encoder.encode_dle(TEST_ARRAY_2)
        encoded[3] = 0x00
        err_code, decoded, bytes_decoded = dle_encoder.decode_dle(encoded)
        self.assertEqual(err_code, dle_encoder.DleErrorCodes.DECODING_ERROR)
        self.assertEqual(bytes_decoded, 2)

    def generic_decoding_test(self, array: bytearray, decode_cr: bool = False):
        encoded = dle_encoder.encode_dle(array)
        err_code, decoded, bytes_decoded = dle_encoder.decode_dle(encoded, decode_cr=decode_cr)
        self.assertEqual(err_code, dle_encoder.DleErrorCodes.OK)
        self.assertEqual(array, decoded)
        self.assertEqual(bytes_decoded, len(encoded))
