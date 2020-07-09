# Kubernetes playground for Avalon Fabric proxy model

This serves as a playground to setup k8s cluster for Avalon Fabric proxy model.

## Prerequisites
- To setup the k8s cluster using minikube, refer to Prerequisites section in [README.md](../README.md) under docker/k8s folder
- This setup is going to work with the assumption that the Fabric network with minifab, Avalon blockchain connector pod
  and Avalon shell pod are running in the same machine.
- Build docker images by running the below command
  `docker-compose -f docker-compose.yaml -f docker/compose/avalon-fabric.yaml build`
- To use Intel SGX HW mode, build avalon-sgx-enclave-manager-dev docker image using below command
  `docker-compose -f docker-compose.yaml -f docker-compose-sgx.yaml build avalon-enclave-manager`
- Start fabric network.
  ```bash
   # Go to avalon root directory and run the below command
   ./scripts/start_fabric.sh -u
  ```

## Running 

1. Start Shared KV database service.
    ```bash
    # bootstrap the deployment and service
    kubectl create -f ../lmdb.yaml
    ```
2. Start `EnclaveManager` (to manage Intel SGX enclaves)
   For Intel SGX simulator mode, use the below command
    ```bash
    kubectl create -f enclave-manager-deployment.yaml
    ```
   For Intel SGX hardware mode, use the below command
    ```bash
    kubectl create -f sgx-enclave-manager-deployment.yaml
    ```
3.  Start `http jrpc Listener service` (to accept and handle http jrpc requests from clients)
    ```bash
    kubectl create -f ../listener.yaml
    ```
4.  Start `blockchain connector` service
    ```bash
    kubectl create -f fabric/blockchain-connector.yaml
    ```
5.  Avalon shell pod can be useful to run applications manually.
    ```bash
    kubectl create -f fabric/shell.yaml
    ```

## Workload request to be executed
1. Before sending a workload request check if sharedkv, enclave manager, listener, blockchain connector and shell pods are running
    ```bash
    kubectl get pods
    ```

2. After verifying all Pods are running, get a shell to the shell running Pod
    ```bash
    # Get the Avalon shell pod name using command
    kubectl get pods
    # Let's say 'avalon-shell-abcde' is the pod created above. Get into the shell
    kubectl exec -it avalon-shell-abcde -- /bin/bash
    ```
3. To execute a transaction from shell
   ```bash
   cd examples/apps/generic_client
   ./generic_client.py -b fabric --workload_id "echo-result" --in_data "Hello" \
       --worker_id "singleton-worker-1"
   ```

   NOTE: `worker_id` should match with worker id of singleton enclave manager.  
   This worker_id can either be command line argument passed to enclave manager or   
   in the absence of command line argument, worker_id in
   `$TCF_HOME/config/singleton_enclave_config.toml` should be used.

# Heads up
- All the resources specified in yaml are using the images built locally.
