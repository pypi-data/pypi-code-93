''' Module to do the predictions given a model and data points to predict on. '''
from soil import modulify
# from soil.data_structures.es_data_structure import Predictions
from soil.data_structures.predictions import Predictions


@modulify(output_types=lambda *input_types, **args: [Predictions])
def make_predictions(model, unlabeled):
    ''' Module function to do the predictions given a model and data points to predict on. '''
    regressor = model.data

    x_labels = model.metadata['x_labels']

    d_y = regressor.predict(unlabeled.data[x_labels])

    new_df = unlabeled.data[x_labels].copy()
    new_df['species'] = d_y
    new_df_dict = new_df.to_dict('records')
    predictions = list({'_id': i, **v} for i, v in enumerate(new_df_dict))

    return [Predictions(predictions, metadata={'index': 'simple-preds'})]
