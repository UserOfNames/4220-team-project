import argparse

import selectors
from selectors import DefaultSelector

import sys
from sys import stderr

import socket as sckt
from socket import socket

from src.protocol import commands
from src.protocol import shared

class ChatServer:
    __slots__ = ('selectors', 'connections', 'channels')

    def __init__(self, port: int, debug_level: int):
        # Global selector. This is used to listen on connections without blocking.
        self.selectors: DefaultSelector = DefaultSelector()

        # Dictionary of active connections, mapping sockets to nicknames.
        self.connections: dict[socket, str] = {}

        # TODO: Maybe don't hardcode the channels? Where would channel config go?
        # Dictionary of channels, mapping channel names to connections.
        self.channels: dict[str, set[socket]] = {
            "General": set(),
            "Meta": set(),
            "Misc": set(),
        }

        listener: socket = socket(sckt.AF_INET, sckt.SOCK_STREAM) # AF_INET: IPv4; SOCK_STREAM: TCP
        listener.bind(('', port)) # Empty string listens on all interfaces
        listener.listen(5) # Allow 5 unaccepted connections before dropping further requests
        listener.setblocking(False) # Necessary for selectors to work

        _ = self.selectors.register(listener, selectors.EVENT_READ, data=self._listener_callback)

    def run(self):
        while True:
            events = self.selectors.select(timeout=180) # 3 minutes * 60 = 180 seconds
            if len(events) == 0:
                raise TimeoutError

            for key, _ in events:
                callback = key.data
                callback(key)

    def shutdown(self):
        # Close all the open connections registered with the selector
        for _, key in list(self.selectors.get_map().items()):
            sock: socket = key.fileobj
            self.selectors.unregister(sock)
            sock.close()

        self.selectors.close()

    def _handle_command(self, sock: socket, msg: commands.CommandObject):
        match msg:
            case commands.CmdSendMessage(message=message):
                print(message)

            case commands.CmdList():
                print("List")

            case commands.CmdNick(nickname=nick):
                print(f"Nick {nick}")
                if nick in self.connections.values():
                    # TODO: Error event; duplicate nickname
                    pass
                else:
                    self.connections[sock] = nick

            case commands.CmdJoin(channel=channel):
                print(f"Join {channel}")

            case commands.CmdLeave(channel=channel):
                print(f"Leave {channel}")

            case _:
                print(f"Error: Unknown command {msg} TODO client ID report", file=stderr)

    # Callback for the listener socket.
    def _listener_callback(self, key):
        sock = key.fileobj
        client_sock, _ = sock.accept()

        # Necessary for selectors to work
        client_sock.setblocking(False)

        _ = self.selectors.register(client_sock, selectors.EVENT_READ, data=self._message_callback)
        self.connections[client_sock] = "placeholder" # TODO: Figure out a system for initial nicknames

    # Callback for client sockets.
    def _message_callback(self, key):
        sock = key.fileobj

        try:
            client_msg = shared.receive(sock)
            if client_msg is None:
                print("Disconnect detected. TODO: debug level, client ID report, ...")
                _ = self.selectors.unregister(sock)
                sock.close()
            else:
                self._handle_command(sock, client_msg)

        except Exception as e:
            # TODO: Improve error message
            print(f"Error while handling client: {e}", file=stderr)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Server-side implementation of the chat protocol')
    _ = parser.add_argument('-p', '--port', help='Port number to run the server on', type=int, required=True)
    _ = parser.add_argument('-d', '--debug-level', help='How many events to log. May be 0 (only errors) or 1 (all events).', type=int)
    args = parser.parse_args()

    exit_code = 0
    server = ChatServer(args.port, args.debug_level)
    try:
        server.run()

    except KeyboardInterrupt:
        print("\nDetected shutdown signal. Shutting down...")

    except TimeoutError:
        print("Timed out. Shutting down...")

    except Exception as e:
        print(f"Unexpected error: {e}\nShutting down...")
        exit_code = 1

    finally:
        server.shutdown()
        sys.exit(exit_code)
