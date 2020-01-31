# Automation test framework 

This is a test framework client intended to execute automated tests. 
The intention is to run tests in direct/ proxy invocation models. 
This is to validate the response of worker, work order and work 
order receipts APIs as per Enterprise Ethereum Alliance Off-Chain 
Trusted Compute Specification v1.1.

Steps to execute automation test framework

1. Build Avalon: Docker-based build (recommended)
	docker-compose up --build
2. Open a Docker container shell using following command 
	docker exec -it tcf bash
3. Run automation
	cd $TCF_HOME/tests/validation_suite
	pytest (All tests)
	pytest work_order_tests/test_work_order_success.py (single test)
