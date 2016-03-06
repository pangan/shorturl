from unittest import TestCase
from collections import Counter

from ..tools.make_wordlist import cleanup_wordlist


class ToolsTestCases(TestCase):
    """
    To run :
       nosetests -v
    """

    def test_cleanup_word_list(self):
        """Test clean up word list
        """

        for item in cleanup_wordlist(['A$%"B23',' ']):
            self.assertIsInstance(item, tuple)
            self.assertRegexpMatches(item[0], '^[a-z0-9]*$')




    def test_unique_words_in_list(self):
        """Test unique words in the word list
        """
        words_count = Counter(cleanup_wordlist(['aa','aa','bb','bb'])).values()
        for item in words_count:
            self.assertEqual(item,1)