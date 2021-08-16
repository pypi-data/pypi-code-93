import csv
import torch
import sys
import SentenceTokenizer as st
from torch.utils.data import DataLoader, IterableDataset, Dataset
import pickle

class MultiSentWordDataset(IterableDataset):
    def __init__(self, path, label_column, encoding, separator, use_pre_processing=True):
        self.use_pre_processing = use_pre_processing
        self.__set_file_iterable(path, encoding, separator)
        self.__set_default_process()
        self.line_mapper = self.line_mapper_training if label_column else \
            self.line_mapper_predicting


    def __set_file_iterable(self, path, encoding, separator):
        self.file_pointer = open(path, encoding=encoding)
        self.file_iterable = csv.reader(self.file_pointer,  delimiter=separator)
        next(self.file_iterable)

    def __set_default_process(self):
        if self.use_pre_processing:
            self.tokenizer = st.SentenceTokenizer()
            self.process = self.pre_process
        else:
            self.process = self.split_sentence

    def close_file(self):
        self.file_pointer.close()

    def line_mapper_training(self, line):
        return [self.process(line[0]), self.split_sentence(line[1])]

    def line_mapper_predicting(self, line):
        return [self.process(line[0])]

    def pre_process(self, sentence):
        return self.tokenizer.process_message(sentence).split()

    def split_sentence(self, sentence):
        return sentence.split()

    def __iter__(self):
        file_iter = self.file_iterable
        return map(self.line_mapper, file_iter)

    def __len__(self):
        return 1

class MultiSentWordBatchDataset(Dataset):
    def __init__(self, use_pre_processing, sentences):
        self.use_pre_processing = use_pre_processing
        self.sentences = sentences
        self.tokenizer = st.SentenceTokenizer()
        self.__set_default_process()

    def pre_process(self, sentence):
        return self.tokenizer.process_message(sentence).split()

    def split_sentence(self, sentence):
        return sentence.split()

    def __set_default_process(self):
        if self.use_pre_processing:
            self.tokenizer = st.SentenceTokenizer()
            self.process = self.pre_process
        else:
            self.process = self.split_sentence

    def __len__(self):
        return len(self.sentences)

    def __getitem__(self, idx):
        return [self.process(self.sentences[idx]['sentence']), int(self.sentences[idx]['id'])]

class MultiSentWordDataLoader(DataLoader):
    def __init__(self, dataset, vocabs, pad_string, unk_string,
                 postag_model=None, input_vocab=None,
                 tensor_lens=True, use_index=False, **kwargs):
        super(MultiSentWordDataLoader, self).__init__(
            dataset=dataset,
            collate_fn=self.collate_fn,
            **kwargs
        )

        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        self.pad_string = pad_string
        self.unk_string = unk_string
        self.tensor_lens = tensor_lens
        self.vocabs = vocabs
        self.use_index = use_index
        self.postag = postag_model
        self.use_pre_processing = dataset.use_pre_processing

    def unlexicalize(self, sentence):
        return [
            self.sentences_vocab.f2i[word] if word in self.sentences_vocab else
            self.sentences_vocab.f2i[self.unk_string] for word in sentence]

    def pad(self, sentence):
        return sentence + [self.sentences_vocab.f2i[self.pad_string]] * (
                self.max_len - len(sentence))

    def predict_tags_batch(self, batches):
        dict_list = []
        msg_list = []
        ner_list = []
        for idx, row in enumerate(batches):
            if len(row) > 1:
                ner_list.append(row[1])
            dict_list.append({'id': idx, 'sentence': ' '.join(row[0])})
            msg_list.append(row[0])
        tags = sorted(self.postag.predict_batch(filepath='',
                                                sentence_column='',
                                                pad_string='<pad>',
                                                unk_string='<unk>',
                                                batch_size=len(dict_list),
                                                shuffle=True,
                                                use_pre_processing=False,
                                                output_lstm=False,
                                                sentences=dict_list),
                      key=lambda content_dict: content_dict['id'])
        if len(ner_list) > 0:
            batches = [[msg, tag_dict['tags'].split(), ner]
                       for msg, tag_dict, ner in zip(msg_list, tags, ner_list)]
        else:
            batches = [[msg, tag_dict['tags'].split()]
                       for msg, tag_dict in zip(msg_list, tags)]
        return batches


    def collate_fn(self, batches):
        batches = filter(lambda x: len(x[0]) > 0, batches)
        if self.postag:
            batches = self.predict_tags_batch(batches)
        sentences_list = list(zip(*batches))
        lens = [len(sentence) for sentence in sentences_list[0]]
        self.max_len = max(lens)
        sequences_collation = []
        for sentences, sentences_vocab in zip(sentences_list, self.vocabs):
            self.sentences_vocab = sentences_vocab
            sentences = map(self.pad, map(self.unlexicalize, sentences))
            sentences = list(sentences)
            sequences_collation.append(torch.LongTensor(sentences).unsqueeze(0))
        sequence_tensor = torch.cat(sequences_collation).to(self.device)
        lens_tensor = torch.LongTensor(lens).to(self.device)
        if self.use_index:
            index_tensor = torch.LongTensor(sentences_list[-1]).to(self.device)
            return sequence_tensor, lens_tensor, index_tensor
        else:
            return sequence_tensor, lens_tensor, None 

maxInt = sys.maxsize
while True:
    # decrease the maxInt value by factor 10 
    # as long as the OverflowError occurs.
    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)
