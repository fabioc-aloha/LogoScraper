"""Unit tests for utils.url_utils domain cleaning functions."""
import unittest
from utils.url_utils import clean_domain, get_domain_from_url

class TestUrlUtils(unittest.TestCase):
    def test_clean_domain_basic(self):
        self.assertEqual(clean_domain('www.example.com'), 'example.com')
        self.assertEqual(clean_domain('EXAMPLE.COM'), 'example.com')
        self.assertEqual(clean_domain(' example.com '), 'example.com')
        self.assertEqual(clean_domain('www.example.com.'), 'example.com')
        self.assertEqual(clean_domain('www.-example-.com-'), 'example-.com')

    def test_clean_domain_unwanted_chars(self):
        self.assertEqual(clean_domain('www.example.com,'), 'example.com')
        self.assertEqual(clean_domain('www.example.com;'), 'example.com')
        self.assertEqual(clean_domain('www.example.com/'), 'example.com')
        self.assertEqual(clean_domain('www.example.com\\'), 'example.com')
        self.assertEqual(clean_domain('www.example.com"'), 'example.com')
        self.assertEqual(clean_domain('www.example.com<'), 'example.com')
        self.assertEqual(clean_domain('www.example.com>'), 'example.com')
        self.assertEqual(clean_domain('www.example.com('), 'example.com')
        self.assertEqual(clean_domain('www.example.com)'), 'example.com')
        self.assertEqual(clean_domain('www.example.com[]'), 'example.com')

    def test_clean_domain_multiple_domains(self):
        self.assertEqual(clean_domain('www.example.com,foo.com'), 'example.com')
        self.assertEqual(clean_domain('www.example.com;foo.com'), 'example.com')
        self.assertEqual(clean_domain('www.example.com/foo.com'), 'example.com')
        self.assertEqual(clean_domain('www.example.com\\foo.com'), 'example.com')
        self.assertEqual(clean_domain('www.example.com foo.com'), 'example.com')

    def test_clean_domain_at_and_strip(self):
        self.assertEqual(clean_domain('user@example.com'), 'example.com')
        self.assertEqual(clean_domain('user@www.example.com'), 'example.com')
        self.assertEqual(clean_domain('user@www.example.com,foo.com'), 'example.com')
        self.assertEqual(clean_domain('user@www.example.com;foo.com'), 'example.com')

    def test_clean_domain_leading_trailing(self):
        self.assertEqual(clean_domain('.example.com.'), 'example.com')
        self.assertEqual(clean_domain('-example.com-'), 'example.com')
        self.assertEqual(clean_domain('...-example.com-...'), 'example.com')

    def test_get_domain_from_url(self):
        self.assertEqual(get_domain_from_url('https://www.example.com'), 'example.com')
        self.assertEqual(get_domain_from_url('http://example.com:8080'), 'example.com')
        self.assertEqual(get_domain_from_url('https://user@www.example.com/path'), 'example.com')
        self.assertEqual(get_domain_from_url('www.example.com'), 'example.com')
        self.assertEqual(get_domain_from_url('example.com'), 'example.com')
        self.assertEqual(get_domain_from_url('user@www.example.com,foo.com'), 'example.com')
        self.assertEqual(get_domain_from_url(''), None)
        self.assertEqual(get_domain_from_url(None), None)

if __name__ == '__main__':
    unittest.main()
