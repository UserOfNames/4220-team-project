import pickle, socket, struct

class ProtocolObject:
    pass

def send(data: ProtocolObject, sock: socket.socket):
    serialized_data = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)

    # Since we're using TCP, we must encode the length of the message before we
    # send it. Otherwise, the receiver would not know how long the message is.
    # ! = Big endian (network order), I = 4-byte integer
    length = struct.pack('!I', len(serialized_data))

    sock.sendall(length + serialized_data)

def receive(sock: socket.socket):
    # Length header is 4 bytes (see `send` implementation)
    length_bytes: bytes | None = recv_n(sock, 4)
    if length_bytes is None:
        return None
    length: int = struct.unpack('!I', length_bytes)[0]

    raw_msg: bytes | None = recv_n(sock, length)
    if raw_msg is None:
        raise ConnectionResetError("Connection closed unexpectedly.")

    return pickle.loads(raw_msg)

def recv_n(sock: socket.socket, n: int) -> bytes | None:
    res = bytearray()

    while len(res) < n:
        packet = sock.recv(n - len(res))
        if not packet:
            if len(res) == 0:
                return None
            raise ConnectionResetError("Connection closed unexpectedly.")
        res.extend(packet)

    return bytes(res)
