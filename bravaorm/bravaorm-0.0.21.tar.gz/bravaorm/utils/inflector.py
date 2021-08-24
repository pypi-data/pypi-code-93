# -*- coding: utf-8 -*-

from bravaorm.utils.singleton import Singleton

import re

class Portugues():

    def camelize(self, word):
        ''' Returns given word as CamelCased
        Converts a word like "send_email" to "SendEmail". It
        will remove non alphanumeric character from the word, so
        "who's online" will be converted to "WhoSOnline"'''
        return ''.join(w[0].upper() + w[1:] for w in re.sub('[^A-Z^a-z^0-9^:]+', ' ', word).split(' '))

    def underscore(self, word):
        ''' Converts a word "into_it_s_underscored_version"
        Convert any "CamelCased" or "ordinary Word" into an
        "underscored_word".
        This can be really useful for creating friendly URLs.'''

        new_word = re.sub('[^A-Z^a-z^0-9^\/]+', '_', re.sub('([a-z\d])([A-Z])', '\\1_\\2',
                                                            re.sub('([A-Z]+)([A-Z][a-z])', '\\1_\\2', re.sub('::', '/', word)))).lower()
        return self.pluralize(new_word) if "_" not in new_word else "_".join([self.pluralize(w) for w in new_word.split("_")])

    def pluralize(self, word):

        rules = [
            ['(?i)r$', 'res'],
            ['(?i)m$', 'ns'],
            ['(?i)il$', 'is'],
            ['(?i)l$', 'is'],
            ['(?i)(ao)$', 'oes'],
            ['(?i)([aeiou])$', '\\1s']
        ]

        uncountable_words = [
            'lapis',
            'onibus',
            'virus',
            'caridade',
            'bondade',
            'fe',
            'ouro',
            'prata',
            'bronze',
            'brisa',
            'oxigenio',
            'fome',
            'sede',
            'po',
            'plebe',
            'neve',
            'lenha',
            'cristianismo',
            'nazismo',
            'sinceridade',
            'lealdade',
            'status'
        ]

        irregular_words = {
            'bookmark': 'bookmarks',
            'direct': 'directs',
            'inbox': 'inboxes',
            'session': 'sessions',
            'fan': 'fans',
            'feed': 'feeds',
            'app':'apps',
            'server': 'servers',
            'mediaserver': 'mediaservers',
            'streamer': 'streamers',
            'mal': 'males',
            'consul': 'consules',
            'mel': 'meis',
            'cal': 'cais',
            'aval': 'avais',
            'mol': 'mois',
            'til': 'tis',
            'projetil': 'projeteis',
            'facil': 'faceis',
            'dificil': 'dificeis',
            'fossil': 'fosseis',
            'cep': 'ceps',
            'log': 'logs',
            'banner': 'banners',
            'faq': 'faqs',
            'newsletter': 'newsletters',
            'vip': 'vips',
            'deploy': 'deploys'
        }

        lower_cased_word = word.lower()

        if lower_cased_word in uncountable_words:
            return word

        if lower_cased_word in irregular_words:
            return irregular_words[word]

        for rule in range(len(rules)):
            match = re.search(rules[rule][0], word, re.IGNORECASE)
            if match:
                groups = match.groups()
                for k in range(0, len(groups)):
                    if groups[k] is None:
                        rules[rule][1] = rules[rule][1].replace(
                            '\\' + str(k + 1), '')
                return re.sub(rules[rule][0], rules[rule][1], word)

        return word

    def do_single_word(self, word):
        if len(word) > 2:

            rules = [
                ['((?i)ns)$', 'm'],
                ['((?i)[e][i]s)$', 'el'],
                ['(?i)(ais)$', 'al'],
                ['(?i)([i]s)$', 'il'],
                ['(?i)(oe)s$', 'ao'],
                ['(?i)(c)oes$', '\\1ao'],
                ['(?i)(r)es$', '\\1'],
                ['(?i)(z)es$', '\\1'],
                ['(?i)(s)es$', '\\1'],
                ['(?i)(le)ns$', '\\1n'],
                ['(?i)(de)ns$', '\\1n'],
                ['(?i)([aeou])is$', 'il'],
                ['(?i)([aeiou])s$', '\\1'],
                ['(?i)ns$', 'm'],
            ]

            uncountable_words = [
                'lapis',
                'onibus',
                'virus',
                'caridade',
                'bondade',
                'fe',
                'ouro',
                'prata',
                'bronze',
                'brisa',
                'oxigenio',
                'fome',
                'sede',
                'po',
                'plebe',
                'neve',
                'lenha',
                'cristianismo',
                'nazismo',
                'sinceridade',
                'lealdade',
                'status'
            ]

            irregular_words = {
                'bookmarks': 'bookmark',
                'directs': 'direct',
                'inboxes': 'inbox',
                'sessions': 'session',
                'fans': 'fan',
                'feeds': 'feed',
                'apps':'app',
                'servers': 'server',
                'mediaservers': 'mediaserver',
                'streamers': 'streamer',
                'males': 'mal',
                'consules': 'consul',
                'meis': 'mel',
                'cais': 'cal',
                'avais': 'aval',
                'mois': 'mol',
                'tis': 'til',
                'projeteis': 'projetil',
                'faceis': 'facil',
                'dificeis': 'dificil',
                'fosseis': 'fossil',
                'ceps': 'cep',
                'logs': 'log',
                'banners': 'banner',
                'faqs': 'faq',
                'newsletters': 'newsletter',
                'vips': 'vip',
                'deploys': 'deploy',
            }

            lower_cased_word = word.lower()

            for uncountable_word in uncountable_words:
                if lower_cased_word[-1 * len(uncountable_word):] == uncountable_word:
                    return word

            for irregular in irregular_words.keys():
                match = re.search('(' + irregular + ')$', word, re.IGNORECASE)
                if match:
                    return re.sub('(?i)' + irregular + '$', match.expand('\\1')[0] + irregular_words[irregular][1:], word)

            for rule in range(len(rules)):
                match = re.search(rules[rule][0], word, re.IGNORECASE)
                if match:
                    groups = match.groups()
                    for k in range(0, len(groups)):
                        if groups[k] is None:
                            rules[rule][1] = rules[rule][1].replace(
                                '\\' + str(k + 1), '')
                        return re.sub(rules[rule][0], rules[rule][1], word)
            return word
        return word

    def singularize(self, word):
        '''Singularizes English nouns.'''

        words = word.split('_')
        words_done = []
        for word in words:
            words_done.append(self.do_single_word(word))
        return '_'.join(words_done)

    def classify(self, table_name):
        '''Converts a table name to its class name according to rails
        naming conventions. Example: Converts "people" to "Person" '''

        return self.camelize(self.singularize(table_name))

    def tableize(self, class_name):
        ''' Converts a class name to its table name according to rails
        naming conventions. Example. Converts "Person" to "people" '''

        return self.underscore(class_name)


