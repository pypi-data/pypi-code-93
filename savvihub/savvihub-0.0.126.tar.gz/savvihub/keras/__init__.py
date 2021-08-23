import warnings
import keras
import numpy as np

from savvihub import log, Image
from savvihub.constants import SAVVIHUB_PLOTS_FILETYPE_IMAGE, SAVVIHUB_PLOTS_FILETYPE_IMAGES


class SavviHubCallback(keras.callbacks.Callback):
    def __init__(self, data_type=None, validation_data=None, num_images=None, labels=None, start_epoch=0,
                 save_image=False):
        super().__init__()
        self._data_type = data_type
        self._num_images = num_images or 1
        self._labels = labels
        self._start_epoch = start_epoch
        self._save_image = save_image

        self.validation_data = None
        if validation_data is not None:
            self.validation_data = validation_data

    def _results_to_predicts(self, results):
        predicts = []
        if results[0].shape[-1] == 1:
            if len(self._labels) == 2:
                predicts = [self._lables[1] if result[0] > 0.5 else self._labels[0] for result in results]
            else:
                if not self._labels:
                    warnings.warn('Cannot find labels for prediction')
                predicts = [result[0] for result in results]
        else:
            argmax_results = np.argmax(np.stack(results), axis=1)
            if not self._labels:
                warnings.warn('Cannot find labels for prediction')
                predicts = argmax_results
            else:
                for argmax_result in argmax_results:
                    try:
                        predicts.append(self._labels[argmax_result])
                    except IndexError:
                        predicts.append(argmax_result)
        return predicts

    def _inference(self):
        x_val, y_val = self.validation_data

        if self._num_images > len(x_val):
            self._num_images = len(x_val)

        random_indices = np.random.choice(len(x_val), self._num_images, replace=False)
        x_val_random = [x_val[i] for i in random_indices]
        y_val_random = [y_val[i] for i in random_indices]

        results = self.model.predict(np.stack(x_val_random), batch_size=1)
        predicts = self._results_to_predicts(results)

        captions = []
        for predict, truth in zip(predicts, y_val_random):
            captions.append(f'Pred: {predict} Truth: {truth}')

        return [Image(x, caption=caption) for x, caption in zip(x_val_random, captions)]

    def on_epoch_end(self, epoch, logs=None):
        log(step=epoch+self._start_epoch+1, row=logs)

        if self._save_image and \
                self._data_type in (SAVVIHUB_PLOTS_FILETYPE_IMAGE, SAVVIHUB_PLOTS_FILETYPE_IMAGES):
            if self.validation_data is None:
                warnings.warn('Cannot find validation_data')

            log({
                "validation_image": self._inference(),
            })
