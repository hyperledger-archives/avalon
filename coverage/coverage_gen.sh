#!/bin/bash

lines=$(ps -ef | grep /usr/local/bin/coverage | wc -l)
echo $lines

# To generate .coverage file, SIGINT signal needs to send to services
# processes running inside avalon containers.
while [ $lines -ne 1 ]
do
        PID=$(ps -ef | grep /usr/local/bin/coverage | awk 'NR==1{print $2}')
        echo $PID
        $(kill -s SIGINT $PID)
	lines=$(ps -ef | grep /usr/local/bin/coverage | wc -l)
done
