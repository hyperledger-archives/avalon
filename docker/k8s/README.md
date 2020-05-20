<!--
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
-->

# Kubernetes playground for Hyperledger Avalon

This serves as a playground for developing
[hyperledger/avalon](https://github.com/hyperledger/avalon)
in SGX-SIM and SGX-HW mode.

## Prerequisites
- kubectl-v1.15.2
- A Kubernetes cluster.
  [Minikube] (https://kubernetes.io/docs/setup/learning-environment/minikube/)
  can be used to setup a single node Kubernetes cluster.
- To enable Intel SGX HW mode, follow the instructions in
  [PREREQUISITES.md](../../PREREQUISITES.md#intel-sgx-in-hardware-mode)
- To use Intel SGX HW mode, build docker image using below command
  `docker-compose -f docker-compose-sgx.yaml build`

## Running Avalon with Kubernetes

1. Start Shared KV database service.
    ```bash
    # bootstrap the deployment and service
    kubectl create -f lmdb.yaml
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
3.  Start `http jrpc Listener service`
    (to accept and handle http jrpc requests from clients)
    ```bash
    kubectl create -f listener.yaml
    ```

## Propose a workload request to be executed
1. Before sending a workload request check if sharedkv, enclave manager and
   listener pods are running
    ```bash
    kubectl get pods
    ```

2. Send the request 
    ```bash
    kubectl create -f propose-requests-job.yaml
    ```

    > The above command would run the 
    > [propose_requests.sh](propose_requests.sh) as a Kubernetes job

3. Check the request handling logs (the request should be done in several 
   minutes after the proposal)
    ```bash
    # Get the workload request pod name using command
    kubectl get pods
    # Let's say 'propose-request-abcde' is the job pod created above.
    # Check the logs
    kubectl logs propose-request-abcde

    # The partial output for the last query should be as follows
    [23:20:36 INFO __main__] Signature Verified
    [23:20:36 INFO utility.utility] Decryption Result at Client - You have a 47% risk of heart disease.
    ```

## Create Avalon shell pod
1. Avalon shell pod can be useful to run applications manually.
    ```bash
    kubectl create -f shell.yaml
    ```
2. After verifying avalon shell pod is running,
   get a shell to the running container
    ```bash
    # Get the Avalon shell pod name using command
    kubectl get pods
    # Let's say 'avalon-shell-abcde' is the pod created above.
    # Get into the shell
    kubectl exec -it avalon-shell-abcde -- /bin/bash
    ```
3. To execute test cases from shell, refer to testing section in
   [BUILD.md](../../BUILD.md#testing)

# Heads up
- All the resources specified in yaml are using the images built locally.
