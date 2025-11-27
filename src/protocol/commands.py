class CommandObject:
    pass

class CmdList(CommandObject):
    __slots__ = ()

class CmdNick(CommandObject):
    __slots__ = ('nickname')

    def __init__(self, nickname: str):
        self.nickname: str = nickname

class CmdJoin(CommandObject):
    __slots__ = ('channel')

    def __init__(self, channel: str):
        self.channel: str = channel

class CmdLeave(CommandObject):
    __slots__ = ('channel')

    def __init__(self, channel: str | None):
        self.channel: str | None = channel

class CmdSendMessage(CommandObject):
    __slots__ = ('message', 'channel')

    def __init__(self, message: str, channel: str):
        self.message: str = message
        self.channel: str = channel

# Commands `connect`, `quit`, and `help` can be handled locally and do not need
# to be sent to the server, so we don't define objects for them
