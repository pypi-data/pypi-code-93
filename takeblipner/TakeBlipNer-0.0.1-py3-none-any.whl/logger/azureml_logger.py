import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
from azureml.core import Run, Model

class AzuremlLogger(object):
    def __init__(self, run, torch_version):
        self.run = run
        self.torch_version = torch_version

    def save_train_parameters(self, args):
        self.run.log('input-path', args.input_path)
        self.run.log('separator', args.separator)
        self.run.log('encoding', args.encoding)
        self.run.log('sentence_column', args.sentence_column)
        self.run.log('label_column', args.label_column)
        self.run.log('save-dir', args.save_dir)
        self.run.log('tensorboard', args.tensorboard)
        self.run.log('use_pre_processing', args.use_pre_processing)
        self.run.log('wordembed-path', args.wordembed_path)
        self.run.log('postag_model_path', args.postag_model_path)
        self.run.log('postag_label_path', args.postag_label_path)
        self.run.log('epochs', args.epochs)
        self.run.log('dropout-prob', args.dropout_prob)
        self.run.log('batch-size', args.batch_size)
        self.run.log('shuffle', args.shuffle)
        self.run.log('learning-rate', args.learning_rate)
        self.run.log('learning-rate-decay', args.learning_rate_decay)
        self.run.log('max-patience', args.max_patience)
        self.run.log('max-decay-num', args.max_decay_num)
        self.run.log('patience-threshold', args.patience_threshold)
        self.run.log('ckpt-period', args.ckpt_period)
        self.run.log('val', args.val)
        self.run.log('val-path', args.val_path)
        self.run.log('val-period', args.val_period)
        self.run.log('samples', args.samples)
        self.run.log('word-dim', args.word_dim)
        self.run.log('lstm-dim', args.lstm_dim)
        self.run.log('lstm-layers', args.lstm_layers)
        self.run.log('bidirectional', args.bidirectional)
        self.run.log('input-data-ref', args.input_data_ref)
        self.run.log('wordembed-model-name', args.wordembed_model_name)
        self.run.log('wordembed-model-version', args.wordembed_model_version)
        self.run.log('alpha', args.alpha)

    def save_validation_metrics(self, metric):
        self.run.log('negative_loglik', metric.item())
        
    def save_confusion_matrix(self, targets_all, preds_all, current_epoch):
        image_file_name = 'confusion_matrix_epoch_{}.png'.format(current_epoch)
        labels = list(set(targets_all))
        labels.sort()
        cm = confusion_matrix(targets_all, preds_all)
        plt.figure(figsize=(16,10))
        sns.heatmap(cm, annot=True, cmap=plt.cm.Blues, xticklabels=labels, yticklabels=labels,  fmt='d')
        plt.yticks(rotation=0) 
        plt.savefig(image_file_name)
        self.run.log_image(image_file_name, plot=plt)

    def save_confusion_matrix_from_tensor(self, confusion_matrix, labels, current_epoch):
        image_file_name = 'confusion_matrix_validation_{}.png'.format(current_epoch)
        plt.figure(figsize=(16,10))
        sns.heatmap(confusion_matrix.long().numpy(), annot=True, cmap=plt.cm.Blues, xticklabels=labels, yticklabels=labels, fmt='d')
        plt.yticks(rotation=0) 
        plt.savefig(image_file_name)
        self.run.log_image(image_file_name, plot=plt)

    def save_loss_convergence(self, loss):
        image_file_name = 'validation_loss.png'
        fig = plt.figure()
        plt.plot(loss, color='blue')
        plt.legend(['Validation Loss'], loc='upper right')
        plt.xlabel('Number of validating examples')
        plt.ylabel('Negative log likelihood loss')
        fig.savefig(image_file_name)
        self.run.log_image(image_file_name, plot=fig)

    def save_report(self, report):
        self.run.log('Accuracy', report['accuracy'])
        self.run.log('Precision - Macro Avg', report['macro avg']['precision'])
        self.run.log('Recall - Macro Avg', report['macro avg']['recall'])
        self.run.log('F1-score - Macro Avg', report['macro avg']['f1-score'])
        self.run.log('Precision - Weighted Avg', report['weighted avg']['precision'])
        self.run.log('Recall - Weighted Avg', report['weighted avg']['recall'])
        self.run.log('F1-score - Weighted Avg', report['weighted avg']['f1-score'])
    
    def save_metrics(self, confusion_matrix, labels):
        precision = confusion_matrix.diag() / confusion_matrix.sum(dim=0)
        recall = confusion_matrix.diag() / confusion_matrix.sum(dim=1)
        f1_score = 2*(precision*recall / (precision + recall))
        #self.run.log('Accuracy', report['accuracy'])
        for index, label in enumerate(labels):
            self.run.log(label + ' Precision', precision[index].numpy().item())
            self.run.log(label + ' Recall', recall[index].numpy().item())
            self.run.log(label + ' F1-score', f1_score[index].numpy().item())

        self.run.log('Model Precision', precision[precision >= 0].mean().numpy().item())
        self.run.log('Model Recall', recall[recall >= 0].mean().numpy().item())
        self.run.log('Model F1-score', f1_score[f1_score >= 0].mean().numpy().item())

    def register_ner_model(self, training_mount_folder, ner_registry):
        ner_model = Model.register(
            workspace=self.run.experiment.workspace,
            model_name=ner_registry,
            model_path=training_mount_folder,
            child_paths=['nermodel.pkl', 'nermodel.py'],
            description='NER Pytorch Model',
            model_framework=Model.Framework.PYTORCH,  
            model_framework_version=self.torch_version, 
            tags = {'runId': self.run.id}
        )
        self.run.log(ner_registry, ner_model)

    def register_ner_label(self, training_mount_folder, ner_registry_label):
        ner_label= Model.register(
            workspace=self.run.experiment.workspace,
            model_name=ner_registry_label,
            model_path=training_mount_folder,
            child_paths=['ner-vocab-label.pkl', 'vocab.py'],
            description='NER Pytorch Labels',
            tags={'runId': self.run.id}
        )
        self.run.log(ner_registry_label, ner_label)