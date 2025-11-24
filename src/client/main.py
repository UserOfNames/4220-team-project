import pickle, socket
from sys import stderr

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
\tLeave chat, disconenct from server, and exit

/help
\tPrint out this help message
'''

def handle_command(raw_command: str):
    command_no_prefix = raw_command[1:]
    command_parts = command_no_prefix.split()

    if len(command_parts) < 1:
        # TODO: Error
        return
    command = command_parts[0]

    match command:
        # TODO: Project requirements say "Connect to named server". How does
        # naming work?
        case 'connect':
            try:
                target_host: str = command_parts[1]
                target_port: int = int(command_parts[2]) if len(command_parts) > 2 else 12345
                sock.connect((target_host, target_port))
                print("Connected successfully.")
            except IndexError:
                print(f"Error: Not enough arguments. Expected server name.", file=stderr)
            except ConnectionRefusedError:
                print(f"Error: Connection refused", file=stderr)

        case 'nick':
            pass

        case 'list':
            pass

        case 'join':
            pass

        case 'leave':
            pass

        case 'quit':
            pass

        case 'help':
            print(help_block)

        case _:
            print(f"Error: Invalid command {command}", file=stderr)

def send_message(message: str):
    pass

if __name__ == '__main__':
    # AF_INET: IPv4
    # SOCK_STREAM: TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print("Enter '/help' for help.")
    while True:
        user_input = input(":> ")

        if user_input.startswith('/'):
            handle_command(user_input)
        else:
            send_message(user_input)
