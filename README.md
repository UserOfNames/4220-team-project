# Members
- Alphonse Amobi: aamobi1
- Viktorio Garev: vgarev1
- Zach Dierberger: zdierberger1 

# Demo video link
TODO

# Code manifest
- **Base directory**:
    - `run_client.sh`: Start the client. Should be run while `cd`ed into the base
      directory.
    - `run_server.sh`: Start the server with `debug-level` 0. Should be run while
      `cd`ed into the base directory. Optionally accepts a port number; otherwise, it
      starts on port 12345.
- `src/client`:
    - `__init__.py`: Empty.
    - `main.py`: Code for the chat client.

- `src/server`:
    - `__init__.py`: Empty.
    - `main.py`: Code for the chat server.

- `src/protocol`:
    - `__init__.py`: Empty.
    - `commands.py`: Declarations for command objects, which are sent from
      clients to the server.
    - `events.py`: Declarations for event objects, which are sent from the
      server to clients.
    - `shared.py`: Common code between clients and servers, including a base
      `ProtocolObject` type for all events and commands, a length-prefixed
      `send()` function to send messages over TCP, and the corresponding `receive()` function.

# Running
The provided `run_client.sh` and `run_server.sh` scripts are sufficient, except
for testing `debug-level=1` on the server. The scripts should be run in the
base directory; that is, they should be visible after running `ls`.

To run the client or server manually, `cd` into the base directory, then run:
- **client**: `python -m src.client.main`
- **server**: `python -m src.server.main <parameters>`

# Testing
Simply ran the programs under various conditions, such as on the same computer
(via localhost) and on different computers. Tried various edge cases, including
repeated connecting and disconnecting, multiple clients, invalid commands,
invalid arguments to commands, etc.

# Observations and roles
TODO
