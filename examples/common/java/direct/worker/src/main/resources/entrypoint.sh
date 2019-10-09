#!/bin/sh

################################################################################
#  Copyright 2019 iExec Blockchain Tech
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
################################################################################

if [ ! -z $EEA_HTTP_PROXY_HOST ] && [ ! -z  $EEA_HTTP_PROXY_PORT ]; then
	java -Dhttp.proxyHost=$EEA_HTTP_PROXY_HOST -Dhttp.proxyPort=$EEA_HTTP_PROXY_PORT -jar /eea-worker.jar
fi

java -jar /eea-worker.jar
