
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
Tests for mamba.web.websocket
"""

import hashlib

from twisted.trial import unittest
from twisted.internet import address, task
from twisted.web.http import datetimeToString
from twisted.test import test_policies, proto_helpers

from mamba.web import websocket

data = (
    'GET /chat HTTP/1.1\r\n'
    'Host: server.example.com\r\n'
    'Upgrade: websocket\r\n'
    'Connection: Upgrade\r\n'
    'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n'
    'Origin: http://example.com\r\n'
    'Sec-WebSocket-Protocol: chat, superchat\r\n'
    'Sec-WebSocket-Version: 13\r\n\r\n'
)

hybi00_data = (
    'GET /demo HTTP/1.1\r\n'
    'Host: example.com\r\n'
    'Connection: Upgrade\r\n'
    'Sec-WebSocket-Key2: 12998 5 Y3 1  .P00\r\n'
    'Sec-WebSocket-Protocol: sample\r\n'
    'Upgrade: WebSocket\r\n'
    'Sec-WebSocket-Key1: 4 @1  46546xW%0l 1 5\r\n'
    'Origin: http://example.com\r\n'
    '\r\n'
    '^n:ds[4U\r\n\r\n'
)


class WebSocketProtocolTest(unittest.TestCase):
    """Test cases for Mamba WebSockets
    """

    def setUp(self):

        self.server = test_policies.Server()
        tServer = TestableWebSocketFactory(task.Clock(), self.server)
        self.port = tServer.buildProtocol(
            address.IPv4Address('TCP', '127.0..0.1', 0))
        self.tr = proto_helpers.StringTransportWithDisconnection()
        self.tr.protocol = self.port
        self.port.makeConnection(self.tr)
        self.port.producer = self.port.wrappedProtocol

    def tearDown(self):
        del self.server
        del self.port
        del self.tr

    def test_parse_headers(self):

        self.port.dataReceived(data)
        self.assertEqual(len(self.port.headers), 7)
        self.assertEqual(self.port.headers['Host'], 'server.example.com')
        self.assertEqual(self.port.headers['Upgrade'], 'websocket')
        self.assertEqual(self.port.headers['Origin'], 'http://example.com')
        self.assertEqual(
            self.port.headers['Sec-WebSocket-Key'], 'dGhlIHNhbXBsZSBub25jZQ==')
        self.assertEqual(
            self.port.headers['Sec-WebSocket-Protocol'], 'chat, superchat')

    def test_websocket_protocol(self):

        self.port.dataReceived(data)
        self.assertEqual(
            self.tr.value(),
            'HTTP/1.1 101 FYI I am not a webserver\r\n'
            'Server: MambaWebSocketWrapper/1.0\r\n'
            'Date: {}\r\n'
            'Upgrade: WebSocket\r\n'
            'Connection: Upgrade\r\n'
            'Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo='
            '\r\n\r\n'.format(datetimeToString())
        )

    def test_returned_key_for_rfc(self):

        self.port.dataReceived(data)
        key = self.tr.value().split('Sec-WebSocket-Accept: ')[1].strip()
        self.assertEqual(
            key,
            hashlib.sha1(
                'dGhlIHNhbXBsZSBub25jZQ==258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
            ).digest().encode('base64').strip()
        )

    def test_websocket_protocol_version_hybi00(self):

        self.port.dataReceived(hybi00_data)
        self.assertEqual(
            self.tr.value(),
            'HTTP/1.1 101 FYI I am not a webserver\r\n'
            'Server: MambaWebSocketWrapper/1.0\r\n'
            'Date: {}\r\n'
            'Upgrade: WebSocket\r\n'
            'Connection: Upgrade\r\n'
            'Sec-WebSocket-Origin: http://example.com\r\n'
            'Sec-WebSocket-Location: ws://example.com/demo\r\n'
            'Sec-WebSocket-Protocol: sample\r\n'
            "8jKS'y:G*Co,Wxa-".format(datetimeToString())
        )

    def test_invalid_protocol_version_preamble(self):

        tmp_data = data.split('\r\n')[:-3]
        tmp_data = '\r\n'.join(tmp_data)
        tmp_data += '\r\nSec-WebSocket-Version: 29\r\n\r\n'

        self.port.dataReceived(tmp_data)
        self.assertEqual(
            self.tr.value(),
            'HTTP/1.1 400 Bad RequestServer: MambaWebSocketWrapper/1.0\r\n'
            'Date: {}\r\n'
            'Upgrade: WebSocket\r\n'
            'Connection: Upgrade\r\n'
            'Sec-WebSocket-Version: 13\r\n'
            'Sec-WebSocket-Version: 8, 7\r\n'.format(datetimeToString())
        )

    def test_returned_key_for_hybi00(self):
        from string import digits
        from struct import pack
        from hashlib import md5

        key1 = '4 @1  46546xW\%0l 1 5'
        key2 = '12998 5 Y3 1  .P00'
        challenge = '^n:ds[4U'

        first = int(''.join(i for i in key1 if i in digits)) / key1.count(' ')
        second = int(''.join(i for i in key2 if i in digits)) / key2.count(' ')

        nonce = pack('>II8s', first, second, challenge)

        self.port.dataReceived(hybi00_data)
        self.assertTrue(md5(nonce).digest() in self.tr.value())

    def test_generate_hybi00frame(self):

        frame = websocket.HyBi00Frame('LEMOOOOOOOOOON')
        self.assertEqual(frame.generate(), '\x00LEMOOOOOOOOOON\xff')

    def test_generate_rfc6455frame(self):

        frame = websocket.HyBi07Frame('LEMOOOOOOOOOON')
        self.assertEqual(frame.generate(), '\x81\x0eLEMOOOOOOOOOON')

    def test_parse_hybi00frame(self):

        frame = websocket.HyBi00Frame('\x00LEMOOOOOOOOOON\xff')
        self.assertEqual(frame.parse()[0][0][1], 'LEMOOOOOOOOOON')

    def test_generate_invalid_hybi00frame(self):

        frame = websocket.HyBi00Frame('\x00LEMOOOOOOO\xffOOON')
        self.assertRaises(
            websocket.InvalidCharacterInHyBi00Frame,
            frame.generate
        )

    def test_parse_rfc6455frame(self):

        frame = websocket.HyBi07Frame('\x81\x0eLEMOOOOOOOOOON')
        self.assertEqual(frame.parse()[0][0][1], 'LEMOOOOOOOOOON')

    def test_mask_noop(self):
        key = '\x00\x00\x00\x00'
        self.assertEqual(
            websocket.HyBi07Frame('').mask('LEMOOOOOOOOOON', key),
            'LEMOOOOOOOOOON'
        )

    def test_unmasked_text(self):

        parser = websocket.HyBi07Frame('\x81\x0eLEMOOOOOOOOOON')
        fr, buf = parser.parse()
        self.assertEqual(len(fr), 1)
        self.assertEqual(fr[0], (websocket.DATA, 'LEMOOOOOOOOOON'))
        self.assertEqual(buf, '')

    def test_masked_text(self):

        key = '\x0a\x45\x34\x1a'
        lemon = 'F\x00yUE\n{UE\n{UE\x0b'
        parser = websocket.HyBi07Frame('\x81\x8e{}{}'.format(key, lemon))
        fr, buf = parser.parse()
        self.assertEqual(len(fr), 1)
        self.assertEqual(fr[0], (websocket.DATA, 'LEMOOOOOOOOOON'))

    def test_unmasked_text_fragments(self):

        parser = websocket.HyBi07Frame('\x81\x08LEMOOOOO\x80\x06OOOOON')
        fr, buf = parser.parse()
        self.assertEqual(len(fr), 2)
        self.assertEqual(fr[0], (websocket.DATA, "LEMOOOOO"))
        self.assertEqual(fr[1], (websocket.DATA, "OOOOON"))
        self.assertEqual(buf, '')

    def test_parse_ping(self):

        fr, buf = websocket.HyBi07Frame('\x89\x0eLEMOOOOOOOOOON').parse()
        self.assertEqual(len(fr), 1)
        self.assertEqual(fr[0], (websocket.PING, "LEMOOOOOOOOOON"))
        self.assertEqual(buf, '')

    def test_parse_pong(self):

        fr, buf = websocket.HyBi07Frame('\x8a\x0eLEMOOOOOOOOOON').parse()
        self.assertEqual(len(fr), 1)
        self.assertEqual(fr[0], (websocket.PONG, "LEMOOOOOOOOOON"))
        self.assertEqual(buf, '')

    def test_parse_close_empty(self):

        fr, buf = websocket.HyBi07Frame('\x88\x00').parse()
        self.assertEqual(len(fr), 1)
        self.assertEqual(fr[0], (websocket.CLOSE, (1000, 'No reason given')))
        self.assertEqual(buf, '')

    def test_parse_close_reason(self):

        frame = '\x88\x10\x03\xe8LEMOOOOOOOOOON'
        fr, buf = websocket.HyBi07Frame(frame).parse()
        self.assertEqual(len(fr), 1)
        self.assertEqual(fr[0], (websocket.CLOSE, (1000, 'LEMOOOOOOOOOON')))
        self.assertEqual(buf, '')

    def test_parse_partial_no_length(self):

        fr, buf = websocket.HyBi07Frame('\x81').parse()
        self.assertEqual(len(fr), 0)
        self.assertEqual(buf, '\x81')

    def test_parse_partial_truncated_length_int(self):

        fr, buf = websocket.HyBi07Frame('\x81\xfe').parse()
        self.assertEqual(len(fr), 0)
        self.assertEqual(buf, '\x81\xfe')

    def test_parse_partial_truncated_length_double(self):

        fr, buf = websocket.HyBi07Frame('\x81\xff').parse()
        self.assertEqual(len(fr), 0)
        self.assertEqual(buf, '\x81\xff')

    def test_parse_partial_no_data(self):

        fr, buf = websocket.HyBi07Frame('\x81\x05').parse()
        self.assertEqual(len(fr), 0)
        self.assertEqual(buf, '\x81\x05')

    def test_parse_partial_truncated_data(self):

        fr, buf = websocket.HyBi07Frame('\x81\x0eLEMOOOO').parse()
        self.assertEqual(len(fr), 0)
        self.assertEqual(buf, '\x81\x0eLEMOOOO')


class TestableWebSocketFactory(websocket.WebSocketFactory):
    """Just for tests purposes
    """

    def __init__(self, clock, *args, **kwargs):
        websocket.WebSocketFactory.__init__(self, *args, **kwargs)
        self.clock = clock

    def callLater(self, period, func):
        return self.clock.callLater(period, func)
