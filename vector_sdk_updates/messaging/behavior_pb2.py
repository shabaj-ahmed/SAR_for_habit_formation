# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: anki_vector/messaging/behavior.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'anki_vector/messaging/behavior.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from anki_vector.messaging import messages_pb2 as anki__vector_dot_messaging_dot_messages__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n$anki_vector/messaging/behavior.proto\x12\x1e\x41nki.Vector.external_interface\x1a$anki_vector/messaging/messages.proto\"\x10\n\x0e\x43ontrolRelease\"\xae\x01\n\x0e\x43ontrolRequest\x12I\n\x08priority\x18\x01 \x01(\x0e\x32\x37.Anki.Vector.external_interface.ControlRequest.Priority\"Q\n\x08Priority\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x16\n\x12OVERRIDE_BEHAVIORS\x10\n\x12\x0b\n\x07\x44\x45\x46\x41ULT\x10\x14\x12\x13\n\x0fRESERVE_CONTROL\x10\x1e\"\xbe\x01\n\x16\x42\x65haviorControlRequest\x12I\n\x0f\x63ontrol_release\x18\x01 \x01(\x0b\x32..Anki.Vector.external_interface.ControlReleaseH\x00\x12I\n\x0f\x63ontrol_request\x18\x02 \x01(\x0b\x32..Anki.Vector.external_interface.ControlRequestH\x00\x42\x0e\n\x0crequest_type\"\x18\n\x16\x43ontrolGrantedResponse\"\x15\n\x13\x43ontrolLostResponse\"\x1d\n\x1bReservedControlLostResponse\"\x82\x03\n\x17\x42\x65haviorControlResponse\x12Z\n\x18\x63ontrol_granted_response\x18\x01 \x01(\x0b\x32\x36.Anki.Vector.external_interface.ControlGrantedResponseH\x00\x12Q\n\x12\x63ontrol_lost_event\x18\x02 \x01(\x0b\x32\x33.Anki.Vector.external_interface.ControlLostResponseH\x00\x12\x43\n\nkeep_alive\x18\x03 \x01(\x0b\x32-.Anki.Vector.external_interface.KeepAlivePingH\x00\x12\x62\n\x1breserved_control_lost_event\x18\x04 \x01(\x0b\x32;.Anki.Vector.external_interface.ReservedControlLostResponseH\x00\x42\x0f\n\rresponse_typeb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'anki_vector.messaging.behavior_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_CONTROLRELEASE']._serialized_start=110
  _globals['_CONTROLRELEASE']._serialized_end=126
  _globals['_CONTROLREQUEST']._serialized_start=129
  _globals['_CONTROLREQUEST']._serialized_end=303
  _globals['_CONTROLREQUEST_PRIORITY']._serialized_start=222
  _globals['_CONTROLREQUEST_PRIORITY']._serialized_end=303
  _globals['_BEHAVIORCONTROLREQUEST']._serialized_start=306
  _globals['_BEHAVIORCONTROLREQUEST']._serialized_end=496
  _globals['_CONTROLGRANTEDRESPONSE']._serialized_start=498
  _globals['_CONTROLGRANTEDRESPONSE']._serialized_end=522
  _globals['_CONTROLLOSTRESPONSE']._serialized_start=524
  _globals['_CONTROLLOSTRESPONSE']._serialized_end=545
  _globals['_RESERVEDCONTROLLOSTRESPONSE']._serialized_start=547
  _globals['_RESERVEDCONTROLLOSTRESPONSE']._serialized_end=576
  _globals['_BEHAVIORCONTROLRESPONSE']._serialized_start=579
  _globals['_BEHAVIORCONTROLRESPONSE']._serialized_end=965
# @@protoc_insertion_point(module_scope)
