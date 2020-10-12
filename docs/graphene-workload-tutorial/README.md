<!--
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
-->

# Writing a Python workload to run with Graphene SGX

## Creating the workload from template

For this tutorial let us consider a check for palindrome as the business logic for our workload.
Bring up the docker container from current directory with the name of your workload as an environment variable. For example -
```
WORKLOAD_NAME=palindrome docker-compose up
```
This will prepare your the setup for building your workload. Note that you just need to implement the business logic in `palindrome/src/palindrome.py`. You would find a function named `_palindrome()` here which should contain the core logic. You also need to update `palindrome/tests/test_work_orders.json` with strings to test in the `params` field.

The new directory `palindrome` created as a result of the docker command invoked above should be moved to `$TCF_HOME/examples/graphene_apps/python_workloads`. You are good to build and test your new workload now with or without Graphene.

The two docker compose files `avalon-workload-graphene.yaml` and `avalon-workload-gsgx.yaml` are meant to be used for running the workload with Avalon. We will see how to do this in the next section. For the time being, move these compose files alongside other compose files at `$TCF_HOME/docker/compose`.

## Build and run

First, you need to build the `avalon-python-worker-dev` image which is the base image for any workload image. To build the worker image, switch to `$TCF_HOME/tc/graphene/python_worker/` directory and run the docker compose command below -
```
docker-compose build
```

Now, you can build the workload image. Navigate back to `$TCF_HOME/examples/graphene_apps/python_workloads/palindrome` and run `docker-compose build` here.

### Running without Intel SGX

Run `docker-compose up` from `$TCF_HOME/examples/graphene_apps/python_workloads/palindrome`.

To run alongside Avalon, invoke the command below from Avalon's home directory (`$TCF_HOME`) -
```
docker-compose -f docker-compose.yaml -f docker/compose/avalon-graphene.yaml up
```

You could then test it by getting into the `avalon-shell` container and invoking the generic client. For example, run the generic client from `/project/avalon/examples/app/generic_client` as -
```
./generic_client.py --uri "http://avalon-listener:1947" -w "graphene-worker-1" --workload_id \
"python-palindrome" --in_data "God save Eva s dog" -o
```

### Running with Graphene SGX

To run workloads with Graphene SGX, you need to graphenize the exiting image to create a gsc(Graphene shielded container) image. Follow the instructions [here](https://github.com/hyperledger/avalon/blob/master/tc/graphene/python_worker/README.md#building-and-running-the-worker-in-graphene-sgx) to graphenize the workload image. The only difference here would be the script file which is `graphene_sgx/build_gsc_workload.sh`.

To run without Avalon, invoke the command - `docker-compose -f docker-compose.yaml -f compose/graphene-sgx.yaml up`

To run with Avalon, navigate to Avalon's home directory and invoke the command as below -
```
docker-compose -f docker-compose.yaml -f docker/compose/avalon-workload-graphene.yaml \
-f docker/compose/avalon-workload-gsgx.yaml up -d
```

This will take some time (1-2 minutes) to come up. Once up, you can get into the `avalon-shell` container and run the generic client as we did above.


