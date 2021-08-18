# MIT License
# Copyright (c) 2021  Zhi Liu(cowliucn@gmail.com)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# This is a simple demo to use cm2metrics to parse confusion matrix.

from cm2metrics.parse_cm import ConfusionMatrixParser
import pandas as pd

class_names = {0:"class0", 1:"class1", 2:"class2"}
df_cm = pd.DataFrame([(1,2,3),(4,5,6),(7,8,9)])
df_cm.rename(index=class_names, columns=class_names, inplace=True)

cm_parser = ConfusionMatrixParser(df_cm)
cm_parsed = cm_parser.parse_confusion_matrix()
print(cm_parsed)
tp = cm_parsed.loc["class0"].at["tp"]
print(tp)

cm_parser.print_summary(class_name="class0")
cm_parser.print_summary(class_index=0)
cm_parser.print_summary()
