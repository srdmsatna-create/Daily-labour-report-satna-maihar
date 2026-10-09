import unittest
from unittest.mock import Mock, patch
import requests
import update_yuktdhara_monitoring as report

class ConnectionTests(unittest.TestCase):
    url=report.BHUVAN_INDEX
    def test_transient_timeout_recovers(self):
        response=Mock(status_code=200,text='official table')
        with patch.object(report.BHUVAN_SESSION,'get',side_effect=[requests.ConnectTimeout(),response]) as get, patch.object(report.time,'sleep'):
            self.assertEqual(report.get_text(self.url),'official table')
            self.assertEqual(get.call_count,2)
            self.assertEqual(get.call_args.kwargs['timeout'],(15,90))
    def test_repeated_timeout_fails_without_success(self):
        with patch.object(report.BHUVAN_SESSION,'get',side_effect=requests.ConnectTimeout()) as get, patch.object(report.time,'sleep'):
            with self.assertRaisesRegex(RuntimeError,'after 3 attempts'):
                report.get_text(self.url)
            self.assertEqual(get.call_count,3)
    def test_auth_denial_is_not_retried(self):
        response=Mock(status_code=401)
        response.raise_for_status.side_effect=requests.HTTPError('401')
        with patch.object(report.BHUVAN_SESSION,'get',return_value=response) as get:
            with self.assertRaises(requests.HTTPError):report.get_text(self.url)
            self.assertEqual(get.call_count,1)
    def test_unexpected_host_is_rejected(self):
        with patch.object(report.BHUVAN_SESSION,'get') as get:
            with self.assertRaisesRegex(RuntimeError,'Unexpected'):report.get_text('https://example.com/report')
            get.assert_not_called()

if __name__=='__main__':unittest.main()
