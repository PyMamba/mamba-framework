# -*- test-case-name: mamba.test.test_websocket -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: websocket
    :platform: Unix, Windows
    :synopsis: Websocket mamba implementation. This module is inspired by
               MostAwesomeDude's work on txWS. txWS is Free Software, you
               can find it here: https://github.com/MostAwesomeDude/txWS

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

from string import digits
from hashlib import sha1, md5
from struct import pack, unpack

from twisted.python import log
from twisted.web.http import datetimeToString
from twisted.internet.interfaces import ISSLTransport
from twisted.protocols.policies import ProtocolWrapper, WrappingFactory

DATA, CLOSE, PING, PONG = range(4)                    # frame control
HYBI00, HYBI07, HYBI10, RFC6455 = range(4)            # supported versions
HANDSHAKE, NEGOTIATION, CHALLENGE, FRAMES = range(4)  # state machine.

NORMAL_CLOSURE = 0x3e8


class WebSocketError(Exception):
    """Fired when something went wrong
    """


class InvalidProtocol(WebSocketError):
    """Fired when the client send something that is not WebSocket protocol
    """


class NoWebSocketCodec(WebSocketError):
    """Fired when we can't handle the codec (WS protocol)
    """


class InvalidProtocolVersion(WebSocketError):
    """Fired when the protocol version is not supported
    """


class InvalidCharacterInHyBi00Frame(WebSocketError):
    """Fired when a xff charecter is found in HyBi-00/Hixie-76 frame buffer
    """


class ReservedFlagsInFrame(WebSocketError):
    """Fired when any of the three reserved bits of HyBi-07 are set on
    """


class UnknownFrameOpcode(WebSocketError):
    """Fired when we get an unused RFC6455 frame opcode
    """


class HandshakePreamble(object):
    """Common HandShake preamble class for all protocols
    """

    def __init__(self):
        self.data = [
            'HTTP/1.1 101 FYI I am not a webserver\r\n',
            'Server: MambaWebSocketWrapper/1.0\r\n',
            'Date: {}\r\n'.format(datetimeToString()),
            'Upgrade: WebSocket\r\n',
            'Connection: Upgrade\r\n'
        ]

    def write_to_transport(self, transport):
        """Write data to the wrapped transport

        :param transport: the underlying transport
        """

        assert(transport is not None)
        transport.writeSequence(self.data)


class HyBi00HandshakePreamble(HandshakePreamble):
    """HyBi-00 preamble
    """

    def __init__(self, protocol):
        super(HyBi00HandshakePreamble, self).__init__()
        protocols = ','.join(protocol.protocols)
        self.data += [
            'Sec-WebSocket-Origin: {}\r\n'.format(protocol.origin),
            'Sec-WebSocket-Location: {}://{}{}\r\n'.format(
                'wss' if protocol.secure is True else 'ws',
                protocol.host,
                protocol.location
            ),
            'Sec-WebSocket-Protocol: {}\r\n'.format(protocols)
        ]

    def write_to_transport(self, transport, response):
        """Write data to the wrapped transport and add a hibi00 auth response

        :param transport: the underlying transport
        :param response: the generated HyBi-00/Hixie-76 response
        """

        super(HyBi00HandshakePreamble, self).write_to_transport(transport)
        transport.write(response)


