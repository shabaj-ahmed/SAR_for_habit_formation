# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: anki_vector/messaging/response_status.proto
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
    'anki_vector/messaging/response_status.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n+anki_vector/messaging/response_status.proto\x12\x1e\x41nki.Vector.external_interface\"\xe8\x01\n\x0eResponseStatus\x12G\n\x04\x63ode\x18\x01 \x01(\x0e\x32\x39.Anki.Vector.external_interface.ResponseStatus.StatusCode\"\x8c\x01\n\nStatusCode\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x15\n\x11RESPONSE_RECEIVED\x10\x01\x12\x16\n\x12REQUEST_PROCESSING\x10\x02\x12\x06\n\x02OK\x10\x03\x12\r\n\tFORBIDDEN\x10\x64\x12\r\n\tNOT_FOUND\x10\x65\x12\x1c\n\x18\x45RROR_UPDATE_IN_PROGRESS\x10\x66\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'anki_vector.messaging.response_status_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_RESPONSESTATUS']._serialized_start=80
  _globals['_RESPONSESTATUS']._serialized_end=312
  _globals['_RESPONSESTATUS_STATUSCODE']._serialized_start=172
  _globals['_RESPONSESTATUS_STATUSCODE']._serialized_end=312
# @@protoc_insertion_point(module_scope)
