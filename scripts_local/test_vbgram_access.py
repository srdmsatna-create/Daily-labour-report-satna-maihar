import os
import unittest
import urllib.request
from unittest.mock import patch
from vbgram_access import session_opener, session_cookies

class SessionTests(unittest.TestCase):
    def attach(self, opener, url):
        request = urllib.request.Request(url)
        for handler in opener.handlers:
            if isinstance(handler, urllib.request.HTTPCookieProcessor):
                handler.cookiejar.add_cookie_header(request)
        return request.get_header('Cookie')

    def test_session_applies_only_to_official_https_host(self):
        with patch.dict(os.environ, {'VBGRAM_COOKIE': 'ASP.NET_SessionId=test-session'}):
            opener = session_opener()
        self.assertEqual(self.attach(opener, 'https://vbgramgrep.dord.gov.in/VBGRAMG/report.aspx'), 'ASP.NET_SessionId=test-session')
        for url in ('https://example.com/', 'https://mnregaweb4.dord.gov.in/', 'http://vbgramgrep.dord.gov.in/'):
            self.assertIsNone(self.attach(opener, url))

    def test_empty_session_keeps_public_fetch_available(self):
        with patch.dict(os.environ, {'VBGRAM_COOKIE': ''}):
            self.assertEqual(session_cookies(), [])
            self.assertIsNone(self.attach(session_opener(), 'https://vbgramgrep.dord.gov.in/'))

    def test_invalid_cookie_header_is_not_forwarded(self):
        with patch.dict(os.environ, {'VBGRAM_COOKIE': 'session=bad\r\nInjected: value'}):
            self.assertEqual(session_cookies(), [])

if __name__ == '__main__':
    unittest.main()
