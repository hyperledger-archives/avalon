# Kubernetes playground for Avalon 

This serves as a playground for developing 
[hyperledger/avalon](https://github.com/hyperledger/avalon)
in SGX-SIM and SGX-HW mode.

## Prerequisites
- kubectl-v1.15.2
- a kubernetes cluster
- To enable SGX HW, follow the instructions in
  [PREREQUISITES.md](../../PREREQUISITES.md#intel-sgx-in-hardware-mode)
- To use SGX HW, build docker image using below command  
  `docker-compose -f docker-compose-sgx.yaml build`

## Running 

1. Start Shared KV database service.
    ```bash
    # bootstrap the deployment and service
    kubectl create -f lmdb.yaml
    ```
2. Start `EnclaveManager` (to manage SGX enclaves)  
   For SGX simulator mode, use the below command
    ```bash
    kubectl create -f enclave-manager-deployment.yaml
    ```
   For SGX hardware mode, use the below command
    ```bash
    kubectl create -f sgx-enclave-manager-deployment.yaml
    ```
3.  Start `http jrpc Listener service` (to accept and handle http jrpc requests from clients)
    ```bash
    kubectl create -f listener.yaml
    ```

## Propose a workload request to be executed
1. Before sending a workload request check if sharedkv, enclave manager and listener pods are running
    ```bash
    kubectl get pods
    ```

2. Send the request 
    ```bash
    kubectl create -f propose-requests-job.yaml
    ```

    > The above command would run the 
    > [propose_requests.sh](./scripts/propose_requests.sh) as a kubernetes job

3. Check the request handling logs (the request should be done in several 
   minutes after the proposal)
    ```bash
    # Let's say 'propose-request-abcde' is the job created above
    kubectl logs propose-request-abcde

    # The partial output for the last query should be go as below
    [23:20:36 INFO    __main__] Signature Verified
    [23:20:36 INFO    utility.utility] Decryption Result at Client - You have a risk of 71% to have heart disease. 
    ```

## Create Avalon shell pod
1. Avalon shell pod can be useful to run applications manually.
    ```bash
    kubectl create -f shell.yaml
    ```
2. After verifying avalon shell pod is running get a shell to the running container
    ```bash
    # Let's say 'avalon-shell-abcde' is the pod created above
    kubectl exec -it avalon-shell-abcde -- /bin/bash
    ```
3. To execute test cases from shell, refer to testing section in [BUILD.md](../../BUILD.md#testing)

# Heads up
- All the resources specified in yaml are using the images built locally.
