"""Reuse an explicitly supplied portal session without exposing it in logs."""
import http.cookiejar
import os
import urllib.error
import urllib.request

HOST = 'vbgramgrep.dord.gov.in'

def session_cookies():
    result = []
    for pair in os.environ.get('VBGRAM_COOKIE', '').split(';'):
        if '=' not in pair:
            continue
        name, value = pair.strip().split('=', 1)
        if name and not any(c in name + value for c in '\r\n'):
            result.append({'name': name, 'value': value, 'domain': HOST,
                           'path': '/', 'secure': True})
    return result

def _build_opener(include_supplied=True):
    jar = http.cookiejar.CookieJar()
    for item in session_cookies() if include_supplied else []:
        jar.set_cookie(http.cookiejar.Cookie(
            version=0, name=item['name'], value=item['value'], port=None,
            port_specified=False, domain=HOST, domain_specified=False,
            domain_initial_dot=False, path='/', path_specified=True,
            secure=True, expires=None, discard=True, comment=None,
            comment_url=None, rest={}, rfc2109=False))
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

class PortalOpener:
    """Use the configured cookie, but recover when a stale cookie blocks a public signed URL."""
    def __init__(self):
        self._has_supplied = bool(session_cookies())
        self._anonymous_retry_used = False
        self._opener = _build_opener(include_supplied=True)

    @property
    def handlers(self):
        return self._opener.handlers

    def open(self, request, *args, **kwargs):
        try:
            return self._opener.open(request, *args, **kwargs)
        except urllib.error.HTTPError as error:
            # Signed public reports sometimes reject an expired ASP.NET cookie even
            # though the same URL is readable in a fresh anonymous session. Retry
            # only the initial GET once; never replay a POST without its session.
            method = request.get_method() if hasattr(request, 'get_method') else 'GET'
            if (error.code in (401, 403) and self._has_supplied and
                    not self._anonymous_retry_used and method == 'GET'):
                self._anonymous_retry_used = True
                self._opener = _build_opener(include_supplied=False)
                return self._opener.open(request, *args, **kwargs)
            raise

def session_opener():
    return PortalOpener()

_OPENER = None

def open_url(request, timeout=90):
    global _OPENER
    if _OPENER is None:
        _OPENER = session_opener()
    try:
        return _OPENER.open(request, timeout=timeout)
    except urllib.error.HTTPError as error:
        if error.code in (401, 403):
            # Do not log signed URLs, response bodies or session values.
            raise RuntimeError('Portal access refused (HTTP %s); report retained. '
                               'A working portal connection/session is required.' % error.code) from None
        raise
