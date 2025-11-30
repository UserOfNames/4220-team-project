import argparse

import selectors
from selectors import DefaultSelector

import sys
from sys import stderr

import socket as sckt
from socket import socket

from src.protocol import commands
from src.protocol import events
from src.protocol import shared

class ChatServer:
    __slots__ = ('debug_level', 'username_generator', 'selectors', 'connections', 'channels')

    def __init__(self, port: int, debug_level: int):
        self.debug_level: int = debug_level

        # Used to generate the initial username of a new clint
        self.username_generator = self.gen_initial_username()

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
        listener.setsockopt(sckt.SOL_SOCKET, sckt.SO_REUSEADDR, 1) # Fix 'address already in use'
        listener.bind(('', port)) # Empty string listens on all interfaces
        listener.listen(5) # Allow 5 unaccepted connections before dropping further requests
        listener.setblocking(False) # Necessary for selectors to work

        _ = self.selectors.register(listener, selectors.EVENT_READ, data=self._listener_callback)

    def gen_initial_username(self):
        x = 0
        while True:
            x += 1
            username = f"User {x}"
            yield username

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
            _ = self.selectors.unregister(sock)
            sock.close()

        self.selectors.close()

    def send_event(self, event: events.EventObject, target: socket):
        if isinstance(event, events.EventError):
            print(f"ERROR:\nOrigin: {target.getpeername()}\n{event}\n", file=stderr)
        elif self.debug_level == 1:
            print(f"EVENT:\nOrigin: {target.getpeername()}\n{event}\n")

        shared.send(event, target)

    # Process commands from the client.
    def _handle_command(self, origin: socket, msg: commands.CommandObject):
        origin_nick = self.connections[origin]

        match msg:
            case commands.CmdSendMessage(message=message, channel=channel):
                try:
                    target = self.channels[channel]
                except KeyError:
                    error = events.EventError(f"Channel {channel} not found")
                    self.send_event(error, origin)
                    return

                if origin not in target:
                    error = events.EventError(f"Not in channel {channel}, consider joining")
                    self.send_event(error, origin)
                    return

                response = events.EventReceiveMessage(origin_nick, message, channel)
                for conn in target:
                    self.send_event(response, conn)

            case commands.CmdList():
                num_users = len(self.connections)
                channels = tuple(self.channels.keys())
                response = events.EventList(num_users, channels)
                self.send_event(response, origin)

            case commands.CmdNick(nickname=new_nick):
                if new_nick in self.connections.values():
                    error = events.EventError("Duplicate nickname")
                    self.send_event(error, origin)
                else:
                    old_nick = self.connections[origin]
                    self.connections[origin] = new_nick
                    response = events.EventNick(old_nick, new_nick)

                    for conn in self.connections.keys():
                        self.send_event(response, conn)

            case commands.CmdJoin(channel=channel):
                try:
                    target = self.channels[channel]
                except KeyError:
                    error = events.EventError(f"Channel {channel} not found")
                    self.send_event(error, origin)
                    return

                target.add(origin)
                response = events.EventJoin(origin_nick, channel)
                for conn in target:
                    self.send_event(response, conn)

            case commands.CmdLeave(channel=channel):
                # TODO: Solve the channel None issue; this will require some
                # remodeling some stuff, like making the client track the active
                # channel, removing the None case and sending the active channel,
                # etc.
                if channel not in self.channels:
                    error = events.EventError(f"Channel {channel} not found")
                    self.send_event(error, origin)
                    return

                try:
                    target = self.channels[channel]
                    target.remove(origin)
                except KeyError:
                    error = events.EventError(f"Not a member of {channel}")
                    self.send_event(error, origin)
                    return

                response = events.EventLeave(origin_nick, channel)
                for conn in target:
                    self.send_event(response, conn)

            case _:
                print(f"Error: Unknown command {msg}", file=stderr)

    # Callback for the listener socket.
    def _listener_callback(self, key):
        sock = key.fileobj
        client_sock, _ = sock.accept()

        # Necessary for selectors to work
        client_sock.setblocking(False)

        _ = self.selectors.register(client_sock, selectors.EVENT_READ, data=self._message_callback)

        initial_nickname = next(self.username_generator)
        self.connections[client_sock] = initial_nickname
        if self.debug_level == 1:
            print(f"New client {client_sock.getpeername()} connected with initial nickname {initial_nickname}")

    # Callback for client sockets.
    def _message_callback(self, key):
        sock = key.fileobj

        try:
            client_msg = shared.receive(sock)
            if client_msg is None:
                if self.debug_level == 1:
                    print(f"Client {sock.getpeername()} disconnected.")

                _ = self.connections.pop(sock, None)
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
