import pandas as pd
import pytest


class MulticlassTestDataset:
    def __init__(self, multiple_text_column, include_label_col, is_val_df=False):
        self.multiple_text_column = multiple_text_column
        self.include_label_col = include_label_col
        self.is_val_df = is_val_df

    def get_data(self):
        text_col_1 = [
            'This is a small sample dataset containing cleaned text data.',
            'It was created manually so that it can be used for tests in text-classification tasks.',
            'It can be leveraged in tests to verify that codeflows are working as expected.',
            'It can also be used to verify that a machine learning model training successfully.',
            'It should not be used to validate the model performance using metrics.'
        ]
        data = {'text_first': text_col_1}

        if self.multiple_text_column:
            data['text_second'] = [
                'This is an additional column.',
                'It was created to test the multiple-text columns scenario for classification.',
                'It can be leveraged in tests to verify that multiple-column codeflows are functional.',
                'It can also be used to verify that a ML model trained successfully with multiple columns.',
                'It should not be used to validate the multiple text columns model performance'
            ]
        if self.include_label_col:
            if self.is_val_df:
                data['labels_col'] = ["XYZ", "DEF", "ABC", "ABC", "XYZ"]
            else:
                data['labels_col'] = ["XYZ", "PQR", "ABC", "ABC", "XYZ"]

        return pd.DataFrame(data)


@pytest.fixture
def MulticlassDatasetTester(multiple_text_column, include_label_col):
    """Create MulticlassDatasetTester object"""
    return MulticlassTestDataset(multiple_text_column, include_label_col)


@pytest.fixture
def MulticlassValDatasetTester(multiple_text_column, include_label_col):
    """Create MulticlassDatasetTester object"""
    return MulticlassTestDataset(multiple_text_column, include_label_col, is_val_df=True)
