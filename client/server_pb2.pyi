from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

Citizen: Role
Commissar: Role
DESCRIPTOR: _descriptor.FileDescriptor
Mafia: Role
Undefined: Role

class TAddMemberToSessionRequest(_message.Message):
    __slots__ = ["session_id", "username"]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    username: str
    def __init__(self, username: _Optional[str] = ..., session_id: _Optional[str] = ...) -> None: ...

class TAddMemberToSessionResponse(_message.Message):
    __slots__ = ["message", "role"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    message: str
    role: Role
    def __init__(self, message: _Optional[str] = ..., role: _Optional[_Union[Role, str]] = ...) -> None: ...

class TGetSessionInfoRequest(_message.Message):
    __slots__ = ["username"]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    username: str
    def __init__(self, username: _Optional[str] = ...) -> None: ...

class TGetSessionInfoResponse(_message.Message):
    __slots__ = ["clients", "mafia_count", "message", "players_count", "session_id"]
    CLIENTS_FIELD_NUMBER: _ClassVar[int]
    MAFIA_COUNT_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    PLAYERS_COUNT_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    clients: _containers.RepeatedScalarFieldContainer[str]
    mafia_count: int
    message: str
    players_count: int
    session_id: str
    def __init__(self, message: _Optional[str] = ..., session_id: _Optional[str] = ..., players_count: _Optional[int] = ..., mafia_count: _Optional[int] = ..., clients: _Optional[_Iterable[str]] = ...) -> None: ...

class TNotification(_message.Message):
    __slots__ = ["notification"]
    NOTIFICATION_FIELD_NUMBER: _ClassVar[int]
    notification: str
    def __init__(self, notification: _Optional[str] = ...) -> None: ...

class TPingRequest(_message.Message):
    __slots__ = ["username"]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    username: str
    def __init__(self, username: _Optional[str] = ...) -> None: ...

class TPingResponse(_message.Message):
    __slots__ = ["message"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class TRegisterClientRequest(_message.Message):
    __slots__ = ["username"]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    username: str
    def __init__(self, username: _Optional[str] = ...) -> None: ...

class TRegisterClientResponse(_message.Message):
    __slots__ = ["message"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class TSessionMoveRequest(_message.Message):
    __slots__ = ["sesion_id", "username", "vote_for"]
    SESION_ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    VOTE_FOR_FIELD_NUMBER: _ClassVar[int]
    sesion_id: str
    username: str
    vote_for: str
    def __init__(self, username: _Optional[str] = ..., vote_for: _Optional[str] = ..., sesion_id: _Optional[str] = ...) -> None: ...

class TSessionMoveResponse(_message.Message):
    __slots__ = ["message"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class TStartSessionRequest(_message.Message):
    __slots__ = ["mafia_count", "players_count", "username"]
    MAFIA_COUNT_FIELD_NUMBER: _ClassVar[int]
    PLAYERS_COUNT_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    mafia_count: int
    players_count: int
    username: str
    def __init__(self, username: _Optional[str] = ..., players_count: _Optional[int] = ..., mafia_count: _Optional[int] = ...) -> None: ...

class TStartSessionResponse(_message.Message):
    __slots__ = ["message", "role", "session_id"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    message: str
    role: Role
    session_id: str
    def __init__(self, message: _Optional[str] = ..., session_id: _Optional[str] = ..., role: _Optional[_Union[Role, str]] = ...) -> None: ...

class TSubscribeRequest(_message.Message):
    __slots__ = ["session_id", "username"]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    username: str
    def __init__(self, username: _Optional[str] = ..., session_id: _Optional[str] = ...) -> None: ...

class Role(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
