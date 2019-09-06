# Kubernetes playground for trusted-compute-framework 

This serves as a playground for developing 
[hyperledger-labs/trusted-compute-framework](https://github.com/hyperledger-labs/trusted-compute-framework)
in SGX-SIM mode.

## Prerequisites
- kubectl-v1.15.2
- a kubernetes cluster

## Running 

1. Start the LMDB server
    ```bash
    # bootstrap the deployment and service
    kubectl create -f lmdb.yaml
    ```
2. Start the `EnclaveManager` (to manage SGX enclaves) and `TCSServer` (to 
   accept and handle requests from clients)  
    ```bash
    kubectl create -f enclave-manager-deployment.yaml

    kubectl create -f tcs.yaml
    ```

## Propose a request
1. Send the request 
    ```bash
    kubectl create -f propose-requests-job.yaml
    ```

    > The above command would run the 
    > [propose_requests.sh](./scripts/propose_requests.sh) as a kubernetes job

2. Check the request handling logs (the request should be done in several 
   minutes after the proposal)
    ```bash
    # Let's say 'propose-request-abcde' is the job created above
    kubectl logs propose-request-abcde

    # The partial output for the last query should be go as below
    [23:20:36 INFO    __main__] Signature Verified
    [23:20:36 INFO    utility.utility] Decryption Result at Client - You have a risk of 71% to have heart disease. 
    ```

## Heads up
- The size of LMDB specified as 1TB in 
  [lmdb_store.cpp](../../tc/sgx/common/packages/db_store/lmdb_store.cpp) should 
  be decreased to something like accordingly for local development
- All the resources specified in yaml are using the images built by sammyne with
  name sammyne/hyperledger-tcf in docker hub