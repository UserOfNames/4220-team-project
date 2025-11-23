import argparse, signal, socket, sys
from types import FrameType

# Slightly unfortunate hack to strongly type parsed arguments...
# Without this, type checkers will flag the return type of parse_args() as Any.
# By using this class as the namespace and hinting its attributes, we get our
# strong typing back.
class ServerArgs(argparse.Namespace):
    port: int = 0
    debug_level: int = 0

def sigint_handler(_sig: int, _frame: FrameType | None):
    print("\nTODO: 'Gracefully shut down with user command Ctrl-C'")
    sys.exit(0)

if __name__ == '__main__':
    _ = signal.signal(signal.SIGINT, sigint_handler)

    parser = argparse.ArgumentParser(description='Server-side implementation of the chat protocol')
    _ = parser.add_argument('-p', '--port', help='Port number to run the server on', type=int)
    _ = parser.add_argument('-d', '--debug-level', help='How many events to log. May be 0 (only errors) or 1 (all events).', type=int)
    args = parser.parse_args(namespace=ServerArgs())
