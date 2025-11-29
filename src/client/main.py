import socket as sckt
from socket import socket

from sys import stderr

import threading

from src.protocol import commands
from src.protocol import events
from src.protocol import shared


help_block = '''
COMMANDS
Format: /command-name <parameter> [optional parameter]

/connect <server> [port#]
\tConnect to named server

/nick <nickname>
\tPick a new nickname (must be unique among active users)

/list
\tList channels and number of users

/join <channel>
\tJoin a channel

/leave [channel]
\tLeave the current (or named, if provided) channel

/quit
\tLeave chat, disconnect from server, and exit

/help
\tPrint out this help message
'''

class ChatClient:
    def __init__(self):
        # If self.connection is None, we aren't connected to a server.
        # Otherwise, the socket for the connection is stored here.
        self.connection: socket | None = None

        # To allow simultaneously listening for user input and events from the
        # server, we spawn a separate listener thread while connections are live.
        self.listener: threading.Thread | None = None

    def connect(self, target_host: str, target_port: int):
        sock = socket(sckt.AF_INET, sckt.SOCK_STREAM)
        sock.connect((target_host, target_port))
        self.connection = sock

        self.listener = threading.Thread(target=self.listener_thread, daemon=True)
        self.listener.start()

    def disconnect(self):
        if self.connection:
            self.connection.shutdown(sckt.SHUT_RDWR)
            self.connection.close()
        self.connection = None
        self.listener = None

    def listener_thread(self):
        while self.connection is not None:
            try:
                event = shared.receive(self.connection)

                if event is None:
                    print("\nServer disconnected.")
                    self.disconnect()
                    break

                # TODO: Handle events

            # TODO: Catch exceptions; which exceptions are expected?
            except Exception as e:
                print(f"Unexpected error in listener thread: {e}")
                break

    def send_to_server(self, msg: commands.CommandObject):
        if self.connection:
            shared.send(msg, self.connection)
        else:
            print(f"Error: Not connected.", file=stderr)

    def handle_command(self, raw_command: str):
        command_no_prefix = raw_command[1:]
        command_parts = command_no_prefix.split()

        if len(command_parts) < 1:
            print(f"Error: No command found.")
            return
        command = command_parts[0]

        match command:
            # TODO: Project requirements say "Connect to named server". How does
            # naming work?
            case 'connect':
                try:
                    target_host: str = command_parts[1]
                    target_port: int = int(command_parts[2]) if len(command_parts) > 2 else 12345
                    self.connect(target_host, target_port)
                    print("Connected successfully.")
                except IndexError:
                    print(f"Error: Not enough arguments. Expected server name.", file=stderr)
                except ConnectionRefusedError:
                    print(f"Error: Connection refused", file=stderr)

            case 'nick':
                try:
                    self.send_to_server(commands.CmdNick(command_parts[1]))
                except IndexError:
                    print(f"Error: Not enough arguments. Expected new nickname.", file=stderr)

            case 'list':
                self.send_to_server(commands.CmdList())

            case 'join':
                try:
                    self.send_to_server(commands.CmdJoin(command_parts[1]))
                except IndexError:
                    print(f"Error: Not enough arguments. Expected channel name.", file=stderr)

            case 'leave':
                target_channel = command_parts[1] if len(command_parts) > 1 else None
                self.send_to_server(commands.CmdLeave(target_channel))

            case 'quit':
                self.disconnect()
                print("Disconnected from server.")

            case 'help':
                print(help_block)

            case _:
                print(f"Error: Invalid command {command}", file=stderr)

    def send_message(self, message: str):
        msg_obj = commands.CmdSendMessage(message, "channel placeholder")
        self.send_to_server(msg_obj)

    def run(self):
        print("Enter '/help' for help.")
        while True:
            user_input = input(":> ")
            try:
                if user_input.startswith('/'):
                    self.handle_command(user_input)
                else:
                    self.send_message(user_input)

            except BrokenPipeError:
                print("Error: Broken connection. Please reconnect.", file=stderr)
                continue

if __name__ == '__main__':
    client = ChatClient()
    client.run()
