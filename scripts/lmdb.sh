#!/bin/bash

lmdb_server="${TCF_HOME}/examples/common/python/shared_kv/remote_lmdb/lmdb_listener.py"

source ${TCF_HOME}/tools/build/_dev/bin/activate

echo "start the lmdb server ..."

python3 ${lmdb_server}
