#!/usr/bin/env bash

here=$( dirname -- "$0" )

python3 -m grpc_tools.protoc \
    -I$here/session \
    --python_out=$here \
    --pyi_out=$here \
    --grpc_python_out=$here \
    $here/core.proto
