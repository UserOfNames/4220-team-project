import pickle, socket, struct


class ProtocolObject:
    pass

class CmdList(ProtocolObject):
    __slots__ = ()

class CmdNick(ProtocolObject):
    __slots__ = ('nickname')

    def __init__(self, nickname: str):
        self.nickname: str = nickname

class CmdJoin(ProtocolObject):
    __slots__ = ('channel')

    def __init__(self, channel: str):
        self.channel: str = channel

class CmdLeave(ProtocolObject):
    __slots__ = ('channel')

    def __init__(self, channel: str | None):
        self.channel: str | None = channel

class CmdSendMessage(ProtocolObject):
    __slots__ = ('message', 'channel')

    def __init__(self, message: str, channel: str):
        self.message: str = message
        self.channel: str = channel

# Commands `connect`, `quit`, and `help` can be handled locally and do not need
# to be sent to the server, so we don't define objects for them


def send(data: ProtocolObject, sock: socket.socket):
    serialized_data = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)

    # Since we're using TCP, we must encode the length of the message before we
    # send it. Otherwise, the receiver would not know how long the message is.
    # ! = Big endian (network order), I = 4-byte integer
    length = struct.pack('!I', len(serialized_data))

    sock.sendall(length + serialized_data)

def receive(sock: socket.socket):
    # Length header is 4 bytes (see `send` implementation)
    length_bytes: bytes = recv_n(sock, 4)
    length: int = struct.unpack('!I', length_bytes)[0]

    raw_msg = recv_n(sock, length)
    return pickle.loads(raw_msg)

def recv_n(sock: socket.socket, n: int) -> bytes:
    res = b''

    while len(res) < n:
        packet = sock.recv(n - len(res))
        if not packet:
            raise ConnectionResetError("Connection closed unexpectedly.")
        res += packet
    return res
