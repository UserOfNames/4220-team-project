import argparse, socket, sys

# Slightly unfortunate hack to strongly type parsed arguments...
# Without this, type checkers will flag the return type of parse_args() as Any.
# By using this class as the namespace and hinting its attributes, we get our
# strong typing back.
class ServerArgs(argparse.Namespace):
    port: int = -1       # Server must specify a port
    debug_level: int = 0 # 0 is a reasonable default, no need to specify it manually

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Server-side implementation of the chat protocol')
    _ = parser.add_argument('-p', '--port', help='Port number to run the server on', type=int, required=True)
    _ = parser.add_argument('-d', '--debug-level', help='How many events to log. May be 0 (only errors) or 1 (all events).', type=int)
    args = parser.parse_args(namespace=ServerArgs())

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # AF_INET: IPv4
        # SOCK_STREAM: TCP
        sock.bind(('', args.port)) # Empty string listens on all interfaces
        sock.listen(5) # Allow 5 unaccepted connections before dropping further requests

        # TODO: Multithreading, multiple clients, multiple channels
        # For now, we just connect to 1 client in a simple loop so we can test the protocol
        while True:
            client_sock, client_addr = sock.accept()

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
