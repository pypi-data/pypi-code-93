"""DLE ASCII Encoder Implementation

This encoder provides a simple ASCII transport layer for serial data.
A give data stream is encoded by adding a STX char at the beginning and an ETX char at the end.
All STX and ETX occurrences in the packet are encoded as well so the receiver can simply look
for STX and ETX occurrences to identify packets.
You can find a C++ implementation here:
https://egit.irs.uni-stuttgart.de/fsfw/fsfw/src/branch/master/globalfunctions/DleEncoder.cpp
"""
import enum
from typing import Tuple, Union
from io import RawIOBase, BytesIO

STX_CHAR = 0x02
ETX_CHAR = 0x03
CARRIAGE_RETURN = 0x0D
DLE_CHAR = 0x10

ESCAPE_JUMP = 0x40

ESCAPED_STX = STX_CHAR + ESCAPE_JUMP
ESCAPED_ETX = ETX_CHAR + ESCAPE_JUMP
ESCAPED_CR = CARRIAGE_RETURN + ESCAPE_JUMP

DLE_BYTE = bytes([DLE_CHAR])
STX_BYTE = bytes([STX_CHAR])
ETX_BYTE = bytes([ETX_CHAR])


class DleErrorCodes(enum.Enum):
    OK = 0,
    END_REACHED = 1,
    DECODING_ERROR = 2


