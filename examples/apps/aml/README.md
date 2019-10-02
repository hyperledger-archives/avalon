The aml example is composed by 3 different parts.
1. standalone-cipher: This is an example of a standalone cipher that is proposed as a possible solution. This tool has several functionalities.
	- It allows you to create a well formatted JSONs that you can send to the platform just by inputing the CSVs with the information about both the users and the transactions.
	- It also allows you to encrypt the JSONs in a manner totally independent from the platform just by feeding the workerInfo of the worker that you are targeting to process your work orders.

2. web-client: This is a example of a proposed view for the aml application with the following functionalities:
	- retrieve the list of available workers and display their information.
	- download the workerInfo of a concrete worker.
	- send already encrypted JSONs to be processed by the server side.
	- retrieve the result of a work order and update the state of the algorithm.

3. workload: Contains the logic used for this aml use case. The algorithm consist on a simplified version of Anti Money Laundering, it searches for money going round in circles and outputs the list of people suspicious of doing so.