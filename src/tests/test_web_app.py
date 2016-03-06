import sqlite3

from unittest import TestCase

from ..shorturl.webapp.views import assign_word_to_url, get_original_url, get_unused_word
from ..shorturl.webapp import _settings


class WebAppFunctionsTestCase(TestCase):
    """
    To Run:
       nosetests -v
    """
    def _creat_test_dbase(self):
        conn = sqlite3.connect('test.db')
        wordslist = [
            ("google",None),
            ("empty",None),
            ("hello", "http://www.hello.com")
        ]
        conn.execute('''DROP TABLE IF EXISTS wordlist;
            '''
            )
        conn.execute('''CREATE TABLE wordlist
                           (WORD TEXT PRIMARY KEY   NOT NULL,
                            URL TEXT,
                            TIME_STAMP NUMBER
                           );
            ''')
        conn.executemany("INSERT INTO wordlist ('WORD','URL') VALUES (?,?)", wordslist)
        conn.commit()

    def setUp(self):

        _settings.WORDS_DATABASE='test.db'


    def test_assign_word_to_url(self):
        """Test assign word to URL


        * Scopes:

        + Assigned words should be in a correct format
        """
        self._creat_test_dbase()
        self.assertRegexpMatches(
            assign_word_to_url("http://www.google.com"),
            '^[a-z0-9]*$')
        self.assertRegexpMatches(
            assign_word_to_url("http://www.nothing.com"),
            '^[a-z0-9]*$')


    def test_get_original_url(self):
        """Test get original URL


        * Scopes

        + If a used word is requested it should return a valid URL
        """
        self._creat_test_dbase()
        urlRegex = '^(?:(?:http|https)://)' \
                   '(?:\\S+(?::\\S*)?@)?(?:(?:(?:[1-9]\\d?|1\\d\\d|2[01]\\d|22[0-3])' \
                   '(?:\\.(?:1?\\d{1,2}|2[0-4]\\d|25[0-5]))' \
                   '{2}(?:\\.(?:[0-9]\\d?|1\\d\\d|2[0-4]\\d|25[0-4]))|(?:(?:[a-z\\u00a1-\\uffff0-9]+-?)*' \
                   '[a-z\\u00a1-\\uffff0-9]+)(?:\\.(?:[a-z\\u00a1-\\uffff0-9]+-?)*[a-z\\u00a1-\\uffff0-9]+)*' \
                   '(?:\\.(?:[a-z\\u00a1-\\uffff]{2,})))|localhost)(?::\\d{2,5})?(?:(/|\\?|#)[^\\s]*)?$'
        self.assertRegexpMatches(
            get_original_url('hello'),
            urlRegex)

    def test_get_original_url_with_invalid_word(self):
        """Test get original url with an invalid word


        * Scopes:

        + Function should return None if an invalid word is required

        + Function should return None if an unused word is required

        """
        self._creat_test_dbase()
        self.assertEqual(
            get_original_url('invalid_word'),
            None
        )
        self.assertEqual(get_original_url('empty'),
                         None)

    def test_get_unused_word(self):
        """Test get unused word function

        * Scopes:

        + Should return correct word that includes in url

        + Should return same word for an exist url

        + Should use an unused word if the word is used before

        + Should use the eldest word if can not find an unused word

        """
        self._creat_test_dbase()
        self.assertEqual(get_unused_word("http://www.hello.com"),
                         "hello")
        assign_word_to_url("http://www.google.com")
        self.assertEqual(get_unused_word("http://www.google.com"),
                         "google")
        self.assertEqual(assign_word_to_url("http://test.google.com"),
                         "empty")
        assign_word_to_url("http://www.hello.com")
        self.assertEqual(assign_word_to_url("http://www.something.new"),
                         "google")