class HyBi07HandshakePreamble(HandshakePreamble):
    """HyBi-07 preamble
    """

    def __init__(self, protocol):
        super(HyBi07HandshakePreamble, self).__init__()
        self.data += self.generate_accept_opening(protocol)

    def generate_accept_opening(self, protocol):
        """Generates the accept response for a given key.

        Concatenates the `Sec-WebSocket-Key` given by the client with the
        string 258EAFA5-E914-47DA-95CA-C5AB0DC85B11 to form a response that
        proves the handshake was received by the server by taking the SHA-1
        hash of this encoding it to base64 and echoing back to the client.

        Refer to [RFC6455][Page 7] for more details.
        """

        key = '{}{}'.format(
            protocol.headers['Sec-WebSocket-Key'],
            '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        )

        return [
            'Sec-WebSocket-Accept: {}\r\n\r\n'.format(
                sha1(key).digest().encode('base64').strip()
            )
        ]


class InvalidProtocolVersionPreamble(HandshakePreamble):
    """Send invalid protocol version response
    """

    def __init__(self):
        super(InvalidProtocolVersionPreamble, self).__init__()
        self.data[0] = 'HTTP/1.1 400 Bad Request'
        self.data += [
            'Sec-WebSocket-Version: 13\r\n',
            'Sec-WebSocket-Version: 8, 7\r\n'
        ]


class HyBi00Frame(object):
    """A WebSocket HyBi-00 frame object representation

    .. sourcecode:: text

        Frame type byte <--------------------------------------.
            |      |                                            |
            |      `--> (0x00 to 0x7F) --> Data... --> 0xFF -->-+
            |                                                   |
            `--> (0x80 to 0xFE) --> Length --> Data... ------->-'

    The implementation of this protocol is really simple, in
    HyBi-00/Hixie-76 only 0x00-0xFF is valid so we use 0x00 always
    as opcode and then put the buffer between the opcode and the
    last 0xFF.

    Only 0x00 to 0xFE values are allowed in the buffer (because
    the 0xFF is used mark for the end of the buffer).

    For more information about this read [HyBi-00/Hixie-76][Page 6]

    :param buf: the buffer data
    """

    def __init__(self, buf):
        self.buf = buf

    @property
    def is_valid(self):
        """Check if the buffer is valid (no xff characters on it)
        """

        for ch in self.buf:
            if ord(ch) == 0xff:
                return False

        return True

    def generate(self, opcode=0x00):
        """Generate a HyBi-00/Hixie-76 frame.
        """

        if self.is_valid:
            return '\x00{buf}\xff'.format(buf=self.buf)

        raise InvalidCharacterInHyBi00Frame(
            'Invalid character \xff in HyBi-00/Hixie-76'
        )

    def parse(self):
        """Parse a HyBi-00/Hixie-76 frame.
        """

        start = self.buf.find("\x00")
        tail = 0
        frames = []

        while start != -1:
            end = self.buf.find('\xff', start + 1)
            if end == -1:
                # the frame is not complete yet, tey again later
                break
            else:
                # new frame found append it to the list
                frame = self.buf[start + 1:end]  # read from 0x00 to 0xff
                frames.append((DATA, frame))
                tail = end + 1

            start = self.buf.find('\x00', end + 1)

        # adjust the buffer and return the parsed frames
        self.buf = self.buf[tail:]
        return frames, self.buf


class HyBi07Frame(object):
    """A WebSocket HiBi-07+ frame object representation

    .. sourcecode:: text

         0                   1                   2                   3
         0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
        +-+-+-+-+-------+-+-------------+-------------------------------+
        |F|R|R|R| opcode|M| Payload len |    Extended payload length    |
        |I|S|S|S|  (4)  |A|     (7)     |             (16/64)           |
        |N|V|V|V|       |S|             |   (if payload len==126/127)   |
        | |1|2|3|       |K|             |                               |
        +-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
        |     Extended payload length continued, if payload len == 127  |
        + - - - - - - - - - - - - - - - +-------------------------------+
        |                               |Masking-key, if MASK set to 1  |
        +-------------------------------+-------------------------------+
        | Masking-key (continued)       |          Payload Data         |
        +-------------------------------- - - - - - - - - - - - - - - - +
        :                     Payload Data continued ...                :
        + - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +
        |                     Payload Data continued ...                |
        +---------------------------------------------------------------+

    For more information about WebSocket framing read [RFC6455][Section 5.2]

    :param buf: the buffer data
    """

    opcodes = {
        0x0: DATA,
        0x1: DATA,
        0x2: DATA,
        0x8: CLOSE,
        0x9: PING,
        0xa: PONG
    }

    def __init__(self, buf):
        self.buf = buf

    def generate(self, opcode=0x1):
        """
        Generate a HyBi-07+ frame.

        This function always creates unmasked frames, and attemps to use the
        smallest possible lengths.

        :param opcode: the opcode to use:
                           0x1 -> Text
                           0x2 -> Binary
        :type opcode: int
        """

        if len(self.buf) > 0xffff:
            length = '\x7f%s' % (pack('>Q', len(self.buf)),)
        elif len(self.buf) > 0x7d:
            length = '\x7e%s' % (pack('>H', len(self.buf)),)
        else:
            length = chr(len(self.buf))

        return '{header}{length}{buf}'.format(
            header=chr(0x80 | opcode), length=length, buf=self.buf
        )

    def parse(self):
        """Parse HyBi-07+ frame.
        """

        start = 0
        frames = []

        while True:
            # is there are not at least two bytes in the buffer, bail
            if len(self.buf) - start < 2:
                break

            # grab the header, this first byte of data contains FIN, RSV1-3
            # and the opcode
            header = ord(self.buf[start])
            fin = (header & 0x80) != 0
            if header & 0x70:
                # at least one of the reserved flags is set.
                # TODO: look at extensions to chekc if something is negotiated
                #       as is specified by [RFC6455][Page 28]
                # Someday, perhaps...
                raise ReservedFlagsInFrame(
                    'Reserved flag in HyBi-07 frame {}'.format(
                        '{:#x} ({:#b})'.format(header, header)
                    )
                )

            # get the opcode
            raw_opcode = header & 0xf
            opcode = self.opcodes.get(raw_opcode)
            if opcode is None:
                raise UnknownFrameOpcode(
                    'Unknown opcode {:#b} in HyBi-07 frame'.format(raw_opcode)
                )

            # get the mask flag and payload length from the next byte and
            # determine if we have to look for any extra length
            data = ord(self.buf[start + 1])
            masked = (data & 0x80) != 0  # most significant bit (should be 1)
            length = data & 0x7f

            # check opcodes for given frames
            if opcode >= CLOSE:
                # control frames shouldn't be fragmented
                if fin is False:
                    raise WebSocketError(
                        'Fragmented control frame with opcode {:#x}'.format(
                            raw_opcode
                        )
                    )

                # control frames shouldn't have more than 125 octects length
                if length > 0x7d:
                    raise WebSocketError(
                        'Control frame with payload longer than 125 octets, '
                        'opcode {:#b}'.format(raw_opcode)
                    )

                # opcodes 0xb to 0xf are reserved for further control frames
                if opcode > PONG:
                    raise WebSocketError(
                        'Control frame using reserved opcode {:#x}'.format(
                            raw_opcode
                        )
                    )
            else:
                # data frames can only use opcodes 0x0, 0x1 and 0x2
                if opcode != DATA:
                    raise WebSocketError(
                        'Data frame using weird opcode {:#x}'.format(
                            raw_opcode
                        )
                    )

            # the offset we're going to use to walk through the frame
            offset = 2

            # extra length fields. if the value is 126 then the following 2
            # bytes interpreted as 16-bit unsigned integer are the payload
            # length
            if length == 0x7e:
                if len(self.buf) - start < 4:
                    break

                # read the next two bytes (start + 2:start + 4) and unpack
                length = unpack('>H', self.buf[start + 2:start + 4])[0]
                offset += 2
            # if the value is 127 then the following 8 bytes interpreted as
            # a 64-bit unsigned integer are the payload length that is a
            # ridiculous big length of data but hey what the fuck I know
            elif length == 0x7f:
                if len(self.buf) - start < 10:
                    break

                # read the next eigth bytes (start +2:start +10) and unpack
                length = unpack('>Q', self.buff[start + 2:start + 10])[0]
                offset += 8

            # browser client is supossed to send all frames masked so this
            # should be always True
            if masked:
                if len(self.buf) - (start + offset) < 4:
                    break

                # get the mask key
                mask_key = self.buf[start + offset:start + offset + 4]
                offset += 4

            # get the payload data
            if len(self.buf) - (start + offset) < length:
                break

            payload_data = self.buf[start + offset:start + offset + length]

            if masked:
                payload_data = self.mask(payload_data, mask_key)

            if opcode == CLOSE:
                if len(payload_data) >= 2:
                    # unpack the opcode and return usable data
                    payload_data = (
                        unpack('>H', payload_data[:2])[0], payload_data[2:])
                else:
                    payload_data = NORMAL_CLOSURE, 'No reason given'

            frames.append((opcode, payload_data))
            start += offset + length

        return frames, self.buf[start:]

    def mask(self, buf, key):
        """Mask or unmask a buffer of bytes with a masking key

        The masking key is a 32-bit value chosen by the browser client. The
        key shouldn't affect the length of the `Payload data`. The used
        algorithm is the following. Octet i of the transformed data is the
        XOR of octet i of the original data with octet at index i modulo 4
        of the masking key::

            j = i % 4
            octet[i] = octet[i] ^ key[j]

        This means that if a third party have access to the key used by our
        connection we are exposed. For more information about this please,
        refer to [RFC6455][Page31]

        :param buf: the buffer to mask or unmask
        :param key: the masking key, it shoudl be exactly four bytes long
        """

        key = [ord(i) for i in key]
        buf = list(buf)

        for i in range(len(buf)):
            buf[i] = chr(ord(buf[i]) ^ key[i % 4])
        return ''.join(buf)


class WebSocketProtocol(ProtocolWrapper):
    """
    Wrapped protocol to handle Websockaet transport layer. Thw websocket
    protocol just wrap another protocol to provide a WebSocket transport.

    warning::
        This protocol is  not HTTP

    How to use it?::

        from twisted.internet import protocol

        from mamba.web import websocket

        class EchoFactory(protocol.Protocol):

            def dataReceived(self, data):
                # this is the websocket data frame
                self.transport.write(data)

        class EchoFactory(protocol.Factory):
            protocol = EchoProtocol


        reactor.listenTCP(6543, websocket.WebSocketFactory(EchoFactory()))


    """

    def __init__(self, *args, **kwargs):
        ProtocolWrapper.__init__(self, *args, **kwargs)
        self.buf = ''
        self.codec = None
        self.location = '/'
        self.host = ''
        self.origin = ''
        self.version = None
        self.state = HANDSHAKE
        self.pending_frames = []
        self.protocols = []
        self.headers = {}

    @property
    def secure(self):
        """
        Borrowed technique for determining whether this connection is
        over SSL/TLS
        """

        return ISSLTransport(self.transport, None) is not None

    @property
    def codecs(self):
        """Return the list of available codecs (WS protocols)
        """

        return ('base64',)

    @property
    def is_hybi00(self):
        """Determine whether a given set of headers are HyBi-00 compilant
        """

        return ('Sec-WebSocket-Key1' in self.headers
                and 'Sec-WebSocket-Key2' in self.headers)

    def dataReceived(self, data):
        """Protocol dataReceived

        If our state is HANDSHAKE then we capture the request path fo echo it
        back to those browsers that require it (Chrome mainly) and set our
        state to NEGOTIATION

        If our state is NEGOTIATION we look at the headers to check if we have
        one complete set. If we can't validate headers we just lose connection

        If out state is CHALLENGE we have to call authentication related code
        for protocol versions HyBi-00/Hixie-76. For more information refer to
        http://tools.ietf.org/html/draft-hixie-thewebsocketprotocol-76#page-5

        If our state is FRAMES then we parse it.

        We always kick any pending frames after each call to `dataReceived`.
        This is neccesary because frames might have started being sended early
        we can get write()s from our protocol above when they makeConnection()
        inmediately before the browser actually send any data. In those cases,
        we need to manually kick pending frames.
        """

        self.buf += data
        oldstate = None

        while oldstate != self.state:
            oldstate = self.state

            if self.state == HANDSHAKE:         # HANDSHAKE
                self.handle_handshake()
            elif self.state == NEGOTIATION:     # NEGOTIATION
                try:
                    self.handle_negotiation()
                except InvalidProtocolVersion:
                    preamble = InvalidProtocolVersionPreamble()
                    preamble.write_to_transport(self.transport)
                    self.close('Invalid Protocol Version')
                except (InvalidProtocol, NoWebSocketCodec) as error:
                    log.err(error)
                    self.loseConnection()
            elif self.state == CHALLENGE:       # CHALLEMGE
                self.handle_challenge()
            elif self.state == FRAMES:          # FRAMES
                self.handle_frames()

        # kick pending frames
        if len(self.pending_frames) > 0:
            self._send()

    def handle_handshake(self):
        """
        Handle initial request. These look very much like HTTP requests but
        aren't. We have to capture the request path to echo it back to the
        browsers that care about.

        These lines looks like::

            GET /some/path/to/a/websocket/resource HTTP/1.1

        """

        if '\r\n' in self.buf:
            request, ignore, self.buf = self.buf.partition('\r\n')
            try:
                method, self.location, http_version = request.split(' ')
            except ValueError as error:
                log.err(error)
                self.loseConnection()
            else:
                self.state = NEGOTIATION

    def handle_negotiation(self):
        """
        Handle negotiations here. We perform some basic checks here, for
        example we check if the protocol being used is WebSocket and if
        we support the version used by the browser.

        In the case that we don't support the broser version wew send back
        an HTTP/1.1 404 Bad Request message with a list of our supported
        protocol versions as is defined in the [RFC6455][Section 4.4]
        """

        # we got a complete set of headers?
        if '\r\n\r\n' in self.buf:
            head, ignore, self.buf = self.buf.partition('\r\n\r\n')
            self.parse_headers(head)

            # validate protocol beign used
            if 'Upgrade' in self.headers.get('Connection', ''):
                if self.headers.get('Upgrade').lower() != 'websocket':
                    raise InvalidProtocol(
                        'Not handling non-WS request. Connection lose...'
                    )

            # Stash host and origin for those browsers that care about it.
            if "Host" in self.headers:
                self.host = self.headers["Host"]
            if "Origin" in self.headers:
                self.origin = self.headers["Origin"]

            # process sub-protocols
            protocol = self.headers.get('WebSocket-Protocol')
            if protocol is None:
                protocol = self.headers.get('Sec-WebSocket-Protocol')

            # no subprotocols are defined if we don't hit this conditional
            if protocol is not None:
                self.protocols = []
                for item in protocol.split(','):
                    self.protocols.append(item)

            # start next phase of handshake for HyBi-00
            if self.is_hybi00:
                log.msg('Starting HyBi-00/Hixie-76 handshake')
                self.version = HYBI00
                self.state = CHALLENGE

            # start next phase of handshake for HyBi-07+
            version = self.headers.get('Sec-WebSocket-Version')
            if version is not None:
                if version not in ('7', '8', '13'):
                    log.msg('Can\'t support protocol version {}'.format(
                        version))
                    raise InvalidProtocolVersion()

                if version == '7':
                    log.msg('Starting HyBi-07 conversation')
                    self.version = HYBI07
                elif version == '8':
                    log.msg('Starting HyBi-10 conversation')
                    self.version = HYBI10
                elif version == '13':
                    log.msg('Starting RFC 6455 conversation')
                    self.version = RFC6455

                preamble = HyBi07HandshakePreamble(self)
                preamble.write_to_transport(self.transport)
                self.state = FRAMES

    def handle_challenge(self):
        """Handle challenge. This is exclusive to HyBi-00/Hixie-76
        """

        if len(self.buf) >= 8:
            # split buff to extract the challenge random 8 bytes
            challenge, self.buf = self.buf[:8], self.buf[8:]
            response = self.complete_hybi00(challenge)

            # send the handshake preamble with the response
            preamble = HyBi00HandshakePreamble(self)
            preamble.write_to_transport(self.transport, response)
            log.msg('Completed HyBi-00/Hixie-76 handshake')

            # we are done here, start sending frames
            self.state = FRAMES

    def handle_frames(self):
        """
        Use the correct frame parser and send parsed data to the underlying
        protocol
        """

        if self.version == HYBI00:
            frame_parser = HyBi00Frame(self.buf)
        elif self.version in (HYBI07, HYBI10, RFC6455):
            frame_parser = HyBi07Frame(self.buf)
        else:
            raise InvalidProtocolVersion(
                'Unknown version {!r}'.format(self.version)
            )

        try:
            frames, self.buf = frame_parser.parse()
        except WebSocketError as error:
            log.err(error)
            self.close(error)
            return

        for frame in frames:
            opcode, data = frame
            if opcode == DATA:
                # pass the frame to the underlying protocol
                ProtocolWrapper.dataReceived(self, data)
            elif opcode == CLOSE:
                # the other side want's to close
                reason, text = data
                log.msg('Closing connection: {!r} ({:d})'.format(
                    text, reason
                ))

                # close the connection
                self.close()
            elif opcode == PING:
                # send pong
                self.transport.write(
                    HyBi07Frame(data).generate(0xa)
                )

    def write(self, data):
        """Write to the transport.

        :param data: the buffer data to write
        """

        self.pending_frames.append(data)
        self._send()

    def writeSequence(self, data):
        """Write a sequence of data to the transport

        :param data: the sequence to be written
        """

        self.pending_frames.extend(data)
        self._send()

    def _send(self, binary=False):
        """Send all pending frames
        """

        if self.state == FRAMES:
            if self.version == HYBI00:
                frame_generator = HyBi00Frame
            elif self.version in (HYBI07, HYBI10, RFC6455):
                frame_generator = HyBi07Frame
            else:
                raise InvalidProtocolVersion(
                    'Unknown version {!r}'.format(self.version)
                )

            for frame in self.pending_frames:
                self.transport.write(frame_generator(frame).generate())

            self.pending_frames = []

    def close(self, reason=''):
        """
        Close the connection.

        This includes telling the other side we are closing the connection.

        If the other ending didn't signal that the connection is beign closed,
        then we might not see their last message, but since their last message
        should, according to the specification, be a simpel acknowledgement, it
        shouldn't be a problem.

        Refer to [RFC6455][Page 35][Page 41] for more details
        """

        if self.version in (HYBI07, HYBI10, RFC6455):
            self.transport.write(HyBi07Frame(reason).generate(opcode=0x8))

        self.loseConnection()

    def complete_hybi00(self, challenge):
        """Generate the response for a HyBi-00 challenge.
        """

        key1 = self.headers['Sec-WebSocket-Key1']
        key2 = self.headers['Sec-WebSocket-Key2']

        first = int(''.join(i for i in key1 if i in digits)) / key1.count(' ')
        second = int(''.join(i for i in key2 if i in digits)) / key2.count(' ')

        nonce = pack('>II8s', first, second, challenge)

        return md5(nonce).digest()

    def parse_headers(self, headers):
        """Parse raw HTTP headers.

        :param headers: the headers to parse
        :type headers: str
        """

        self.headers.clear()

        for line in headers.split('\r\n'):
            packed = [i.strip() for i in line.split(':', 1)]
            if len(packed) > 1:
                k, v = packed
                self.headers[k] = v


class WebSocketFactory(WrappingFactory):
    """
    Factory that wraps another factory to provide WebSockets transports
    for all of its protocols
    """

    protocol = WebSocketProtocol