class DleEncoder:
    def __init__(self, escape_stx_etx: bool = True, escape_cr: bool = False):
        """Create an encoder instance.

        :param escape_stx_etx: Configure the encoder to run in the escaped mode. Currently, this
            is the only supported mode
        :param escape_cr: If running is escaped mode, this flag can be used to escape CR occurrences
            as well
        """
        self.escape_stx_tx = escape_stx_etx
        self.escape_cr = escape_cr

    def encode(
            self, source_packet: bytearray, add_stx_etx: bool = True
    ) -> bytearray:
        """Encodes a given stream with DLE encoding.

        :return: Encoded bytearray.
        """
        if self.escape_stx_tx:
            return self.__encode_escaped(source_packet=source_packet, add_stx_etx=add_stx_etx)
        else:
            encoded_packet = bytearray()
            encoded_packet.append(DLE_CHAR)
            encoded_packet.append(STX_CHAR)
            encoded_packet.extend(source_packet.replace(DLE_BYTE, DLE_BYTE * 2))
            encoded_packet.append(DLE_CHAR)
            encoded_packet.append(ETX_CHAR)
            return encoded_packet

    def __encode_escaped(self, source_packet: bytearray, add_stx_etx: bool = True) -> bytearray:
        dest_stream = bytearray()
        source_len = len(source_packet)
        source_index = 0
        if add_stx_etx:
            dest_stream.append(STX_CHAR)

        while source_index < source_len:
            next_byte = source_packet[source_index]
            # STX, ETX and CR characters in the stream need to be escaped with DLE
            if (next_byte == STX_CHAR or next_byte == ETX_CHAR) or \
                    (self.escape_cr and next_byte == CARRIAGE_RETURN):
                dest_stream.append(DLE_CHAR)
                """Escaped byte will be actual byte + 0x40. This prevents
                STX and ETX characters from appearing
                in the encoded data stream at all, so when polling an
                encoded stream, the transmission can be stopped at ETX.
                0x40 was chosen at random with special requirements:
                - Prevent going from one control char to another
                - Prevent overflow for common characters
                """
                dest_stream.append(next_byte + ESCAPE_JUMP)
            elif next_byte == DLE_CHAR:
                dest_stream.append(DLE_CHAR)
                dest_stream.append(DLE_CHAR)
            else:
                dest_stream.append(next_byte)
            source_index += 1
        if add_stx_etx:
            dest_stream.append(ETX_CHAR)
        return dest_stream

    def decode(
            self, source_packet: bytearray
    ) -> Tuple[DleErrorCodes, bytearray, int]:
        """Decodes a given DLE encoded data stream. This call only returns the first packet found.

        It might be necessary to call this function multiple times, depending on the third
        return value.

        :return:
            - DleErrorCode - If decoding has failed, this will not be DleErrorCodes.OK. The function
              will still return the read length and the decoded bytearray, if any decoding was
              performed
            - Decoded bytearray - Decoded packet
            - Read length - Read length in the encoded stream. If this is smaller than the length of
              the passed bytearray, the decoding function should be called again.
        """
        stream = BytesIO(source_packet)
        retval, decoded_packet, decoded_bytes = self.read(file=stream)
        if retval == DleErrorCodes.END_REACHED:
            # Convert this return value. If the user supplies a packet, the format is expected
            # to be valid
            return DleErrorCodes.DECODING_ERROR, decoded_packet, decoded_bytes
        return retval, decoded_packet, decoded_bytes

    def read(
            self, file: Union[RawIOBase, BytesIO]
    ) -> Tuple[DleErrorCodes, bytearray, int]:
        """Read DLE encoded packets from a given file or byte stream

        :param file:
        :return:
            - DleErrorCode - If decoding has failed, this will not be DleErrorCodes.OK. The function
              will still return the read length and the decoded bytearray, if any decoding was
              performed. DleErrorCodes.END_REACHED if all bytes have been read but not end
              marker was detected
            - Decoded bytearray - Decoded packet
            - Read length - Read length in the encoded stream. If this is smaller than the length of
              the passed bytearray, the decoding function should be called again.
        """
        if self.escape_stx_tx:
            return self.__read_escaped(file=file)
        else:
            return self.__read_non_escaped(file=file)

    def __read_escaped(
            self, file: Union[RawIOBase, BytesIO]
    ) -> Tuple[DleErrorCodes, bytearray, int]:
        encoded_index = 0
        dest_stream = bytearray()
        byte = file.read(1)
        if len(byte) == 0 or byte[0] != STX_CHAR:
            return DleErrorCodes.DECODING_ERROR, dest_stream, encoded_index

        encoded_index += 1
        while True:
            byte = file.read(1)
            if len(byte) == 0:
                return DleErrorCodes.END_REACHED, dest_stream, encoded_index
            else:
                byte = byte[0]
            if byte == DLE_CHAR:
                next_byte = file.read(1)
                if len(next_byte) == 0:
                    return DleErrorCodes.DECODING_ERROR, dest_stream, encoded_index
                else:
                    next_byte = next_byte[0]
                if (next_byte == ESCAPED_STX or next_byte == ESCAPED_ETX) or \
                        (self.escape_cr and next_byte == ESCAPED_CR):
                    dest_stream.append(next_byte - ESCAPE_JUMP)
                    encoded_index += 2
                elif next_byte == DLE_CHAR:
                    dest_stream += DLE_BYTE
                    encoded_index += 2
                else:
                    return DleErrorCodes.DECODING_ERROR, dest_stream, encoded_index
            elif byte == ETX_CHAR:
                encoded_index += 1
                return DleErrorCodes.OK, dest_stream, encoded_index
            else:
                dest_stream.append(byte)
                encoded_index += 1

    @staticmethod
    def __read_non_escaped(
            file: Union[RawIOBase, BytesIO]
    ) -> Tuple[DleErrorCodes, bytearray, int]:
        encoded_index = 0
        dest_stream = bytearray()
        header = file.read(2)
        if len(header) < 2 or header[0] != DLE_CHAR or header[1] != STX_CHAR:
            return DleErrorCodes.DECODING_ERROR, dest_stream, encoded_index
        encoded_index += 2
        buffer = bytearray()
        while True:
            buffer += file.read(2 - len(buffer))
            if len(buffer) != 2:
                encoded_index += len(buffer)
                return DleErrorCodes.DECODING_ERROR, dest_stream, encoded_index
            if buffer.startswith(DLE_BYTE):
                if buffer[1] == DLE_CHAR:
                    dest_stream.append(buffer[1])
                    encoded_index += 2
                    buffer.clear()
                elif buffer[1] == ETX_CHAR:
                    encoded_index += 2
                    return DleErrorCodes.OK, dest_stream, encoded_index
                else:
                    return DleErrorCodes.DECODING_ERROR, dest_stream, encoded_index
            else:
                encoded_index += 1
                dest_stream.append(buffer.pop(0))