class Inflector(metaclass=Singleton):
    """
    Inflector for pluralizing and singularizing nouns.

    It provides methods for helping on creating programs
    based on naming conventions like on Ruby on Rails.
    """

    def __init__(self, Inflector=Portugues):
        assert callable(Inflector), "Inflector should be a callable obj"
        self.Inflector = Inflector()

    def pluralize(self, word):
        '''Pluralizes nouns.'''
        return self.Inflector.pluralize(word)

    def singularize(self, word):
        '''Singularizes nouns.'''
        return self.Inflector.singularize(word)

    def conditionalPlural(self, numer_of_records, word):
        '''Returns the plural form of a word if first parameter is greater than 1'''
        return self.Inflector.conditionalPlural(numer_of_records, word)

    def titleize(self, word, uppercase=''):
        '''Converts an underscored or CamelCase word into a sentence.
            The titleize function converts text like "WelcomePage",
            "welcome_page" or  "welcome page" to this "Welcome Page".
            If the "uppercase" parameter is set to 'first' it will only
            capitalize the first character of the title.'''
        return self.Inflector.titleize(word, uppercase)

    def camelize(self, word):
        ''' Returns given word as CamelCased
        Converts a word like "send_email" to "SendEmail". It
        will remove non alphanumeric character from the word, so
        "who's online" will be converted to "WhoSOnline"'''
        return self.Inflector.camelize(word)

    def underscore(self, word):
        ''' Converts a word "into_it_s_underscored_version"
        Convert any "CamelCased" or "ordinary Word" into an
        "underscored_word".
        This can be really useful for creating friendly URLs.'''
        return self.Inflector.underscore(word)

    def humanize(self, word, uppercase=''):
        '''Returns a human-readable string from word
        Returns a human-readable string from word, by replacing
        underscores with a space, and by upper-casing the initial
        character by default.
        If you need to uppercase all the words you just have to
        pass 'all' as a second parameter.'''
        return self.Inflector.humanize(word, uppercase)

    def variablize(self, word):
        '''Same as camelize but first char is lowercased
        Converts a word like "send_email" to "sendEmail". It
        will remove non alphanumeric character from the word, so
        "who's online" will be converted to "whoSOnline"'''
        return self.Inflector.variablize(word)

    def tableize(self, class_name):
        return self.Inflector.tableize(class_name)

    def classify(self, table_name):
        wrong = re.search('^ref_[0-9]+[_]', table_name)
        if wrong:
            table_name = table_name.replace(wrong.group(0), '')
        return self.Inflector.classify(table_name)

    def ordinalize(self, number):
        '''Converts number to its ordinal form.
        This method converts 13 to 13th, 2 to 2nd ...'''
        return self.Inflector.ordinalize(number)

    def unaccent(self, text):
        '''Transforms a string to its unaccented version.
        This might be useful for generating "friendly" URLs'''
        return self.Inflector.unaccent(text)

    def urlize(self, text):
        '''Transform a string its unaccented and underscored
        version ready to be inserted in friendly URLs'''
        return self.Inflector.urlize(text)

    def demodulize(self, module_name):
        return self.Inflector.demodulize(module_name)

    def modulize(self, module_description):
        return self.Inflector.modulize(module_description)

    def foreignKey(self, class_name, separate_class_name_and_id_with_underscore=1):
        ''' Returns class_name in underscored form, with "_id" tacked on at the end.
        This is for use in dealing with the database.'''
        return self.Inflector.foreignKey(class_name, separate_class_name_and_id_with_underscore)
