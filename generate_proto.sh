#!/usr/bin/env bash

here=$( dirname -- "$0" )

python3 -m grpc_tools.protoc \
    -I$here/proto \
    --python_out=$here/client/proto \
    --pyi_out=$here/client/proto \
    --grpc_python_out=$here/client/proto \
    $here/proto/core.proto

python3 -m grpc_tools.protoc \
    -I$here/proto \
    --python_out=$here/server/proto \
    --pyi_out=$here/server/proto \
    --grpc_python_out=$here/server/proto \
    $here/proto/core.proto
