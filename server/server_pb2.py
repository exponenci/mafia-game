# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: server.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0cserver.proto\"*\n\x16TRegisterClientRequest\x12\x10\n\x08username\x18\x01 \x01(\t\"*\n\x17TRegisterClientResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\" \n\x0cTPingRequest\x12\x10\n\x08username\x18\x01 \x01(\t\" \n\rTPingResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\"*\n\x16TGetSessionInfoRequest\x12\x10\n\x08username\x18\x01 \x01(\t\"\xbb\x01\n\x17TGetSessionInfoResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\x12\x17\n\nsession_id\x18\x02 \x01(\tH\x00\x88\x01\x01\x12\x1a\n\rplayers_count\x18\x03 \x01(\x05H\x01\x88\x01\x01\x12\x18\n\x0bmafia_count\x18\x04 \x01(\x05H\x02\x88\x01\x01\x12\x0f\n\x07\x63lients\x18\x05 \x03(\tB\r\n\x0b_session_idB\x10\n\x0e_players_countB\x0e\n\x0c_mafia_count\"T\n\x14TStartSessionRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x15\n\rplayers_count\x18\x02 \x01(\x05\x12\x13\n\x0bmafia_count\x18\x03 \x01(\x05\"a\n\x15TStartSessionResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\x12\x14\n\nsession_id\x18\x02 \x01(\tH\x00\x12\x15\n\x04role\x18\x03 \x01(\x0e\x32\x05.RoleH\x00\x42\n\n\x08response\"B\n\x1aTAddMemberToSessionRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x12\n\nsession_id\x18\x02 \x01(\t\"Q\n\x1bTAddMemberToSessionResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\x12\x18\n\x04role\x18\x02 \x01(\x0e\x32\x05.RoleH\x00\x88\x01\x01\x42\x07\n\x05_role\"9\n\x11TSubscribeRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x12\n\nsession_id\x18\x02 \x01(\t\"%\n\rTNotification\x12\x14\n\x0cnotification\x18\x01 \x01(\t\"L\n\x13TSessionMoveRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x10\n\x08vote_for\x18\x02 \x01(\t\x12\x11\n\tsesion_id\x18\x03 \x01(\t\"\'\n\x14TSessionMoveResponse\x12\x0f\n\x07message\x18\x01 \x01(\t*<\n\x04Role\x12\r\n\tUndefined\x10\x00\x12\t\n\x05Mafia\x10\x01\x12\x0b\n\x07\x43itizen\x10\x02\x12\r\n\tCommissar\x10\x03\x32\xa7\x01\n\x07IServer\x12\x30\n\rConnectClient\x12\r.TPingRequest\x1a\x0e.TPingResponse\"\x00\x12\x33\n\x10\x44isconnectClient\x12\r.TPingRequest\x1a\x0e.TPingResponse\"\x00\x12\x35\n\x10GetOnlinePlayers\x12\r.TPingRequest\x1a\x0e.TPingResponse\"\x00\x30\x01\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'server_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _ROLE._serialized_start=959
  _ROLE._serialized_end=1019
  _TREGISTERCLIENTREQUEST._serialized_start=16
  _TREGISTERCLIENTREQUEST._serialized_end=58
  _TREGISTERCLIENTRESPONSE._serialized_start=60
  _TREGISTERCLIENTRESPONSE._serialized_end=102
  _TPINGREQUEST._serialized_start=104
  _TPINGREQUEST._serialized_end=136
  _TPINGRESPONSE._serialized_start=138
  _TPINGRESPONSE._serialized_end=170
  _TGETSESSIONINFOREQUEST._serialized_start=172
  _TGETSESSIONINFOREQUEST._serialized_end=214
  _TGETSESSIONINFORESPONSE._serialized_start=217
  _TGETSESSIONINFORESPONSE._serialized_end=404
  _TSTARTSESSIONREQUEST._serialized_start=406
  _TSTARTSESSIONREQUEST._serialized_end=490
  _TSTARTSESSIONRESPONSE._serialized_start=492
  _TSTARTSESSIONRESPONSE._serialized_end=589
  _TADDMEMBERTOSESSIONREQUEST._serialized_start=591
  _TADDMEMBERTOSESSIONREQUEST._serialized_end=657
  _TADDMEMBERTOSESSIONRESPONSE._serialized_start=659
  _TADDMEMBERTOSESSIONRESPONSE._serialized_end=740
  _TSUBSCRIBEREQUEST._serialized_start=742
  _TSUBSCRIBEREQUEST._serialized_end=799
  _TNOTIFICATION._serialized_start=801
  _TNOTIFICATION._serialized_end=838
  _TSESSIONMOVEREQUEST._serialized_start=840
  _TSESSIONMOVEREQUEST._serialized_end=916
  _TSESSIONMOVERESPONSE._serialized_start=918
  _TSESSIONMOVERESPONSE._serialized_end=957
  _ISERVER._serialized_start=1022
  _ISERVER._serialized_end=1189
# @@protoc_insertion_point(module_scope)