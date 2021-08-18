import typing as tp

from take_text_preprocess.presentation import pre_process

from logic import get_class_name_from_file
from data.read_word_files import read_file, get_files_in_dir
from logic import CLASS_TO_POS_TAG, PUNCTUATION, SYMBOLS, \
    SUBSTANTIVE_PLACEHOLDERS, NUMERIC_PLACEHOLDERS, OOV_TOKEN


class ListWeakModel:
    """
    Class responsible for assigning POS Tags to words based on lists of part of speech classes.
    
    Methods:
    --------
        * get_word_per_class: Get dictionary from word class to words on file.
        * get_vocabulary: Get dictionary from words to possible POS Tag classes.
        * label_message: Labels the words of a given sentence with the appropriate POS Tag classes.
        * label_messages: Labels the words of a list of sentences with the appropriate POS Tag classes.
    
    Attributes:
    --------
        * words_per_class: Dictionary from word class to words on file.
        * vocabulary: Dictionary from words to possible POS Tag classes.
        * class_names: List of POS Tags used to label words.
        * class_to_postag: Dictionary from word class to POS Tag.
    """
    
    def __init__(self, directory_path: str, pre_processing_options: tp.List[str] = []):
        """
            Initializes the class by reading the word list files, storing the words by class and which files constitute
            each class.
            
            Possible pre processing options are EMAIL, URL, NUMBER and CODE.
            
        :param directory_path: Directory containing files to be read.
        :type directory_path: `str`
        :param pre_processing_options: Optional pre processing options to be applied. Defaults to basic pre processing.
        :type pre_processing_options: `tp.List[str]`
        """
        
        self.class_to_postag = CLASS_TO_POS_TAG
        
        self.class_names = list(self.class_to_postag.keys())
        
        self.__dir_name = directory_path
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

    def label_message(self, sentence: str) -> str:
        """
            Labels the words of a given sentence with the appropriate POS Tag classes.
            
            In case of ambiguity in the class choice the word is labeled with the `self.__out_of_vocab_token`.
            
        :param sentence: Sentence to be labeled.
        :type sentence: `str`
        :return: Labels for the words on the sentence.
        :rtype: `str`
        """
        split_sentence = pre_process(sentence, self.__pre_processing_options).split()
            
        sentence_labels = []
        
        for word in split_sentence:
            sentence_labels.append(self.vocabulary.get(word, self.__out_of_vocab_token))
            
        return ' '.join(['|'.join([label for label in word_labels]) if len(word_labels) > 1 else word_labels[0]
                         for word_labels in sentence_labels]
                        )

    def label_messages(self, sentences: tp.List[str]) -> tp.List[str]:
        """
            Labels the words of a list of sentences with the appropriate POS Tag classes.
            
        :param sentences: List of sentences to be labeled.
        :type sentences: `tp.List[str]`
        :return: List of labels for each sentences.
        :rtype: `tp.List[str]`
        """
        return [self.label_message(sentence) for sentence in sentences]
    
    def __generate_words_per_class_dict(self) -> None:
        """ Reads words from files and stores them by POS Tag class in a dictionary. """
        words_per_class = {class_name: set() for class_name in self.class_names}
        for file_name in get_files_in_dir(self.__dir_name):
            class_name = get_class_name_from_file(file_name)
            words_per_class[class_name].update(
                set(read_file(self.__dir_name + file_name, self.__pre_processing_options))
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
