# eea-worker

### Overview

The EEA-Worker is a lite iexec-worker compliant with the EEA specification


### Run an eea-worker


#### With Gradle

*Please first update your config located in `./src/main/resources/application.yml`*

* for dev purposes:

```
cd eea-worker
gradle bootRun --refresh-dependencies
```
* or on a remote instance:
```
cd eea-worker
./gradlew bootRun --refresh-dependencies
```

