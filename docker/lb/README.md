# nginx based Load Balancer for Avalon

This shows how to create nginx based Load Balancer to forward the requests
coming from clients to one of the many avalon-listeners running in backend.

## Running

1. Build and run Avalon components.
    ```bash
    docker-compose -f docker/lb/docker-compose-lb.yaml up --build

    The above command is going to start nginx based service (avalon-lb) along
    with other avalon services. The nginx load balancer configuration is
    defined in nginx.conf file which starts the nginx server on port 9947.
    The client is going to submit the transaction to avalon-lb Load Balancer
    and this load balancer is going to forward the  requests to 3 instances
    of avalon-listeners in the backend in round-robin fashion.
    ```

2. Start transaction from client.
    ```bash
    # Go to shell container
    docker exec -it avalon-shell bash
 
    # run the transaction
    cd examples/apps/generic_client
    ./generic_client.py --uri "http://avalon-lb:9947" --workload_id "echo-result" --in_data "Hello" --worker_id "singleton-worker-1"
     ```
