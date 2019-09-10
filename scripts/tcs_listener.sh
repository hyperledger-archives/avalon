#!/bin/bash

listener="${TCF_HOME}/examples/common/python/connectors/direct/tcs_listener/tcs_listener.py"
# Read Listener port from config file
listener_port=`grep listener_port ${TCF_HOME}/config/tcs_config.toml | awk {'print $3'}`

# config in env variables takes higher priority
port=${TCF_TCS_LISTENER_PORT:-${listener_port}}

source ${TCF_HOME}/tools/build/_dev/bin/activate

echo "starting TCS listener ..."
python3 $listener --bind_uri ${port}
