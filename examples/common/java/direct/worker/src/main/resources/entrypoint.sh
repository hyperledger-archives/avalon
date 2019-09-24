#!/bin/sh
if [ ! -z $EEA_HTTP_PROXY_HOST ] && [ ! -z  $EEA_HTTP_PROXY_PORT ]; then
	java -Dhttp.proxyHost=$EEA_HTTP_PROXY_HOST -Dhttp.proxyPort=$EEA_HTTP_PROXY_PORT -jar /eea-worker.jar
fi

java -jar /eea-worker.jar