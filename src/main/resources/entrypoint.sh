#!/bin/sh
if [ ! -z $IEXEC_HTTP_PROXY_HOST ] && [ ! -z  $IEXEC_HTTP_PROXY_PORT ]; then
	java -Dhttp.proxyHost=$IEXEC_HTTP_PROXY_HOST -Dhttp.proxyPort=$IEXEC_HTTP_PROXY_PORT -jar /iexec-worker.jar
fi

java -jar /iexec-worker.jar