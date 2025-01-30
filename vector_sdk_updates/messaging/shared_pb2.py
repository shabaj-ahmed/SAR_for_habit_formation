# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: anki_vector/messaging/shared.proto
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
    'anki_vector/messaging/shared.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from anki_vector.messaging import behavior_pb2 as anki__vector_dot_messaging_dot_behavior__pb2
from anki_vector.messaging import cube_pb2 as anki__vector_dot_messaging_dot_cube__pb2
from anki_vector.messaging import messages_pb2 as anki__vector_dot_messaging_dot_messages__pb2
from anki_vector.messaging import settings_pb2 as anki__vector_dot_messaging_dot_settings__pb2
from anki_vector.messaging import extensions_pb2 as anki__vector_dot_messaging_dot_extensions__pb2
from anki_vector.messaging import response_status_pb2 as anki__vector_dot_messaging_dot_response__status__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\"anki_vector/messaging/shared.proto\x12\x1e\x41nki.Vector.external_interface\x1a$anki_vector/messaging/behavior.proto\x1a anki_vector/messaging/cube.proto\x1a$anki_vector/messaging/messages.proto\x1a$anki_vector/messaging/settings.proto\x1a&anki_vector/messaging/extensions.proto\x1a+anki_vector/messaging/response_status.proto\"J\n\x16ProtocolVersionRequest\x12\x16\n\x0e\x63lient_version\x18\x01 \x01(\x03\x12\x18\n\x10min_host_version\x18\x02 \x01(\x03\"\xa7\x01\n\x17ProtocolVersionResponse\x12N\n\x06result\x18\x01 \x01(\x0e\x32>.Anki.Vector.external_interface.ProtocolVersionResponse.Result\x12\x14\n\x0chost_version\x18\x02 \x01(\x03\"&\n\x06Result\x12\x0f\n\x0bUNSUPPORTED\x10\x00\x12\x0b\n\x07SUCCESS\x10\x01\"h\n\x12\x43onnectionResponse\x12>\n\x06status\x18\x01 \x01(\x0b\x32..Anki.Vector.external_interface.ResponseStatus\x12\x12\n\nis_primary\x18\x02 \x01(\x08\"\xc9\x08\n\x05\x45vent\x12P\n\x13time_stamped_status\x18\x01 \x01(\x0b\x32\x31.Anki.Vector.external_interface.TimeStampedStatusH\x00\x12=\n\twake_word\x18\x03 \x01(\x0b\x32(.Anki.Vector.external_interface.WakeWordH\x00\x12P\n\x13robot_observed_face\x18\x05 \x01(\x0b\x32\x31.Anki.Vector.external_interface.RobotObservedFaceH\x00\x12\x64\n\x1erobot_changed_observed_face_id\x18\x06 \x01(\x0b\x32:.Anki.Vector.external_interface.RobotChangedObservedFaceIDH\x00\x12\x43\n\x0cobject_event\x18\x07 \x01(\x0b\x32+.Anki.Vector.external_interface.ObjectEventH\x00\x12K\n\x10stimulation_info\x18\x08 \x01(\x0b\x32/.Anki.Vector.external_interface.StimulationInfoH\x00\x12\x41\n\x0bphoto_taken\x18\t \x01(\x0b\x32*.Anki.Vector.external_interface.PhotoTakenH\x00\x12\x41\n\x0brobot_state\x18\n \x01(\x0b\x32*.Anki.Vector.external_interface.RobotStateH\x00\x12\x43\n\x0c\x63ube_battery\x18\x0b \x01(\x0b\x32+.Anki.Vector.external_interface.CubeBatteryH\x00\x12\x43\n\nkeep_alive\x18\x0c \x01(\x0b\x32-.Anki.Vector.external_interface.KeepAlivePingH\x00\x12Q\n\x13\x63onnection_response\x18\r \x01(\x0b\x32\x32.Anki.Vector.external_interface.ConnectionResponseH\x00\x12R\n\x14mirror_mode_disabled\x18\x10 \x01(\x0b\x32\x32.Anki.Vector.external_interface.MirrorModeDisabledH\x00\x12]\n\x1avision_modes_auto_disabled\x18\x11 \x01(\x0b\x32\x37.Anki.Vector.external_interface.VisionModesAutoDisabledH\x00\x12\x41\n\x0buser_intent\x18\x13 \x01(\x0b\x32*.Anki.Vector.external_interface.UserIntentH\x00\x42\x0c\n\nevent_type\"\x1a\n\nFilterList\x12\x0c\n\x04list\x18\x01 \x03(\t\"\xb6\x01\n\x0c\x45ventRequest\x12@\n\nwhite_list\x18\x01 \x01(\x0b\x32*.Anki.Vector.external_interface.FilterListH\x00\x12@\n\nblack_list\x18\x02 \x01(\x0b\x32*.Anki.Vector.external_interface.FilterListH\x00\x12\x15\n\rconnection_id\x18\x03 \x01(\tB\x0b\n\tlist_type\"\x8b\x01\n\rEventResponse\x12>\n\x06status\x18\x01 \x01(\x0b\x32..Anki.Vector.external_interface.ResponseStatus\x12\x34\n\x05\x65vent\x18\x02 \x01(\x0b\x32%.Anki.Vector.external_interface.Event:\x04\x80\xa6\x1d\x01\"I\n\x19UserAuthenticationRequest\x12\x17\n\x0fuser_session_id\x18\x01 \x01(\x0c\x12\x13\n\x0b\x63lient_name\x18\x02 \x01(\x0c\"\xf0\x01\n\x1aUserAuthenticationResponse\x12>\n\x06status\x18\x01 \x01(\x0b\x32..Anki.Vector.external_interface.ResponseStatus\x12M\n\x04\x63ode\x18\x02 \x01(\x0e\x32?.Anki.Vector.external_interface.UserAuthenticationResponse.Code\x12\x19\n\x11\x63lient_token_guid\x18\x03 \x01(\x0c\"(\n\x04\x43ode\x12\x10\n\x0cUNAUTHORIZED\x10\x00\x12\x0e\n\nAUTHORIZED\x10\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'anki_vector.messaging.shared_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_EVENTRESPONSE']._loaded_options = None
  _globals['_EVENTRESPONSE']._serialized_options = b'\200\246\035\001'
  _globals['_PROTOCOLVERSIONREQUEST']._serialized_start=303
  _globals['_PROTOCOLVERSIONREQUEST']._serialized_end=377
  _globals['_PROTOCOLVERSIONRESPONSE']._serialized_start=380
  _globals['_PROTOCOLVERSIONRESPONSE']._serialized_end=547
  _globals['_PROTOCOLVERSIONRESPONSE_RESULT']._serialized_start=509
  _globals['_PROTOCOLVERSIONRESPONSE_RESULT']._serialized_end=547
  _globals['_CONNECTIONRESPONSE']._serialized_start=549
  _globals['_CONNECTIONRESPONSE']._serialized_end=653
  _globals['_EVENT']._serialized_start=656
  _globals['_EVENT']._serialized_end=1753
  _globals['_FILTERLIST']._serialized_start=1755
  _globals['_FILTERLIST']._serialized_end=1781
  _globals['_EVENTREQUEST']._serialized_start=1784
  _globals['_EVENTREQUEST']._serialized_end=1966
  _globals['_EVENTRESPONSE']._serialized_start=1969
  _globals['_EVENTRESPONSE']._serialized_end=2108
  _globals['_USERAUTHENTICATIONREQUEST']._serialized_start=2110
  _globals['_USERAUTHENTICATIONREQUEST']._serialized_end=2183
  _globals['_USERAUTHENTICATIONRESPONSE']._serialized_start=2186
  _globals['_USERAUTHENTICATIONRESPONSE']._serialized_end=2426
  _globals['_USERAUTHENTICATIONRESPONSE_CODE']._serialized_start=2386
  _globals['_USERAUTHENTICATIONRESPONSE_CODE']._serialized_end=2426
# @@protoc_insertion_point(module_scope)
