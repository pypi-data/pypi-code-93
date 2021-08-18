from unittest import TestCase
import dle_encoder


START_MARKER = dle_encoder.STX_CHAR
END_MARKER = dle_encoder.ETX_CHAR
DLE_CHAR = dle_encoder.DLE_CHAR

DLE_BYTE = bytes([DLE_CHAR])

TEST_ARRAY_0 = bytearray(5)
TEST_ARRAY_1 = bytearray([0x00, DLE_CHAR, 0x00])
TEST_ARRAY_2 = bytearray([0x00, START_MARKER, 0x00])
TEST_ARRAY_3 = bytearray([0x00, dle_encoder.CARRIAGE_RETURN, START_MARKER])
TEST_ARRAY_4 = bytearray([DLE_CHAR, END_MARKER, START_MARKER])


class TestEncoder(TestCase):
    def test_espcaped_encoding(self):
        encoder = dle_encoder.DleEncoder()
        encoded = encoder.encode(TEST_ARRAY_0)
        expected = bytearray()
        expected.append(START_MARKER)
        expected.extend(TEST_ARRAY_0)
        expected.append(END_MARKER)
        self.assertEqual(encoded, expected)

        encoded = encoder.encode(TEST_ARRAY_1)
        expected = bytearray()
        expected.append(START_MARKER)
        expected.append(0x00)
        expected.append(DLE_CHAR)
        expected.append(DLE_CHAR)
        expected.append(0x00)
        expected.append(END_MARKER)
        self.assertEqual(encoded, expected)

        encoded = encoder.encode(TEST_ARRAY_2)
        expected = bytearray()
        expected.append(START_MARKER)
        expected.append(0x00)
        expected.append(DLE_CHAR)
        expected.append(START_MARKER + 0x40)
        expected.append(0x00)
        expected.append(END_MARKER)
        self.assertEqual(encoded, expected)

        encoder.escape_cr = True
        encoded = encoder.encode(TEST_ARRAY_3, add_stx_etx=True)
        expected = bytearray()
        expected.append(START_MARKER)
        expected.append(0x00)
        expected.append(DLE_CHAR)
        expected.append(dle_encoder.CARRIAGE_RETURN + 0x40)
        expected.append(DLE_CHAR)
        expected.append(START_MARKER + 0x40)
        expected.append(END_MARKER)
        self.assertEqual(encoded, expected)

    def test_nonescaped_encoding(self):
        encoder = dle_encoder.DleEncoder(escape_stx_etx=False)
        self.generic_non_escaped_encoding(encoder=encoder, array=TEST_ARRAY_0)
        self.generic_non_escaped_encoding(encoder=encoder, array=TEST_ARRAY_1)
        self.generic_non_escaped_encoding(encoder=encoder, array=TEST_ARRAY_2)
        self.generic_non_escaped_encoding(encoder=encoder, array=TEST_ARRAY_3)
        self.generic_non_escaped_encoding(encoder=encoder, array=TEST_ARRAY_4)

    def generic_non_escaped_encoding(
            self, encoder: dle_encoder.DleEncoder, array: bytearray
    ):
        encoded = encoder.encode(array)
        expected = bytearray()
        expected.append(DLE_CHAR)
        expected.append(START_MARKER)
        expected.extend(array.replace(DLE_BYTE, DLE_BYTE*2))
        expected.append(DLE_CHAR)
        expected.append(END_MARKER)
        self.assertEqual(encoded, expected)

    def test_escaped_decoding(self):
        encoder = dle_encoder.DleEncoder()
        self.generic_decoder_test(encoder=encoder)
        self.faulty_source_for_decoing(encoder=encoder)

    def test_non_escaped_decoding(self):
        encoder = dle_encoder.DleEncoder(escape_stx_etx=False)
        self.generic_decoder_test(encoder=encoder)
        self.faulty_source_for_decoing(encoder=encoder)

    def generic_decoder_test(self, encoder: dle_encoder.DleEncoder):
        self.decode_given_array(encoder=encoder, array=TEST_ARRAY_0)
        self.decode_given_array(encoder=encoder, array=TEST_ARRAY_1)
        self.decode_given_array(encoder=encoder, array=TEST_ARRAY_2)
        encoder.escape_cr = True
        self.decode_given_array(encoder=encoder, array=TEST_ARRAY_3)

    def decode_given_array(
            self, encoder: dle_encoder.DleEncoder, array: bytearray
    ):
        encoded = encoder.encode(array)
        err_code, decoded, bytes_decoded = encoder.decode(encoded)
        self.assertEqual(err_code, dle_encoder.DleErrorCodes.OK)
        self.assertEqual(array, decoded)
        self.assertEqual(bytes_decoded, len(encoded))

    def faulty_source_for_decoing(self, encoder: dle_encoder.DleEncoder):
        # End marker invalid. Everything except end marker is decoded
        encoded = encoder.encode(TEST_ARRAY_2)
        encoded[len(encoded) - 1] = 0x00
        if not encoder.escape_stx_tx:
            # When using escaping
            encoded[len(encoded) - 2] = 0x00

        err_code, decoded, bytes_decoded = encoder.decode(encoded)
        self.assertEqual(err_code, dle_encoder.DleErrorCodes.DECODING_ERROR)
        self.assertEqual(bytes_decoded, len(encoded))

        # Start byte invalid. Nothing is decoded
        encoded = encoder.encode(TEST_ARRAY_1)
        encoded[0] = 0x00
        err_code, decoded, bytes_decoded = encoder.decode(encoded)
        self.assertEqual(err_code, dle_encoder.DleErrorCodes.DECODING_ERROR)
        self.assertEqual(bytes_decoded, 0)

        # Second value after DLE not properly escaped, so only two bytes are decoded
        if encoder.escape_stx_tx:
            encoded = encoder.encode(TEST_ARRAY_2)
            encoded[3] = 0x00
            err_code, decoded, bytes_decoded = encoder.decode(encoded)
            self.assertEqual(err_code, dle_encoder.DleErrorCodes.DECODING_ERROR)
            self.assertEqual(bytes_decoded, 2)

            encoded = encoder.encode(TEST_ARRAY_1)
            # Last byte is DLE char
            encoded[5] = DLE_CHAR
            err_code, decoded, bytes_decoded = encoder.decode(encoded)
            self.assertEqual(err_code, dle_encoder.DleErrorCodes.DECODING_ERROR)
            self.assertEqual(bytes_decoded, 5)
        # Don't escape value after DLE properly
        else:
            encoded = encoder.encode(TEST_ARRAY_1)
            encoded[4] = 0x00
            err_code, decoded, bytes_decoded = encoder.decode(encoded)
            self.assertEqual(err_code, dle_encoder.DleErrorCodes.DECODING_ERROR)
            self.assertEqual(bytes_decoded, 3)
