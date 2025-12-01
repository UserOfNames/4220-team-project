# Members
- Alphonse Amobi: aamobi1
- Viktorio Garev: vgarev1
- Zach Dierberger: zdierberger1 

# Demo video link
https://www.youtube.com/watch?v=1zvoOd2fNOM&feature=youtu.be

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
- Alphonse Amobi: Recorded the video demo.
- Viktorio Garev: Created the team Discord server.
- Zachary Dierberger: Wrote the program & recorded the code walkthrough.

The development process was pretty straightforward. Most of the code was just
somewhat tedious control flow management, matching events and commands, and
creating the logic to manage server and client state. The hardest part was
getting the multithreading to work, especially on the client side. The server's
worker-based threading model was pretty easy to set up, but the client's
threading model included a server listener (to handle events) and a user input
listener (to form commands). Coordinating the two was surprisingly tricky.

The repo is at https://github.com/UserOfNames/4220-team-project
