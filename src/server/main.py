import argparse, sys
from sys import stderr

import socket as sckt
from socket import socket

from src.protocol import commands
from src.protocol.commands import ProtocolObject

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

        # TODO: Multithreading, multiple clients, multiple channels
        # For now, we just connect to 1 client in a simple loop so we can test the protocol
        client_sock, (client_addr, client_port) = sock.accept()
        while True:
            client_msg: ProtocolObject | None = commands.receive(client_sock)

            match client_msg:
                case None:
                    print("Disconnect detected. TODO: debug level, client ID report, ...")
                    sys.exit(0) # TODO: Don't exit here when multiple clients are supported

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

    except KeyboardInterrupt:
        print("\nDetected shutdown signal. Shutting down...")
        # Further shutdown handling (closing sockets and connections) happens
        # in the finally block, no need to do it here

    except Exception as e:
        print(f"Unexpected error: {e}\nShutting down...")

    finally:
        if sock:
            sock.close()

        sys.exit(0)
