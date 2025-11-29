from typing import Any
from .shared import ProtocolObject

# TODO: Determine if these events are properly designed, if more events are
# needed, etc.

class EventObject(ProtocolObject):
    """Base class for all events."""
    pass

class EventReceiveMessage(EventObject):
    """
    Event: Message received from client.
    Response: Relay the message to all other clients, with information about
    the sender.
    """
    __slots__ = ('sender_nick', 'message')

    def __init__(self, sender_nick: str, message: str):
        self.sender_nick: str = sender_nick
        self.message: str = message

class EventList(EventObject):
    """
    Event: A client requested a list of channels and number of users.
    Response: Give that information to that client.
    """
    __slots__ = ('num_users', 'channels')

    def __init__(self, num_users: int, channels: tuple[str]):
        self.num_users: int = num_users
        self.channels: tuple[str] = channels

class EventJoin(EventObject):
    """
    Event: A client joined a channel.
    Response: Inform other members of that channel of the new user.
    """
    __slots__ = ('new_user_nick', 'channel')

    def __init__(self, new_user_nick: str, channel: str):
        self.new_user_nick: str = new_user_nick
        self.channel: str = channel

class EventLeave(EventObject):
    """
    Event: A user left the channel.
    Response: Inform other members of that channel that the user left.
    """
    __slots__ = ('left_user_nick', 'channel')

    def __init__(self, left_user_nick: str, channel: str):
        self.left_user_nick: str = left_user_nick
        self.channel: str = channel

class EventError(EventObject):
    """
    Event: An error occurred.
    Response: Report the error to the relevant user(s).
    """
    __slots__ = ('relevant_user_nicks', 'error')

    def __init__(self, relevant_user_nicks: tuple[str], error: Any):
        self.relevant_user_nicks: tuple[str] = relevant_user_nicks
        self.error: Any = error
