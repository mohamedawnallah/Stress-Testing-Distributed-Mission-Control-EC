# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: external_coordinator.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.api import annotations_pb2 as google_dot_api_dot_annotations__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1a\x65xternal_coordinator.proto\x12\x05\x65\x63rpc\x1a\x1cgoogle/api/annotations.proto\"B\n\x1dRegisterMissionControlRequest\x12!\n\x05pairs\x18\x01 \x03(\x0b\x32\x12.ecrpc.PairHistory\"9\n\x1eRegisterMissionControlResponse\x12\x17\n\x0fsuccess_message\x18\x01 \x01(\t\"&\n$QueryAggregatedMissionControlRequest\"J\n%QueryAggregatedMissionControlResponse\x12!\n\x05pairs\x18\x01 \x03(\x0b\x32\x12.ecrpc.PairHistory\"S\n\x0bPairHistory\x12\x11\n\tnode_from\x18\x01 \x01(\x0c\x12\x0f\n\x07node_to\x18\x02 \x01(\x0c\x12 \n\x07history\x18\x03 \x01(\x0b\x32\x0f.ecrpc.PairData\"\x93\x01\n\x08PairData\x12\x11\n\tfail_time\x18\x01 \x01(\x03\x12\x14\n\x0c\x66\x61il_amt_sat\x18\x02 \x01(\x03\x12\x15\n\rfail_amt_msat\x18\x03 \x01(\x03\x12\x14\n\x0csuccess_time\x18\x04 \x01(\x03\x12\x17\n\x0fsuccess_amt_sat\x18\x05 \x01(\x03\x12\x18\n\x10success_amt_msat\x18\x06 \x01(\x03\x32\xce\x02\n\x13\x45xternalCoordinator\x12\x8c\x01\n\x16RegisterMissionControl\x12$.ecrpc.RegisterMissionControlRequest\x1a%.ecrpc.RegisterMissionControlResponse\"%\x82\xd3\xe4\x93\x02\x1f\"\x1a/v1/registermissioncontrol:\x01*\x12\xa7\x01\n\x1dQueryAggregatedMissionControl\x12+.ecrpc.QueryAggregatedMissionControlRequest\x1a,.ecrpc.QueryAggregatedMissionControlResponse\")\x82\xd3\xe4\x93\x02#\x12!/v1/queryaggregatedmissioncontrol0\x01\x42\x41Z?github.com/ziggie1984/Distributed-Mission-Control-for-LND/ecrpcb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'external_coordinator_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'Z?github.com/ziggie1984/Distributed-Mission-Control-for-LND/ecrpc'
  _globals['_EXTERNALCOORDINATOR'].methods_by_name['RegisterMissionControl']._loaded_options = None
  _globals['_EXTERNALCOORDINATOR'].methods_by_name['RegisterMissionControl']._serialized_options = b'\202\323\344\223\002\037\"\032/v1/registermissioncontrol:\001*'
  _globals['_EXTERNALCOORDINATOR'].methods_by_name['QueryAggregatedMissionControl']._loaded_options = None
  _globals['_EXTERNALCOORDINATOR'].methods_by_name['QueryAggregatedMissionControl']._serialized_options = b'\202\323\344\223\002#\022!/v1/queryaggregatedmissioncontrol'
  _globals['_REGISTERMISSIONCONTROLREQUEST']._serialized_start=67
  _globals['_REGISTERMISSIONCONTROLREQUEST']._serialized_end=133
  _globals['_REGISTERMISSIONCONTROLRESPONSE']._serialized_start=135
  _globals['_REGISTERMISSIONCONTROLRESPONSE']._serialized_end=192
  _globals['_QUERYAGGREGATEDMISSIONCONTROLREQUEST']._serialized_start=194
  _globals['_QUERYAGGREGATEDMISSIONCONTROLREQUEST']._serialized_end=232
  _globals['_QUERYAGGREGATEDMISSIONCONTROLRESPONSE']._serialized_start=234
  _globals['_QUERYAGGREGATEDMISSIONCONTROLRESPONSE']._serialized_end=308
  _globals['_PAIRHISTORY']._serialized_start=310
  _globals['_PAIRHISTORY']._serialized_end=393
  _globals['_PAIRDATA']._serialized_start=396
  _globals['_PAIRDATA']._serialized_end=543
  _globals['_EXTERNALCOORDINATOR']._serialized_start=546
  _globals['_EXTERNALCOORDINATOR']._serialized_end=880
# @@protoc_insertion_point(module_scope)
