<!--
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
-->

# eea-worker

### Overview

The EEA Worker is a light Java worker client compliant with the
[EEA Off-Chain Trusted Compute Specification v1](https://entethalliance.org/wp-content/uploads/2019/05/EEA_Off_Chain_Trusted_Compute_Specification_V1_0.pdf).


### Run an eea-worker


#### With Gradle

*Please first update your config located in `./src/main/resources/application.yml`*

* for dev purposes:

```bash
cd eea-worker
gradle bootRun --refresh-dependencies
```
* or on a remote instance:
```bash
cd eea-worker
./gradlew bootRun --refresh-dependencies
```
