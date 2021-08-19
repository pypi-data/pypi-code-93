from trifacta.transform_functions.function_definitions import Replace

import unittest


class TestReplace(unittest.TestCase):
    def test_valid_group_index_case(self):
        self.assertEqual(Replace(
            '(?:^((?:1[4-9]|2[0-5])\\d{2})(?: |,|\\/|-)(0?[1-9]|1[0-2])(?: |,|\\/|-)([0-2]?[0-9]|30|31)$)|(?:^.*$)',
            '$1 $2 $3', False, True).
                         exec('2048-05-06'), '2048 05 06')

        self.assertEqual(Replace(
            'hello (.*)', 'Hello $1', False, False).
                         exec('hello Tim'), 'Hello Tim')

        self.assertEqual(Replace(
            'version (\\d+).(\\d+).(\\d+)', '$2_$3_$1 VERSION', True, False).
                         exec('version 10.21.4'),
                         '21_4_10 VERSION')

        self.assertEqual(Replace(
            'version (\\d+).(\\d+).(\\d+)', 'VERSION $0_$2_$3_$1_$0', True, False).
                         exec('version 10.21.4; version 3.6.18'),
                         'VERSION version 10.21.4_21_4_10_version 10.21.4; VERSION version 3.6.18_6_18_3_version 3.6.18')

        self.assertEqual(Replace(
            "(\\d\\d):(\\d\\d):(\\d\\d);(\\d\\d):(\\d\\d):(\\d\\d);(\\w\\w):(\\w\\w):(\\w\\w);(##):(&&):(@@)",
            " $1-$2-$3, $4-$5-$6, 0x$7$8$9, $10:$11:$12", False, False).
                         exec('19:XX:00;09:12:34;21:40:00;FE:AB:CC;##:&&:@@'),
                         '19:XX:00; 09-12-34, 21-40-00, 0xFEABCC, ##:&&:@@')

        self.assertEqual(Replace(
            '(abc)(.*)(xyz)', '$3$2$1', False, False).
                         exec('cdecded19823abc-nike-xyz////*auabcubnsdkxyxyz0984324=--2'),
                         'cdecded19823xyz-nike-xyz////*auabcubnsdkxyabc0984324=--2')

        self.assertEqual(Replace(
            '(a)', 'b', False, False).
                         exec('aaaaaaaaaaaaaaaaaaaaaaaaaaa'),
                         'baaaaaaaaaaaaaaaaaaaaaaaaaa')

        self.assertEqual(Replace(
            '(a+)(bc)', '\\\\$2$1', True, False).
                         exec('aaaaaaabcabcaaaa'),
                         '\\bcaaaaaaa\\bcaaaaa')

        self.assertEqual(Replace(
            ".*?(food).*", "$1", True, False).
                         exec('message="food"'),
                         'food')

        self.assertEqual(Replace(
            "(\\s+)", "#\\\\$1", True, False).
                         exec('data is   important\t\tto \tfuture'),
                         'data#\\ is#\\   important#\\\t\tto#\\ \tfuture')

    def test_invalid_group_index_case(self):
        self.assertEqual(Replace(
            "$", "$0$$1$100$$\\$", True, False).
                         exec('AB$CDEFG'),
                         r'AB$CDEFG$$1$100$$$')

        self.assertEqual(Replace(
            '$', '\\$$$0$$1$100$$\\$', True, False).
                         exec('AB$CDEFG'),
                         'AB$CDEFG$$$$1$100$$$')

        self.assertEqual(Replace(
            ".*?(food).*", "$1 $22", True, False).
                         exec('message="food"'),
                         'food $22')

        self.assertEqual(Replace(
            ".*?(food).*", "$1 \\$1 \\$2", True, False).
                         exec('message="food"'),
                         'food $1 $2')

        self.assertEqual(Replace(
            "(a+)(bc)", "\\\\$$1", True, False).
                         exec('aaaaaaabcabcaaaa'),
                         '\\aaaaaaa\\aaaaa')

        self.assertEqual(Replace(
            "(a+)(bc)", "\\\\$2$1", True, False).
                         exec('aaaaaaabcabcaaaa'),
                         '\\bcaaaaaaa\\bcaaaaa')

        self.assertEqual(Replace(
            "\"", "\\\\\"", True, False).
                         exec('message=\"food\"'),
                         'message=\\\"food\\\"')

        self.assertEqual(Replace(
            'x', '\\\\', True, False).
                         exec('xxX'), '\\\\X')

    def test_curly_braces(self):
        self.assertEqual(Replace(
            "(a+)(bc)", "\\\\$2{}$1", True, False).
                         exec('aaaaaaabcabcaaaa'),
                         '\\bc{}aaaaaaa\\bc{}aaaaa')

        self.assertEqual(Replace(
            "(a+)(bc)", "\\\\$2{0}$1", True, False).
                         exec('aaaaaaabcabcaaaa'),
                         '\\bc{0}aaaaaaa\\bc{0}aaaaa')

        self.assertEqual(Replace(
            ".*?(food).*", "{$1} {\\$1} \\$2", True, False).
                         exec('message="food"'),
                         '{food} {$1} $2')

        if __name__ == '__main__':
            unittest.main()
