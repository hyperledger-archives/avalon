<!--
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
-->

# Hyperledger Avalon Python Workload for Graphene SGX

## Building and Running the Fibonacci python workload without Intel SGX

- To build Avalon Python worker run the following command from [python_worker](https://github.com/hyperledger/avalon/tree/master/tc/graphene/python_worker) directory:

  `docker-compose build`

  This will create docker image *avalon-python-worker-dev*. This image contains Avalon python worker, hello workload and a test application to send fibonacci work orders to python worker.

- To build Fibonacci python workload, run the following command from [fibonacci](https://github.com/hyperledger/avalon/tree/master/examples/graphene_apps/python_workloads/fibonacci) directory.
  `docker-compose build`

  This will create docker image *avalon-fibonacci-workload-dev*. This image contains Avalon python worker, fibonacci workload and a test application to send fibonacci work orders to python worker.

### Test Fibonacci python workload using Avalon

- To run fibonacci python workload with Avalon Graphene Enclave Manager, go to Avalon repository top level directory and execute the following command:

  `docker-compose -f docker-compose.yaml -f docker/compose/avalon-fib-graphene.yaml up`

- To send work orders to fibonacci workload running python worker we can use [generic client](https://github.com/hyperledger/avalon/tree/master/examples/apps/generic_client) application. Execute following commands:

  1. Get into Avalon Shell container : `sudo docker exec -it avalon-shell bash`

  2. `cd /project/avalon/examples/apps/generic_client/`

  3. Send work order request with *"python-fib"* workload id to fibonacci workload running in graphene worker *"graphene-worker-1"*

     `./generic_client.py --uri "http://avalon-listener:1947" -w "graphene-worker-1" --workload_id "python-fib" --in_data "10" -o`

     If everything goes fine, then you should see following output in stdout:

     *Decryption result at client - Fibonacci number at position 10 = 55*

## Building and Running Fibonacci workload in Graphene SGX

- Run the following command from Graphene git repository root directory:

  1. Copy the Graphene python worker GSC build script file *build_gsc_fibonacci_workload.sh* from [here](https://github.com/hyperledger/avalon/tree/master/examples/graphene_apps/python_workloads/fibonacci/graphene_sgx) to <graphene_repo>/Tools/gsc using following command :

     `cp <path of build_gsc_fibonacci_workload.sh> Tools/gsc`

  2. Set *TCF_HOME* to the top level directory of your avalon source repository.

     `export TCF_HOME=<path of avalon repo top level directory>`

  3. Graphenize Avalon python worker docker image using following command :

     `./build_gsc_fibonacci_workload.sh`

  Above command if run successfully will generate a Graphene based docker image *gsc-avalon-fibonacci-workload-dev*.

### Test Fibonacci workload using test client (without Avalon)

- To run fibonacci workload as a docker container in Graphene-SGX environment and to use a test application to send work order requests, execute the following command from [fibonacci](https://github.com/hyperledger/avalon/tree/master/examples/graphene_apps/python_workloads/fibonacci) directory.

  `docker-compose -f docker-compose.yaml -f compose/graphene-sgx.yaml up`

  Above command will run test work orders listed in file [*test_fib_work_orders.json*](http://github.com/hyperledger/avalon/tree/master/examples/graphene_apps/python_workloads/fibonacci/tests/test_fib_work_orders.json).

### Test Fibonacci workload using Avalon

- To run fibonacci workload in Graphene-SGX with Avalon Graphene Enclave Manager, go to Avalon repository  top level directory and execute the following commands :

  1. Start all the required containers in detached mode.

     `docker-compose -f docker-compose.yaml -f docker/compose/avalon-fib-graphene.yaml -f docker/compose/avalon-fib-gsgx.yaml up -d`

  2. Graphene-SGX Fibonacci workload service will take around 3 minutes to get ready. Check the logs of graphene python workload using below command

     `docker-compose -f docker-compose.yaml -f docker/compose/avalon-fib-graphene.yaml -f docker/compose/avalon-fib-gsgx.yaml logs -f graphene-python-workload`

     If everything goes fine you should see following log in stdout

     *graphene-python-workload   | Generate worker signing and encryption keys*
     *graphene-python-workload   | Start listening to ZMQ for work orders*
     *graphene-python-workload   | Bind to zmq port*
     *graphene-python-workload   | waiting for next request*

  3. To send work orders to fibonacci workload running in python worker we can use Avalon generic client application as shown [above](https://github.com/hyperledger/avalon/tree/master/examples/graphene_apps/python_workloads#test-python-worker-using-avalon).

  4. To restart the python worker you have to first bring all the containers down before bringing it up again. This is to ensure that python worker generate new keys and Avalon Graphene Enclave Manager gets the updated sign up information from python worker.

     `docker-compose -f docker-compose.yaml -f docker/compose/avalon-fib-graphene.yaml -f docker/compose/avalon-fib-gsgx.yaml down`
