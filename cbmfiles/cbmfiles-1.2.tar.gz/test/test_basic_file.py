import unittest
import io

from cbm_files.basic_file import BASICFile


class TestBASICFile(unittest.TestCase):
    def test_read(self):
        mock_file = io.BytesIO(b'\x01\x12'
                               b'\x0d\x12\x0a\x00C\xb240703\x00'
                               b'\x14\x12d\x00\x87A\x00'
                               b'\x21\x12n\x00\x8bA\xb30\x89200\x00'
                               b'\x2a\x12x\x00\x97C,A\x00'
                               b'\x00\x00')
        prog = BASICFile(mock_file)
        self.assertEqual(list(prog.lines.keys()), [10, 100, 110, 120])

    def test_read_addr(self):
        mock_file = io.BytesIO(b'\x0d\x12\x0a\x00C\xb240703\x00'
                               b'\x14\x12d\x00\x87A\x00'
                               b'\x21\x12n\x00\x8bA\xb30\x89200\x00'
                               b'\x2a\x12x\x00\x97C,A\x00'
                               b'\x00\x00')
        prog = BASICFile(mock_file, start_addr=0x1201)
        self.assertEqual(list(prog.lines.keys()), [10, 100, 110, 120])

    def test_from_text(self):
        mock_file = io.StringIO("10 REM LINE 1\n30STOP\n")
        prog = BASICFile(None)
        prog.from_text(mock_file)
        self.assertEqual(list(prog.lines.keys()), [10, 30])
        self.assertEqual(prog.lines[30], b'\x90')

    def test_to_binary(self):
        prog = BASICFile(None)
        prog.add_line(10, 'C=40703')
        prog.add_line(100, 'READA')
        prog.add_line(110, 'IFA<0GOTO200')
        prog.add_line(120, 'POKEC,A')
        data = list(prog.to_binary(start_addr=0x1201, prepend_addr=False))
        self.assertEqual(data, [b'\x0d\x12\x0a\x00C\xb240703\x00',
                                b'\x14\x12d\x00\x87A\x00',
                                b'\x21\x12n\x00\x8bA\xb30\x89200\x00',
                                b'\x2a\x12x\x00\x97C,A\x00',
                                b'\x00\x00'])
        data = list(prog.to_binary(start_addr=0x1201))
        self.assertEqual(data[0], b'\x01\x12')

    def test_to_text(self):
        prog = BASICFile(None)
        prog.add_encoded_line(10, b'C\xb240703')
        prog.add_encoded_line(100, b'\x87A')
        prog.add_encoded_line(110, b'\x8bA\xb30\x89200')
        prog.add_encoded_line(120, b'\x97C,A')
        text = list(prog.to_text())
        self.assertEqual(text, ['10 C=40703', '100 READA', '110 IFA<0GOTO200', '120 POKEC,A'])

    def test_merge(self):
        prog1 = BASICFile(None)
        prog1.add_encoded_line(10, b'\x01')
        prog1.add_encoded_line(20, b'\x01')
        prog1.add_encoded_line(30, b'\x01')
        prog2 = BASICFile(None)
        prog2.add_encoded_line(15, b'\x02')
        prog2.add_encoded_line(20, b'\x02')
        prog2.add_encoded_line(25, b'\x02')
        prog1.merge(prog2)
        self.assertEqual(list(prog1.lines.keys()), [10, 15, 20, 25, 30])
        self.assertEqual(prog1.lines[20], b'\x02')

    def test_add_encoded_line(self):
        prog = BASICFile(None)
        prog.add_encoded_line(10, b'\x00')
        prog.add_encoded_line(100, b'\x00')
        prog.add_encoded_line(50, b'\x00')
        self.assertEqual(list(prog.lines.keys()), [10, 50, 100])

    def test_add_line(self):
        prog = BASICFile(None)
        prog.add_line(50, 'PRINT')
        self.assertEqual(prog.lines[50], b'\x99')

    def test_delete_line(self):
        prog = BASICFile(None)
        prog.add_encoded_line(10, b'\x00')
        prog.add_encoded_line(50, b'\x00')
        prog.add_encoded_line(100, b'\x00')
        prog.delete_line(50)
        self.assertEqual(list(prog.lines.keys()), [10, 100])

    def test_escape_set_name(self):
        self.assertEqual(BASICFile.escape_set_name('petscii-vic20en-uc'), 'escape-vic20')
        self.assertEqual(BASICFile.escape_set_name('dummy'), 'escape-c64')

    def test_tokenize(self):
        prog = BASICFile(None)
        self.assertEqual(prog.tokenize('PRINT"{lgrn}"'), b'\x99"\x99"')

    def test_expand(self):
        prog = BASICFile(None, encoding='utf8')
        self.assertEqual(prog.expand(b'\x99"\x09"', False), 'PRINT"\t"')

    def test_expand_escape(self):
        prog = BASICFile(None)
        self.assertEqual(prog.expand(b'\x99"\x09"', True), 'PRINT"{ensh}"')
