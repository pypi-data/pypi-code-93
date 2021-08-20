import typing as tp
from unidecode import unidecode

from take_text_preprocess.presentation import pre_process

from weak_postagger.logic.utils import get_class_name_from_file
from weak_postagger.data.read_word_files import read_file, get_files_in_dir
from weak_postagger.logic.param import CLASS_TO_POS_TAG, PUNCTUATION, SYMBOLS, \
    SUBSTANTIVE_PLACEHOLDERS, NUMERIC_PLACEHOLDERS, OOV_TOKEN


class ListWeakModel:
    """
    Class responsible for assigning POS Tags to words based on lists of part of speech classes.
    
    Methods:
    --------
        * get_word_per_class: Get dictionary from word class to words on file.
        * get_vocabulary: Get dictionary from words to possible POS Tag classes.
        * label_message: Labels the words of a given sentence with the appropriate POS Tag classes.
    
    Attributes:
    --------
        * words_per_class: Dictionary from word class to words on file.
        * vocabulary: Dictionary from words to possible POS Tag classes.
        * class_names: List of POS Tags used to label words.
        * class_to_postag: Dictionary from word class to POS Tag.
    """
    
    def __init__(self, directory_path: str, use_preprocess: bool = True, pre_processing_options: tp.List[str] = []):
        """
            Initializes the class by reading the word list files, storing the words by class and which files constitute
            each class.
            
            Possible pre processing options are EMAIL, URL, NUMBER and CODE.
            
        :param directory_path: Directory containing files to be read.
        :type directory_path: `str`
        :param use_preprocess: Flags whether text pre processing should be used. Defaults to true.
        :type use_preprocess: `bool`
        :param pre_processing_options: Optional pre processing options to be applied. Defaults to basic pre processing.
        :type pre_processing_options: `tp.List[str]`
        """
        
        self.class_to_postag = CLASS_TO_POS_TAG
        
        self.class_names = list(self.class_to_postag.keys())
        
        self.__dir_name = directory_path
        self.__use_preprocessing = use_preprocess
        self.__pre_processing_options = pre_processing_options
        self.__out_of_vocab_token = OOV_TOKEN
        self.__punctuation = PUNCTUATION
        self.__symbols = SYMBOLS
        self.__substantive_placeholder = SUBSTANTIVE_PLACEHOLDERS
        self.__numeric_placeholder = NUMERIC_PLACEHOLDERS
        
        self.__generate_words_per_class_dict()
        self.__generate_vocabulary()
    
    def get_word_per_class(self) -> tp.Dict[str, tp.Set[str]]:
        """
            Get dictionary from word class to words on file.
            
        :return: Dictionary of POS Tags to a set of unique words in each class as read from file.
        :rtype: `tp.Dict[str, tp.Set[str]]`
        """
        return self.words_per_class
    
    def get_vocabulary(self) -> tp.Dict[str, tp.Set[str]]:
        """
            Get dictionary from words to possible POS Tag classes.

        :return: Dictionary from words to possible POS Tag classes.
        :rtype: `tp.Dict[str, tp.Set[str]]`
        """
        return self.vocabulary
    
    def label_message(self, sentence: str) -> tp.Tuple[str, str]:
        """
            Labels the words of a given sentence with the appropriate POS Tag classes.
            
            In case of ambiguity in the class choice the word is labeled with the `self.__out_of_vocab_token`.
            
        :param sentence: Sentence to be labeled.
        :type sentence: `str`
        :return: A tuple with the preprocessed sentence and the labels for the words on the sentence.
        :rtype: `tp.Tuple[str, str]`
        """
        if self.__use_preprocessing:
            split_sentence = pre_process(sentence, self.__pre_processing_options).split()
        else:
            split_sentence = sentence.split()
        
        sentence_labels = []
        
        for index, word in enumerate(split_sentence):
            sentence_labels.append(self.vocabulary.get(word,
                                                       self.vocab_normalized.get(unidecode(word.lower()),
                                                                                 self.__compound_words(index,
                                                                                                       split_sentence))
                                                       )
                                   )
        
        resulting_labels = ' '.join(
            ['|'.join([label for label in word_labels]) if len(word_labels) > 1 else word_labels[0]
             for word_labels in sentence_labels]
            )
        processed_sentence = ' '.join(split_sentence)
        
        return processed_sentence, resulting_labels
    
    def __compound_words(self, word_index: int, sentence: tp.List[str]) -> tp.List[str]:
        """
            Verifies if a word is part of a compound word.
            
        :param word_index: Word position.
        :type word_index: `int`
        :param sentence: Sentence being analysed.
        :type sentence: `tp.List[str]`
        :return: Label for the compound word.
        :rtype: `tp.List[str]`
        """
        label = self.__out_of_vocab_token
        
        window_position = max(0, word_index - 5)
        while window_position < min(word_index + 6, len(sentence)) and label == self.__out_of_vocab_token:
            if window_position < word_index:
                words_list = sentence[window_position:word_index + 1]
            elif window_position > word_index:
                words_list = sentence[word_index:window_position + 1]
            else:
                words_list = sentence[word_index]
            words = ' '.join(
                [unidecode(word.lower()) for word in words_list])
            label = self.vocab_normalized.get(words, self.__out_of_vocab_token)
            window_position += 1
        return label
    
    def __generate_words_per_class_dict(self) -> None:
        """ Reads words from files and stores them by POS Tag class in a dictionary. """
        words_per_class = {class_name: set() for class_name in self.class_names}
        for file_name in get_files_in_dir(self.__dir_name):
            class_name = get_class_name_from_file(file_name)
            words_per_class[class_name].update(
                set(read_file(self.__dir_name + file_name, pre_processing_opt=self.__pre_processing_options))
            )
        self.words_per_class = words_per_class
    
    def __generate_vocabulary(self) -> None:
        """ Creates a dictionary with all words from the lists to its possible POS Tagging classes. """
        self.vocabulary = {}
        self.__remove_word_by_size(word_class='substantivos', word_size=1)
        
        for class_name in self.words_per_class.keys():
            for word in self.words_per_class[class_name]:
                self.vocabulary[word] = self.vocabulary.get(word, []) + [self.class_to_postag[class_name]]
        
        self.__update_vocab_by_list(self.__punctuation, 'PON')
        self.__update_vocab_by_list(self.__symbols, 'SIMB')
        self.__update_vocab_by_list(self.__substantive_placeholder, 'SUBS')
        self.__update_vocab_by_list(self.__numeric_placeholder, 'NUMB')
        self.__update_vocab_by_list(['LAUGH'], 'INT')
        
        self.vocabulary = {key: sorted(list(set(value))) for key, value in self.vocabulary.items()}
        
        self.vocab_normalized = {unidecode(k.lower()): v for (k, v) in
                                 self.vocabulary.items()}
    
    def __update_vocab_by_list(self, words: tp.List[str], class_name: str) -> None:
        """
            Update vocabulary with words on input list by setting their label to the given POS Tag class.
            
        :param words: A list of words to receive the same POS Tag label.
        :type words: `tp.List[str]`
        :param class_name: POS Tag label to be give to the input words.
        :type class_name: `str`
        """
        for word in words:
            if class_name not in self.vocabulary.get(word, []):
                self.vocabulary[word] = self.vocabulary.get(word, []) + [class_name]
    
    def __remove_word_by_size(self, word_class: str, word_size: int = 1) -> None:
        """
            Remove from vocabulary words from a `word_class` smaller than `word_size`.
            
        :param word_class: POS Tag to be processed.
        :type word_class: `str`
        :param word_size: Word size threshold. Defaults to one.
        :type word_size: `int`
        """
        self.words_per_class[word_class] = {i for i in self.words_per_class[word_class] if len(i) > word_size}
