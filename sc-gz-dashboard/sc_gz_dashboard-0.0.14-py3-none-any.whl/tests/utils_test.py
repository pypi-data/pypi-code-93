#  The MIT License (MIT)
#
#  Copyright (c) 2021. Scott Lau
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import unittest

from sc_gz_dashboard.utils import MonthUtils


class UtilsTestCase(unittest.TestCase):
    def test_calculate_month(self):
        (yearly, seasonal, monthly) = MonthUtils.calculate_month(2021, 0)
        self.assertIsNone(yearly[0])
        self.assertIsNone(yearly[1])
        self.assertIsNone(seasonal[0])
        self.assertIsNone(seasonal[1])
        self.assertIsNone(monthly[0])
        self.assertIsNone(monthly[1])
        (yearly, seasonal, monthly) = MonthUtils.calculate_month(2021, 13)
        self.assertIsNone(yearly[0])
        self.assertIsNone(yearly[1])
        self.assertIsNone(seasonal[0])
        self.assertIsNone(seasonal[1])
        self.assertIsNone(monthly[0])
        self.assertIsNone(monthly[1])
        (yearly, seasonal, monthly) = MonthUtils.calculate_month(2021, 1)
        self.assertEqual(yearly, (2020, 12))
        self.assertEqual(seasonal, (2020, 12))
        self.assertEqual(monthly, (2020, 12))
        (yearly, seasonal, monthly) = MonthUtils.calculate_month(2021, 2)
        self.assertEqual(yearly, (2020, 12))
        self.assertEqual(seasonal, (2020, 12))
        self.assertEqual(monthly, (2021, 1))
        (yearly, seasonal, monthly) = MonthUtils.calculate_month(2021, 3)
        self.assertEqual(yearly, (2020, 12))
        self.assertEqual(seasonal, (2020, 12))
        self.assertEqual(monthly, (2021, 2))
        (yearly, seasonal, monthly) = MonthUtils.calculate_month(2021, 4)
        self.assertEqual(yearly, (2020, 12))
        self.assertEqual(seasonal, (2021, 3))
        self.assertEqual(monthly, (2021, 3))
        (yearly, seasonal, monthly) = MonthUtils.calculate_month(2021, 5)
        self.assertEqual(yearly, (2020, 12))
        self.assertEqual(seasonal, (2021, 3))
        self.assertEqual(monthly, (2021, 4))
        (yearly, seasonal, monthly) = MonthUtils.calculate_month(2021, 6)
        self.assertEqual(yearly, (2020, 12))
        self.assertEqual(seasonal, (2021, 3))
        self.assertEqual(monthly, (2021, 5))
        (yearly, seasonal, monthly) = MonthUtils.calculate_month(2021, 7)
        self.assertEqual(yearly, (2020, 12))
        self.assertEqual(seasonal, (2021, 6))
        self.assertEqual(monthly, (2021, 6))
        (yearly, seasonal, monthly) = MonthUtils.calculate_month(2021, 8)
        self.assertEqual(yearly, (2020, 12))
        self.assertEqual(seasonal, (2021, 6))
        self.assertEqual(monthly, (2021, 7))
        (yearly, seasonal, monthly) = MonthUtils.calculate_month(2021, 9)
        self.assertEqual(yearly, (2020, 12))
        self.assertEqual(seasonal, (2021, 6))
        self.assertEqual(monthly, (2021, 8))
        (yearly, seasonal, monthly) = MonthUtils.calculate_month(2021, 10)
        self.assertEqual(yearly, (2020, 12))
        self.assertEqual(seasonal, (2021, 9))
        self.assertEqual(monthly, (2021, 9))
        (yearly, seasonal, monthly) = MonthUtils.calculate_month(2021, 11)
        self.assertEqual(yearly, (2020, 12))
        self.assertEqual(seasonal, (2021, 9))
        self.assertEqual(monthly, (2021, 10))
        (yearly, seasonal, monthly) = MonthUtils.calculate_month(2021, 12)
        self.assertEqual(yearly, (2020, 12))
        self.assertEqual(seasonal, (2021, 9))
        self.assertEqual(monthly, (2021, 11))


if __name__ == '__main__':
    unittest.main()
