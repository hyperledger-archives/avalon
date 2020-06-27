# Python code coverage for Hyperledger Avalon

This describes way to generate the python code coverage for 
[hyperledger/avalon](https://github.com/hyperledger/avalon)

1. Build Avalon components
   ```bash
   cd coverage
   docker-compose -f ../docker-compose.yaml -f coverage-direct-model.yaml build
   ```

2. Run Avalon services
   ```bash
   docker-compose -f ../docker-compose.yaml -f coverage-direct-model.yaml up
   ``` 

3. Run tests
   ```bash
   # Go to avalon-shell container
   docker exec -it avalon-shell bash
   
   You are allowed to run tests from avalon-shell container or any other way.
   ```

4. Generate avalon components specific .coverage files
   ```bash
   # Do not terminate the avalon containers and run the below shell script
   sudo ./coverage_gen.sh

   The above script will send SIGINT signal to the running process inside avalon components
   which will generate the .coverage file
   ```

5. Create avalon-coverage container to generate the coverage report in HTML format
   ```bash
   docker-compose -f generate-report.yaml up --build
   ```

6. After successfully running step 5 above, you would get the python code coverage report in report/ folder

   [Click here to see the sample python code coverage report](../images/sample-python-code-coverage-report.png)
