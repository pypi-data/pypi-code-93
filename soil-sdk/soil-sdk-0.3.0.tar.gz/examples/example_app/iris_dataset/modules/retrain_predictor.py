''' Module to train the predictor '''
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from soil import modulify
from soil import logger
from soil.data_structures.random_forest_model import RandomForestModel


@modulify(output_types=lambda *input_types, **args: [RandomForestModel])
def retrain_predictor(data):
    ''' Trains the predictor with available data '''
    model = RandomForestClassifier(oob_score=True)
    metadata = data.metadata

    # #  This is here to prevent a weird bug.
    if data.data is not None:
        data = data.data

    x_labels = metadata['columns']['X_columns']
    y_labels = metadata['columns']['y_columns']

    df = pd.DataFrame(data)
    x = df[x_labels]
    y = df[y_labels].values.ravel()

    model = model.fit(x, y)

    logger.info('Model oob score: %s', model.oob_score_)
    logger.info('Model error: %s', 1 - model.oob_score_)

    model_metadata = {
        'oob_score': model.oob_score_,
        'error': 1 - model.oob_score_,
        'x_labels': x_labels,
        'y_labels': y_labels
        }
    return [RandomForestModel(model, model_metadata)]
