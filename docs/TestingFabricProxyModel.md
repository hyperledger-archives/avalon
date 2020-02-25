**Testing Avalon Proxy model with Hyperledger Fabric**
1.  Install curl, docker and docker-compse
2.  Set the environment variable TCF_HOME to Avalon root directory
3.  Start the fabric network with 2 organizations, 4 peers and 3 orderers using start_fabric.sh script.
    *cd $TCF_HOME*
    *./scripts/start_fabric.sh*
Starting fabric docker conainers will take some time, once it is up and running check for fabric containers with name with peer-*, orderer-*, dev-*
4.  Start the avalon containers
    *docker-compose -f docker-compose-fabric.yaml up --build*
*Once fabric containers are up and running we can start and stop Avalon containers any number of time without restarting fabric containers.
5.  Go to tcf container to run generic_client
    *docker exec -it tcf bash*
    *cd examples/apps/generic_client/*
    *./fabric_generic_client.py -b fabric --workload_id "echo-result" --in_data "Hello"*

