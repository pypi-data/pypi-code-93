import matplotlib.pyplot as plt


class VisualizeMixin:
    def plot_training_metrics(self, figsize=(16, 4)):
        """ plots the loss and validation accuracy during training for a model """
        if self.training_metrics:
            fig = plt.figure(figsize=figsize)
            num_iterations = len(self.training_metrics["validation_accuracy"])
            plt.plot(self.training_metrics["train_accuracy"], label="training")
            plt.plot(self.training_metrics["validation_accuracy"], label="validation")
            plt.xlabel("epochs")
            plt.ylabel("accuracy")
            plt.xlim(0, num_iterations)
            plt.ylim(0, 1)
            plt.legend(loc="best")
            plt.show()
        else:
            print("No training metrics for this model")
