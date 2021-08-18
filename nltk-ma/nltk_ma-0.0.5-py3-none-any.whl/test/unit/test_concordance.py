import unittest
from io import StringIO
from nltkma.text import find_concordance
from nltkma.collocations import BigramCollocationFinder, BigramAssocMeasures


class TestConcordance(unittest.TestCase):
    """Text constructed using: http://www.nltk.org/book/ch01.html"""

    def test_concordance_list_1(self):
        corpus_token = ['Traditionally', ',', 'black', 'Black', 'Asians', 'Blacks', 'blacks', 'bame', 'a', 'text', 'is',
                        'BAME', 'Asian', 'BAME', 'Asian', 'BAME', 'Asian', 'BAME', 'Asian', 'understood', 'minority',
                        ',', 'asian', 'to', 'be', 'a', ',' 'piece', 'of', 'written', 'or', 'spoken', 'material', '.',
                        'in', 'its', 'primary', 'form', '(', 'as', 'opposed', 'to', 'a', 'paraphrase', 'or']
        corpus_token_cleaned = ['Traditionally', 'black', 'Black', 'Asians', 'Blacks', 'blacks', 'bame', 'a', 'text',
                                'is',
                                'BAME', 'Asian', 'BAME', 'Asian', 'BAME', 'Asian', 'BAME', 'Asian', 'understood',
                                'minority',
                                'asian', 'to', 'be', 'a', 'piece', 'of', 'written', 'or', 'spoken', 'material', 'in',
                                'its',
                                'primary', 'form', '(', 'as', 'opposed', 'to', 'a', 'paraphrase', 'or']

        pivot_token = ['minority']
        target_token = ['asian']
        result = find_concordance(pivot_token, target_token, (3, 3), (1, 10), corpus_token, corpus_token_cleaned, True,
                                  True, False)

        expected_line = 'Asian BAME Asian understood minority , asian to be a ,piece of written or spoken material .'
        expected_left_line = 'BAME Asian understood'
        expected_left_context = 'Asian'
        expected_right_line = ', asian to be'
        expected_right_context = 'a ,piece of written or spoken material .'
        expected_query = 'minority'
        assert expected_line == result[0].line
        assert expected_left_context == result[0].left_context
        assert expected_left_line == result[0].left_span
        assert expected_query == result[0].query
        assert expected_right_line == result[0].right_span
        assert expected_right_context == result[0].right_context

    def test_concordance_list_2(self):
        corpus_token = ['Traditionally', ',', 'black', 'Black', 'Asians', 'Blacks', 'blacks', 'bame', 'a', 'text',
                        'is',
                        'BAME', 'Asian', 'BAME', 'Asian', 'BAME', 'Asian', 'BAME', 'Asian', 'understood',
                        'minority',
                        ',', 'asian', 'to', 'be', 'a', ',' 'piece', 'of', 'written', 'or', 'spoken', 'material',
                        '.',
                        'in', 'its', 'primary', 'form', '(', 'as', 'opposed', 'to', 'a', 'paraphrase', 'or']
        corpus_token_cleaned = ['Traditionally', 'black', 'Black', 'Asians', 'Blacks', 'blacks', 'bame', 'a',
                                'text',
                                'is',
                                'BAME', 'Asian', 'BAME', 'Asian', 'BAME', 'Asian', 'BAME', 'Asian', 'understood',
                                'minority',
                                'asian', 'to', 'be', 'a', 'piece', 'of', 'written', 'or', 'spoken', 'material',
                                'in',
                                'its',
                                'primary', 'form', '(', 'as', 'opposed', 'to', 'a', 'paraphrase', 'or']

        pivot_token = ['minority']
        target_token = ['asian']
        result = find_concordance(pivot_token, target_token, (3, 3), (1, 10), corpus_token, corpus_token_cleaned,
                                  True,
                                  False,
                                  False)

        expected_line = 'Asian BAME Asian understood minority , asian to be a ,piece of written or spoken material . ' \
                        'in its primary'
        expected_left_line = 'BAME Asian understood'
        expected_left_context = 'Asian'
        expected_right_line = ', asian to be'
        expected_right_context = 'a ,piece of written or spoken material . in its primary'
        expected_query = 'minority'
        assert expected_line == result[0].line
        assert expected_left_context == result[0].left_context
        assert expected_left_line == result[0].left_span
        assert expected_query == result[0].query
        assert expected_right_line == result[0].right_span
        assert expected_right_context == result[0].right_context

    def test_concordance_list_3(self):
        corpus_token = ['Traditionally', ',', 'black', 'Black', 'Asians', 'Blacks', 'blacks', 'bame', 'a', 'text',
                        'is',
                        'BAME', 'Asian', 'BAME', 'Asian', 'BAME', 'Asian', 'BAME', 'Asian', 'understood',
                        'minority',
                        ',', 'asian', 'to', 'be', 'a', ',' 'piece', 'of', 'written', 'or', 'spoken', 'material',
                        '.',
                        'in', 'its', 'primary', 'form', '(', 'as', 'opposed', 'to', 'a', 'paraphrase', 'or']
        corpus_token_cleaned = ['Traditionally', 'black', 'Black', 'Asians', 'Blacks', 'blacks', 'bame', 'a',
                                'text',
                                'is',
                                'BAME', 'Asian', 'BAME', 'Asian', 'BAME', 'Asian', 'BAME', 'Asian', 'understood',
                                'minority',
                                'asian', 'to', 'be', 'a', 'piece', 'of', 'written', 'or', 'spoken', 'material',
                                'in',
                                'its',
                                'primary', 'form', '(', 'as', 'opposed', 'to', 'a', 'paraphrase', 'or']

        pivot_token = []
        target_token = []
        result = find_concordance(pivot_token, target_token, (3, 3), (1, 10), corpus_token, corpus_token_cleaned,
                                  True,
                                  False,
                                  False)

        expected = []

        assert expected == result

    def test_concordance_list_4(self):
        corpus_token = ['Traditionally', ',', 'black', 'Black', 'Asians', 'Blacks', 'blacks', 'bame', 'a', 'text',
                        'is',
                        'BAME', 'Asian', 'BAME', 'Asian', 'BAME', 'Asian', 'BAME', 'Asian', 'understood',
                        'minority',
                        ',', 'asian', 'to', 'be', 'a', ',' 'piece', 'of', 'written', 'or', 'spoken', 'material',
                        '.',
                        'in', 'its', 'primary', 'form', '(', 'as', 'opposed', 'to', 'a', 'paraphrase', 'or']
        corpus_token_cleaned = ['Traditionally', 'black', 'Black', 'Asians', 'Blacks', 'blacks', 'bame', 'a',
                                'text',
                                'is',
                                'BAME', 'Asian', 'BAME', 'Asian', 'BAME', 'Asian', 'BAME', 'Asian', 'understood',
                                'minority',
                                'asian', 'to', 'be', 'a', 'piece', 'of', 'written', 'or', 'spoken', 'material',
                                'in',
                                'its',
                                'primary', 'form', '(', 'as', 'opposed', 'to', 'a', 'paraphrase', 'or']

        pivot_token = ['minority']
        target_token = ['Asian']
        actual = find_concordance(pivot_token, target_token, (1, 1), (1, 10), corpus_token, corpus_token_cleaned,
                                  True,
                                  False,
                                  False)

        expected = []
        assert expected == actual

    def test_concordance_list_1(self):
        corpus_token = ['Traditionally', ',', 'black', 'Black', 'Asians', 'Blacks', 'blacks', 'bame', 'a', 'text', 'is',
                        'BAME', 'Asian', 'BAME', 'Asian', 'BAME', 'Asian', 'BAME', 'Asian', 'understood', 'minority',
                        ',', 'asian', 'to', 'be', 'a', ',' 'piece', 'of', 'written', 'or', 'spoken', 'material', '.',
                        'in', 'its', 'primary', 'form', '(', 'as', 'opposed', 'to', 'a', 'paraphrase', 'or']
        corpus_token_cleaned = ['traditionally', 'black', 'black', 'asians', 'blacks', 'blacks', 'bame', 'a', 'text',
                                'is',
                                'bame', 'asian', 'bAME', 'asian', 'bAME', 'asian', 'bame', 'asian', 'understood',
                                'minority',
                                'asian', 'to', 'be', 'a', 'piece', 'of', 'written', 'or', 'spoken', 'material', 'in',
                                'its',
                                'primary', 'form', '(', 'as', 'opposed', 'to', 'a', 'paraphrase', 'or']

        pivot_token = ['minority']
        target_token = ['asian']
        result = find_concordance(pivot_token, target_token, (3, 3), (1, 10), corpus_token, corpus_token_cleaned, True,
                                  True, True)

        expected_line = 'Asian BAME Asian understood minority , asian to be a ,piece of written or spoken material .'
        expected_left_line = 'BAME Asian understood'
        expected_left_context = 'Asian'
        expected_right_line = ', asian to be'
        expected_right_context = 'a ,piece of written or spoken material .'
        expected_query = 'minority'
        assert expected_line == result[0].line
        assert expected_left_context == result[0].left_context
        assert expected_left_line == result[0].left_span
        assert expected_query == result[0].query
        assert expected_right_line == result[0].right_span
        assert expected_right_context == result[0].right_context

    def test_concordance_list_5(self):
        corpus_token = ['Hi','!', 'I', 'am', 'black', 'and', 'I', 'am', 'going', 'to', 'get', 'the', 'vaccine', 'next',
                        'week', '.', 'Black', 'and', 'vaccine', '=', 'love', '.', 'That', 'is', 'all', 'I', 'am',
                        'going', 'to', 'say', '!']
        corpus_token_cleaned = ['Hi', 'I', 'am', 'black', 'and', 'I', 'am', 'going', 'to', 'get', 'the', 'vaccine',
                                'next', 'week', 'Black', 'and', 'vaccine', 'love', 'That', 'is', 'all', 'I', 'am',
                                'going', 'to', 'say']

        pivot_token = ['vaccine']
        target_token = ['Black']
        result = find_concordance(pivot_token, target_token, (100, 100), (2, 2), corpus_token, corpus_token_cleaned, True,
                                  True, False)

        expected_line = ' Hi ! I am black and I am going to get the vaccine next week .  '
        expected_left_line = 'Hi ! I am black and I am going to get the'
        expected_left_context = ''
        expected_right_line = 'next week .'
        expected_right_context = ' '
        expected_query = 'vaccine'
        assert expected_line == result[0].line
        assert expected_left_context == result[0].left_context
        assert expected_left_line == result[0].left_span
        assert expected_query == result[0].query
        assert expected_right_line == result[0].right_span
        assert expected_right_context == result[0].right_context

    def test_concordance_list_6(self):

            corpus_token = ['Hi','!', 'I', 'am', 'black', 'and', 'I', 'am', 'going', 'to', 'get', 'the', 'vaccine', 'next',
                            'week', '.', 'Black', 'and', 'vaccine', '=', 'love', '.', 'That', 'is', 'all', 'I', 'am',
                            'going', 'to', 'say', '!']
            corpus_token_cleaned = ['Hi', 'I', 'am', 'black', 'and', 'I', 'am', 'going', 'to', 'get', 'the', 'vaccine',
                                    'next', 'week', 'Black', 'and', 'vaccine', 'love', 'That', 'is', 'all', 'I', 'am',
                                    'going', 'to', 'say']

            pivot_token = ['vaccine']
            target_token = ['black']
            result = find_concordance(pivot_token, target_token, (10, 3), (100, 100), corpus_token, corpus_token_cleaned, True,
                                      False, False)

            expected_line = 'Hi ! I am black and I am going to get the vaccine next week . Black and vaccine = love . That is all I am going to say !'
            expected_left_line = 'I am black and I am going to get the'
            expected_left_context = 'Hi !'
            expected_right_line = 'next week . Black'
            expected_right_context = 'and vaccine = love . That is all I am going to say !'
            expected_query = 'vaccine'
            assert expected_line == result[0].line
            assert expected_left_context == result[0].left_context
            assert expected_left_line == result[0].left_span
            assert expected_query == result[0].query
            assert expected_right_line == result[0].right_span
            assert expected_right_context == result[0].right_context

    def test_concordance_list_6(self):

            corpus_token = ['There', 'have', 'been', '20', 'presidents', 'of', 'the', 'University', 'of', 'Illinois', 'system', ',', 'a', 'system', 'of', 'public', 'universities', 'in', 'the', 'U', '.', 'S', '.', 'state', 'of', 'Illinois', '.', 'The', 'president', 'is', 'the', 'chief', 'executive', 'officer', 'and', 'a', 'faculty', 'member', 'of', 'each', 'of', 'its', 'colleges', ',', 'schools', ',', 'institutions', ',', 'and', 'divisions', '.', 'Elected', 'by', 'the', 'board', 'of', 'trustees', ',', 'the', 'president', 'is', 'responsible', 'to', 'them', 'for', 'the', 'operation', 'of', 'the', 'system', 'by', 'preparing', 'budgets', ',', 'recommending', 'persons', 'for', 'appointment', 'to', 'university', 'positions', ',', 'and', 'enforcing', 'of', 'the', 'rules', 'and', 'regulations', 'of', 'the', 'universities', '.', 'Following', 'the', 'establishment', 'of', 'the', 'office', 'in', '1867', ',', 'John', 'Milton', 'Gregory', 'served', 'as', 'the', 'first', 'president', ',', 'originally', 'titled', '&', 'quot', ';', 'regent', '&', 'quot', ';', '.', 'Three', 'presidents', ',', 'Lloyd', 'Morey', ',', 'James', 'J', '.', 'Stukel', ',', 'and', 'Robert', 'A', '.', 'Easter', ',', 'are', 'alumni', 'of', 'the', 'University', 'of', 'Illinois', 'Urbana', '-', 'Champaign', '.', 'The', 'current', 'president', 'is', 'Timothy', 'L', '.', 'Killeen', ',', 'who', 'has', 'held', 'the', 'position', 'since', '2015', '.']
            corpus_token_cleaned = ['There', 'have', 'been', '20', 'presidents', 'of', 'the', 'University', 'of', 'Illinois', 'system', 'a', 'system', 'of', 'public', 'universities', 'in', 'the', 'U',  'S',  'state', 'of', 'Illinois', 'The', 'president', 'is', 'the', 'chief', 'executive', 'officer', 'and', 'a', 'faculty', 'member', 'of', 'each', 'of', 'its', 'colleges','schools', 'institutions', 'and', 'divisions','Elected', 'by', 'the', 'board', 'of', 'trustees', 'the', 'president', 'is', 'responsible', 'to', 'them', 'for', 'the', 'operation', 'of', 'the', 'system', 'by', 'preparing', 'budgets', 'recommending', 'persons', 'for', 'appointment', 'to', 'university', 'positions', 'and', 'enforcing', 'of', 'the', 'rules', 'and', 'regulations', 'of', 'the', 'universities', 'Following', 'the', 'establishment', 'of', 'the', 'office', 'in', '1867', 'John', 'Milton', 'Gregory', 'served', 'as', 'the', 'first', 'president', 'originally', 'titled', 'quot',  'regent', 'quot','Three', 'presidents','Lloyd', 'Morey', 'James', 'J', 'Stukel','and', 'Robert', 'A', 'Easter', 'are', 'alumni', 'of', 'the', 'University', 'of', 'Illinois', 'Urbana', 'Champaign', 'The', 'current', 'president', 'is', 'Timothy', 'L','Killeen', 'who', 'has', 'held', 'the', 'position', 'since', '2015']

            pivot_token = ['University']
            target_token = ['Illinois']
            result = find_concordance(pivot_token, target_token, (10, 3), (1, 2), corpus_token, corpus_token_cleaned,corpus_token_cleaned, True,
                                      False, False)

            expected_line = ' There have been 20 presidents of the University of Illinois system , a system'
            expected_left_line = 'There have been 20 presidents of the'
            expected_left_context = ''
            expected_right_line = 'of Illinois system ,'
            expected_right_context = 'a system'
            expected_query = 'University'
            assert expected_line == result[0].line
            assert expected_left_context == result[0].left_context
            assert expected_left_line == result[0].left_span
            assert expected_query == result[0].query
            assert expected_right_line == result[0].right_span
            assert expected_right_context == result[0].right_context


