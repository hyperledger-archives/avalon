<!--
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
-->

# Writing a Python workload to run with Graphene SGX

## Changes to customize the template

For this tutorial let us consider a check for palindrome as the business logic for our workload.

### Sourcecode changes in template.py

- Rename `template.py` to something more meaningful for your workload. eg - palindrome.py
- Open palindrome.py and replace all occurrences as below -
    `<My_workload>` with Palindrome
    `<my_workload>` with palindrome
- Uncomment all code blocks in the function `_palindrome()`. This function holds the core business logic.

This completes the business logic implementation. Time to move on to setup next.

### Setup Changes

Update `workload.json` for the module and classname as updated while making changes in the sourcecode.
After changes the file should should contain -
```
{
    "python-palindrome": {
        "module": "src.palindrome",
        "class": "PalindromeWorkLoad"
    }
}
```

Here, "python-palindrome" is the workload-id that will be used for submitting work-orders. The other two fields are self-explanatory.

- Update the `tests/test_work_orders.json` file with workload-id as used in `workload.json`.

- Update `Dockerfile`, the image definition file for your workload. Replace `<my_workload>` with palindrome.

- Update image field as well in all the services in docker compose files `compose/graphene-sgx.yaml` and `docker-compose.yaml`.

- Now, put the same image name in `graphene_sgx/build_gsc_workload.sh`.

### Avalon specific changes

Update image name in the docker compose files `docker/compose/avalon-fib-graphene.yaml` and `docker/compose/avalon-fib-gsgx.yaml`. You could rename to these files to `docker/compose/avalon-pal-graphene.yaml` and `docker/compose/avalon-pal-gsgx.yaml` respectively as well.

Finally, create a directory named `palindrome` at `examples/graphene_apps/python_workloads`. Copy all the contents from the current directory to it. You are good to build and test your new workload now with or without Graphene.

## Build and run

First, you need to build the `avalon-python-worker-dev` image which is the base image for any workload image. To build the worker image, switch to `tc/graphene/python_worker/` directory and run the docker compose command below -
`docker-compose build`

Now, you can build the workload image. Navigate back to `examples/graphene_apps/python_workloads/palindrome` and run `docker-compose build` here.

### Running without Intel SGX

Run `docker-compose up`

To run alongside Avalon, invoke the command below from Avalon's home directory - 
`docker-compose -f docker-compose.yaml -f docker/compose/avalon-graphene.yaml up`

You could then test it by getting into the `avalon-shell` container and invoking the generic client. For example, run the generic client from `examples/app/generic_client` as -
```
./generic_client.py --uri "http://avalon-listener:1947" -w "graphene-worker-1" --workload_id "python-palindrome" --in_data "Hellolleh" -o
```

### Running with Graphene SGX

To run workloads with Graphene SGX, you need to graphenize the exiting image to create a gsc(Graphene shielded container) image. Follow the instructions [here](https://github.com/hyperledger/avalon/tree/master/examples/graphene_apps/python_worker#building-and-running-the-worker-in-graphene-sgx) to graphenize the workload image. The only difference here would be the script file which is `graphene_sgx/build_gsc_workload.sh`.

To run without Avalon, invoke the command - `docker-compose -f docker-compose.yaml -f compose/graphene-sgx.yaml up`

To run with Avalon, navigate to avalon home directory and invoke the command as below - 
`docker-compose -f docker-compose.yaml -f docker/compose/avalon-pal-graphene.yaml -f docker/compose/avalon-pal-gsgx.yaml up -d`

This will take some time(1-2 minutes) to come up. Once up, you can get into the `avalon-shell` container and run the generic client as we did above.

