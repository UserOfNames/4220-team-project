import argparse

import selectors

import sys
from sys import stderr

import socket as sckt
from socket import socket

from src.protocol import commands
from src.protocol import shared

# Global selector. This is used to listen on connections without blocking.
sel = selectors.DefaultSelector()

# Callback for the listener socket.
def accept_connection(key, mask):
    sock = key.fileobj
    client_sock, _ = sock.accept()

    # Necessary for selectors to work
    client_sock.setblocking(False)

    _ = sel.register(client_sock, selectors.EVENT_READ, data=service_connection)

# Callback for client sockets.
def service_connection(key, mask):
    sock = key.fileobj

    try:
        client_msg = shared.receive(sock)
        handle_command(sock, client_msg)

    except Exception as e:
        # TODO: Error handling
        print(f"Error in service_connection: {e}", file=stderr)

def handle_command(sock: socket, client_msg: commands.CommandObject | None):
    match client_msg:
        case None:
            print("Disconnect detected. TODO: debug level, client ID report, ...")
            _ = sel.unregister(sock)
            sock.close()

        case commands.CmdSendMessage(message=message):
            print(message)

        case commands.CmdList():
            print("List")

        case commands.CmdNick(nickname=nick):
            print(f"Nick {nick}")

        case commands.CmdJoin(channel=channel):
            print(f"Join {channel}")

        case commands.CmdLeave(channel=channel):
            print(f"Leave {channel}")

        case _:
            print(f"Error: Unknown command {client_msg} TODO client ID report", file=stderr)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Server-side implementation of the chat protocol')
    _ = parser.add_argument('-p', '--port', help='Port number to run the server on', type=int, required=True)
    _ = parser.add_argument('-d', '--debug-level', help='How many events to log. May be 0 (only errors) or 1 (all events).', type=int)
    args = parser.parse_args()

    # AF_INET: IPv4
    # SOCK_STREAM: TCP
    sock = socket(sckt.AF_INET, sckt.SOCK_STREAM)
    try:
        sock.bind(('', args.port)) # Empty string listens on all interfaces
        sock.listen(5) # Allow 5 unaccepted connections before dropping further requests
        sock.setblocking(False) # Necessary for selectors to work

        _ = sel.register(sock, selectors.EVENT_READ, data=accept_connection)

        while True:
            events = sel.select(timeout=None)

            for key, mask in events:
                callback = key.data
                callback(key, mask)


    except KeyboardInterrupt:
        print("\nDetected shutdown signal. Shutting down...")
        # Further shutdown handling (closing sockets and connections) happens
        # in the finally block, no need to do it here

    except Exception as e:
        print(f"Unexpected error: {e}\nShutting down...")

    finally:
        sock.close()
        sel.close()
        sys.exit(0)
