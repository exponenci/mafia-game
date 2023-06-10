from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

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

class TSessionMoveRequest(_message.Message):
    __slots__ = ["session_id", "username", "vote_for"]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    VOTE_FOR_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    username: str
    vote_for: str
    def __init__(self, username: _Optional[str] = ..., vote_for: _Optional[str] = ..., session_id: _Optional[str] = ...) -> None: ...

class TSessionMoveResponse(_message.Message):
    __slots__ = ["message"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class TSystemNotification(_message.Message):
    __slots__ = ["message", "session_info", "turn_info", "type"]
    class NotificationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    class Role(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    class SessionInfo(_message.Message):
        __slots__ = ["players", "role", "session_id"]
        PLAYERS_FIELD_NUMBER: _ClassVar[int]
        ROLE_FIELD_NUMBER: _ClassVar[int]
        SESSION_ID_FIELD_NUMBER: _ClassVar[int]
        players: _containers.RepeatedScalarFieldContainer[str]
        role: TSystemNotification.Role
        session_id: str
        def __init__(self, session_id: _Optional[str] = ..., role: _Optional[_Union[TSystemNotification.Role, str]] = ..., players: _Optional[_Iterable[str]] = ...) -> None: ...
    class TurnInfo(_message.Message):
        __slots__ = ["target_role", "target_username", "turn", "vote_options"]
        TARGET_ROLE_FIELD_NUMBER: _ClassVar[int]
        TARGET_USERNAME_FIELD_NUMBER: _ClassVar[int]
        TURN_FIELD_NUMBER: _ClassVar[int]
        VOTE_OPTIONS_FIELD_NUMBER: _ClassVar[int]
        target_role: TSystemNotification.Role
        target_username: str
        turn: TSystemNotification.Role
        vote_options: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, turn: _Optional[_Union[TSystemNotification.Role, str]] = ..., vote_options: _Optional[_Iterable[str]] = ..., target_username: _Optional[str] = ..., target_role: _Optional[_Union[TSystemNotification.Role, str]] = ...) -> None: ...
    CITIZEN_ROLE: TSystemNotification.Role
    COMMISSAR_ROLE: TSystemNotification.Role
    MAFIA_ROLE: TSystemNotification.Role
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    REGULAR_MESSAGE: TSystemNotification.NotificationType
    SESSION_INFO_FIELD_NUMBER: _ClassVar[int]
    SESSION_INFO_MESSAGE: TSystemNotification.NotificationType
    TURN_INFO_FIELD_NUMBER: _ClassVar[int]
    TURN_INFO_MESSAGE: TSystemNotification.NotificationType
    TYPE_FIELD_NUMBER: _ClassVar[int]
    message: str
    session_info: TSystemNotification.SessionInfo
    turn_info: TSystemNotification.TurnInfo
    type: TSystemNotification.NotificationType
    def __init__(self, type: _Optional[_Union[TSystemNotification.NotificationType, str]] = ..., message: _Optional[str] = ..., session_info: _Optional[_Union[TSystemNotification.SessionInfo, _Mapping]] = ..., turn_info: _Optional[_Union[TSystemNotification.TurnInfo, _Mapping]] = ...) -> None: ...
