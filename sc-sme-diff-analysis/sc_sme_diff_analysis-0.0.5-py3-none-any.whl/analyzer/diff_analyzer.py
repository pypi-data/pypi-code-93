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

from sc_sme_diff_analysis.utils import ConfigUtils
from . import BranchSummaryDiffAnalyzer
from . import ManagerSummaryDiffAnalyzer
from . import ValidClearingAccountDetailDiffAnalyzer
from . import ValidCreditAccountDetailDiffAnalyzer


class DiffAnalyzer:
    """
    差异分析类
    """

    def __init__(self):
        pass

    def analysis(self):
        config = ConfigUtils.get_config()
        # 有效授信户-客户经理明细-差异分析
        analyzer = ValidCreditAccountDetailDiffAnalyzer(config=config, is_first_analyzer=True)
        result = analyzer.analysis()
        if result != 0:
            return result
        # 对公结算户考核明细表-差异分析
        analyzer = ValidClearingAccountDetailDiffAnalyzer(config=config)
        result = analyzer.analysis()
        if result != 0:
            return result
        # 客户经理汇总差异分析
        analyzer = ManagerSummaryDiffAnalyzer(config=config)
        result = analyzer.analysis()
        if result != 0:
            return result
        # 机构汇总差异分析
        analyzer = BranchSummaryDiffAnalyzer(config=config)
        result = analyzer.analysis()
        return result
