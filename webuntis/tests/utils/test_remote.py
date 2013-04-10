import webuntis
import mock
from webuntis.utils.third_party import json
from webuntis.tests import WebUntisTestCase, StringIO

class BasicUsage(WebUntisTestCase):
    def test_parse_result(self):
        x = webuntis.utils.remote._parse_result

        a = {'id': 2}
        b = {'id': 3}
        self.assertRaisesRegex(webuntis.errors.RemoteError,
                               'Request ID', x, a, b)

        a = b = {'id': 2}
        self.assertRaisesRegex(webuntis.errors.RemoteError,
                               'JSON-RPC', x, a, b)

        a = {'id': 2}
        b = {'id': 2, 'result': 'YESSIR'}
        self.assertEqual(x(a, b), 'YESSIR')

    def test_parse_error_code(self):
        x = webuntis.utils.remote._parse_error_code

        a = b = {}
        self.assertRaisesRegex(webuntis.errors.RemoteError,
                               'JSON-RPC', x, a, b)

        b = {'error': {'code': 0, 'message': 'hello'}}
        self.assertRaisesRegex(webuntis.errors.RemoteError,
                               'JSON-RPC', x, a, b)

        for code, exc in webuntis.utils.remote._errorcodes.items():
            self.assertRaises(exc, x, a, {
                'error': {'code': code, 'message': 'hello'}
            })

    def test_send_request(self):
        self.request_patcher.stop()
        x = webuntis.utils.remote._send_request 

        endpoint = 'http://example.com/endpoint'
        data = {'method': 'getFoo', 'params': {'actually': 'nope'}}
        headers = {'x-foobar': 'HAHA'}

        rv = {'result': 'HOIHOI'}
        enc_rv = json.dumps(rv)

        def cb(req):
            assert req.get_full_url() == endpoint
            assert json.loads(req.data) == data
            h = dict((k.lower(), v) for k, v in req.header_items())
            assert h == headers

            return StringIO(enc_rv)

        with mock.patch('webuntis.utils.third_party.urlrequest.urlopen', new=cb):
            assert x(endpoint, data, headers) == rv
            enc_rv = 'alert("HELLO");'

            self.assertRaisesRegex(webuntis.errors.RemoteError, 'JSON', x, endpoint, data, headers)