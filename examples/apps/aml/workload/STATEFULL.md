
## Changes to make tcf statefull
1. First we needed to modify *work_order_processor.cpp* and *work_order_processor.h* inside the folder *tc/sgx/trusted_worker_manager/enclave/*. On them we have added a new variable "keepState" that will is parsed from the workOrder json and indicates if we want to keep the WorkloadProcessor that was used on the last execution or we want to create a new one with the state starting from scratch.
2. Next we have modified the files *workload_processor.cpp* and *workload_processor.h* in folder *common/sgx_workload/*.
	- We have added 2 new parameters to the function *CreateWorkloadProcessor* (*worker_id* and the newly created *keepState*).
	- In the cpp file we have added new map called *initialized_processors*. This map will be used to store the state of the already initialized WorkloadProcessors between 2 different workOrders. The key key for that map would be the following one:
		```
		workload_tag = worker_id + "_" + workload_id;
		```
	- This new map changes a bit the algorithm, now the first thing it does is checking inside *initialized_processors* if there's a WorkloadProcessor initialized for the actual *workload_tag*. If so and *keepState* value is "true" the function will return the already initialized *WorkloadProcessor*. On the other hand if any of them is false the algorithm will work as in previous versions creating a new copy from scratch of the expected *WorkloadProcessor*
 ```
