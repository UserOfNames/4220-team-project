from .shared import ProtocolObject

class CommandObject(ProtocolObject):
    """
    Base class for all command objects.
    """
    pass

class CmdList(CommandObject):
    """
    Command: List channels and number of users.
    """
    __slots__ = ()

class CmdNick(CommandObject):
    """
    Command: Change nickname.
    """
    __slots__ = ('nickname')

    def __init__(self, nickname: str):
        self.nickname: str = nickname

class CmdJoin(CommandObject):
    """
    Command: Join a new channel.
    """
    __slots__ = ('channel')

    def __init__(self, channel: str):
        self.channel: str = channel

class CmdLeave(CommandObject):
    # TODO: Is 'leave all channels' the correct interpretation of no-args
    # `/leave`?
    """
    Command: Leave the chosen channel, or all channels.
    """
    __slots__ = ('channel')

    def __init__(self, channel: str | None):
        self.channel: str | None = channel

class CmdSendMessage(CommandObject):
    """
    Command: Send a message to the chosen channel.
    """
    __slots__ = ('message', 'channel')

    def __init__(self, message: str, channel: str):
        self.message: str = message
        self.channel: str = channel

# Commands `connect`, `quit`, and `help` can be handled locally and do not need
# to be sent to the server, so we don't define objects for them
