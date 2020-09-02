# nginx based Load Balancer for Avalon

This shows how to create nginx based Load Balancer to forward the requests
coming from clients to one of the many avalon-listeners running in backend.

## Running

1. Build and run Avalon components.
    ```bash
    docker-compose -f docker-compose.yaml -f docker/lb/docker-compose-listeners.yaml -f docker/lb/docker-compose-lb-nginx.yaml up --build

    The above command is going to start nginx based service (avalon-lb-nginx) along
    with other Avalon services. The nginx load balancer configuration is
    defined in nginx.conf file which starts the nginx server on port 9947.
    The client is going to submit the transaction to avalon-lb Load Balancer
    and this load balancer is going to forward the  requests to 4 instances
    of avalon-listeners in the backend in round-robin fashion.
    ```

2. Start transaction from client.
    ```bash
    # Go to shell container
    docker exec -it avalon-shell bash
 
    # run the transaction
    cd examples/apps/generic_client
    ./generic_client.py --uri "http://avalon-lb-nginx:9947" --workload_id "echo-result" --in_data "Hello" --worker_id "singleton-worker-1"
     ```


# HAProxy based Load Balancer for Avalon

This shows how to create HAProxy based Load Balancer to forward the requests
coming from clients to one of the many avalon-listeners running in backend.

## Running

1. Build and run Avalon components.
    ```bash
    docker-compose -f docker-compose.yaml -f docker/lb/docker-compose-listeners.yaml -f docker/lb/docker-compose-lb-haproxy.yaml up --build

    The above command is going to start HAProxy based service (avalon-lb-haproxy) along
    with other Avalon services. The HAProxy load balancer configuration is
    defined in haproxy.cfg file which starts the haproxy server on port 9947.
    The client is going to submit the transaction to avalon-lb Load Balancer
    and this load balancer is going to forward the  requests to 4 instances
    of avalon-listeners in the backend in round-robin fashion.
    ```

2. Start transaction from client.
    ```bash
    # Go to shell container
    docker exec -it avalon-shell bash

    # run the transaction
    cd examples/apps/generic_client
    ./generic_client.py --uri "http://avalon-lb-haproxy:9947" --workload_id "echo-result" --in_data "Hello" --worker_id "singleton-worker-1"
    ```
